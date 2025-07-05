import json
import sqlite3
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Any, Optional
from pathlib import Path
import calendar
from dataclasses import dataclass, asdict
import threading
import time

@dataclass
class Task:
    """Task data structure"""
    id: Optional[int] = None
    title: str = ""
    description: str = ""
    status: str = "pending"  # pending, in_progress, completed, cancelled
    priority: int = 1  # 1-5 scale
    due_date: Optional[datetime] = None
    created_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    category: str = "general"
    tags: List[str] = None
    estimated_duration: Optional[int] = None  # minutes
    actual_duration: Optional[int] = None  # minutes

@dataclass
class Event:
    """Calendar event data structure"""
    id: Optional[int] = None
    title: str = ""
    description: str = ""
    start_time: datetime = None
    end_time: datetime = None
    location: str = ""
    attendees: List[str] = None
    reminder_minutes: int = 15
    category: str = "meeting"
    recurring: bool = False
    recurrence_pattern: str = ""  # daily, weekly, monthly, yearly

@dataclass
class Reminder:
    """Reminder data structure"""
    id: Optional[int] = None
    title: str = ""
    message: str = ""
    reminder_time: datetime = None
    repeat_interval: Optional[int] = None  # minutes
    is_active: bool = True
    created_at: Optional[datetime] = None

class TaskManager:
    """Manages tasks, calendar events, and reminders"""
    
    def __init__(self, db_path: str = "memory/task_manager.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.init_database()
        self.reminder_thread = None
        self.is_monitoring = False
        self.reminder_callbacks = []
    
    def init_database(self):
        """Initialize the task management database"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Tasks table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS tasks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    description TEXT,
                    status TEXT DEFAULT 'pending',
                    priority INTEGER DEFAULT 1,
                    due_date DATETIME,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    completed_at DATETIME,
                    category TEXT DEFAULT 'general',
                    tags TEXT,
                    estimated_duration INTEGER,
                    actual_duration INTEGER
                )
            ''')
            
            # Events table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    description TEXT,
                    start_time DATETIME NOT NULL,
                    end_time DATETIME NOT NULL,
                    location TEXT,
                    attendees TEXT,
                    reminder_minutes INTEGER DEFAULT 15,
                    category TEXT DEFAULT 'meeting',
                    recurring BOOLEAN DEFAULT FALSE,
                    recurrence_pattern TEXT
                )
            ''')
            
            # Reminders table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS reminders (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    message TEXT,
                    reminder_time DATETIME NOT NULL,
                    repeat_interval INTEGER,
                    is_active BOOLEAN DEFAULT TRUE,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            conn.commit()
    
    def add_task(self, task: Task) -> int:
        """Add a new task"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            tags_json = json.dumps(task.tags) if task.tags else None
            
            cursor.execute('''
                INSERT INTO tasks 
                (title, description, status, priority, due_date, category, tags, estimated_duration)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                task.title, task.description, task.status, task.priority,
                task.due_date, task.category, tags_json, task.estimated_duration
            ))
            
            task_id = cursor.lastrowid
            conn.commit()
            
            return task_id
    
    def get_tasks(self, status: str = None, category: str = None, 
                  limit: int = 50, sort_by: str = "due_date") -> List[Task]:
        """Get tasks with optional filtering"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            query = "SELECT * FROM tasks WHERE 1=1"
            params = []
            
            if status:
                query += " AND status = ?"
                params.append(status)
            
            if category:
                query += " AND category = ?"
                params.append(category)
            
            query += f" ORDER BY {sort_by} ASC LIMIT ?"
            params.append(limit)
            
            cursor.execute(query, params)
            results = cursor.fetchall()
            
            tasks = []
            columns = [desc[0] for desc in cursor.description]
            
            for row in results:
                task_dict = dict(zip(columns, row))
                
                # Parse dates
                if task_dict['due_date']:
                    task_dict['due_date'] = datetime.fromisoformat(task_dict['due_date'])
                if task_dict['created_at']:
                    task_dict['created_at'] = datetime.fromisoformat(task_dict['created_at'])
                if task_dict['completed_at']:
                    task_dict['completed_at'] = datetime.fromisoformat(task_dict['completed_at'])
                
                # Parse tags
                if task_dict['tags']:
                    task_dict['tags'] = json.loads(task_dict['tags'])
                
                tasks.append(Task(**task_dict))
            
            return tasks
    
    def update_task(self, task_id: int, **updates) -> bool:
        """Update a task"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Build update query dynamically
            set_clauses = []
            params = []
            
            for field, value in updates.items():
                if field in ['title', 'description', 'status', 'priority', 'due_date', 
                           'category', 'estimated_duration', 'actual_duration']:
                    set_clauses.append(f"{field} = ?")
                    params.append(value)
                elif field == 'tags':
                    set_clauses.append("tags = ?")
                    params.append(json.dumps(value) if value else None)
            
            if not set_clauses:
                return False
            
            query = f"UPDATE tasks SET {', '.join(set_clauses)} WHERE id = ?"
            params.append(task_id)
            
            cursor.execute(query, params)
            success = cursor.rowcount > 0
            conn.commit()
            
            return success
    
    def complete_task(self, task_id: int) -> bool:
        """Mark a task as completed"""
        return self.update_task(task_id, status='completed', completed_at=datetime.now())
    
    def delete_task(self, task_id: int) -> bool:
        """Delete a task"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
            success = cursor.rowcount > 0
            conn.commit()
            return success
    
    def add_event(self, event: Event) -> int:
        """Add a calendar event"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            attendees_json = json.dumps(event.attendees) if event.attendees else None
            
            cursor.execute('''
                INSERT INTO events 
                (title, description, start_time, end_time, location, attendees, 
                 reminder_minutes, category, recurring, recurrence_pattern)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                event.title, event.description, event.start_time, event.end_time,
                event.location, attendees_json, event.reminder_minutes,
                event.category, event.recurring, event.recurrence_pattern
            ))
            
            event_id = cursor.lastrowid
            conn.commit()
            
            return event_id
    
    def get_events(self, start_date: datetime = None, end_date: datetime = None,
                   category: str = None, limit: int = 50) -> List[Event]:
        """Get calendar events with optional date range filtering"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            query = "SELECT * FROM events WHERE 1=1"
            params = []
            
            if start_date:
                query += " AND start_time >= ?"
                params.append(start_date)
            
            if end_date:
                query += " AND end_time <= ?"
                params.append(end_date)
            
            if category:
                query += " AND category = ?"
                params.append(category)
            
            query += " ORDER BY start_time ASC LIMIT ?"
            params.append(limit)
            
            cursor.execute(query, params)
            results = cursor.fetchall()
            
            events = []
            columns = [desc[0] for desc in cursor.description]
            
            for row in results:
                event_dict = dict(zip(columns, row))
                
                # Parse dates
                if event_dict['start_time']:
                    event_dict['start_time'] = datetime.fromisoformat(event_dict['start_time'])
                if event_dict['end_time']:
                    event_dict['end_time'] = datetime.fromisoformat(event_dict['end_time'])
                
                # Parse attendees
                if event_dict['attendees']:
                    event_dict['attendees'] = json.loads(event_dict['attendees'])
                
                events.append(Event(**event_dict))
            
            return events
    
    def get_today_events(self) -> List[Event]:
        """Get today's events"""
        today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        tomorrow = today + timedelta(days=1)
        return self.get_events(start_date=today, end_date=tomorrow)
    
    def get_upcoming_events(self, days: int = 7) -> List[Event]:
        """Get upcoming events for next N days"""
        start_date = datetime.now()
        end_date = start_date + timedelta(days=days)
        return self.get_events(start_date=start_date, end_date=end_date)
    
    def add_reminder(self, reminder: Reminder) -> int:
        """Add a reminder"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO reminders 
                (title, message, reminder_time, repeat_interval, is_active)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                reminder.title, reminder.message, reminder.reminder_time,
                reminder.repeat_interval, reminder.is_active
            ))
            
            reminder_id = cursor.lastrowid
            conn.commit()
            
            return reminder_id
    
    def get_due_reminders(self) -> List[Reminder]:
        """Get reminders that are due now"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            current_time = datetime.now()
            cursor.execute('''
                SELECT * FROM reminders 
                WHERE is_active = TRUE AND reminder_time <= ?
                ORDER BY reminder_time ASC
            ''', (current_time,))
            
            results = cursor.fetchall()
            columns = [desc[0] for desc in cursor.description]
            
            reminders = []
            for row in results:
                reminder_dict = dict(zip(columns, row))
                
                if reminder_dict['reminder_time']:
                    reminder_dict['reminder_time'] = datetime.fromisoformat(reminder_dict['reminder_time'])
                if reminder_dict['created_at']:
                    reminder_dict['created_at'] = datetime.fromisoformat(reminder_dict['created_at'])
                
                reminders.append(Reminder(**reminder_dict))
            
            return reminders
    
    def start_reminder_monitoring(self, callback_func=None):
        """Start monitoring for due reminders"""
        if self.is_monitoring:
            return
        
        self.is_monitoring = True
        if callback_func:
            self.reminder_callbacks.append(callback_func)
        
        self.reminder_thread = threading.Thread(target=self._monitor_reminders, daemon=True)
        self.reminder_thread.start()
    
    def stop_reminder_monitoring(self):
        """Stop reminder monitoring"""
        self.is_monitoring = False
        if self.reminder_thread:
            self.reminder_thread.join(timeout=2.0)
    
    def _monitor_reminders(self):
        """Monitor and trigger due reminders"""
        while self.is_monitoring:
            try:
                due_reminders = self.get_due_reminders()
                
                for reminder in due_reminders:
                    # Trigger callbacks
                    for callback in self.reminder_callbacks:
                        try:
                            callback(reminder)
                        except Exception as e:
                            print(f"Reminder callback error: {e}")
                    
                    # Handle repeating reminders
                    if reminder.repeat_interval:
                        next_time = reminder.reminder_time + timedelta(minutes=reminder.repeat_interval)
                        self.update_reminder(reminder.id, reminder_time=next_time)
                    else:
                        # Deactivate one-time reminders
                        self.update_reminder(reminder.id, is_active=False)
                
                time.sleep(60)  # Check every minute
                
            except Exception as e:
                print(f"Reminder monitoring error: {e}")
                time.sleep(60)
    
    def update_reminder(self, reminder_id: int, **updates) -> bool:
        """Update a reminder"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            set_clauses = []
            params = []
            
            for field, value in updates.items():
                if field in ['title', 'message', 'reminder_time', 'repeat_interval', 'is_active']:
                    set_clauses.append(f"{field} = ?")
                    params.append(value)
            
            if not set_clauses:
                return False
            
            query = f"UPDATE reminders SET {', '.join(set_clauses)} WHERE id = ?"
            params.append(reminder_id)
            
            cursor.execute(query, params)
            success = cursor.rowcount > 0
            conn.commit()
            
            return success
    
    def get_productivity_stats(self, days: int = 7) -> Dict[str, Any]:
        """Get productivity statistics"""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Completed tasks
            cursor.execute('''
                SELECT COUNT(*), AVG(actual_duration), category
                FROM tasks 
                WHERE completed_at BETWEEN ? AND ? AND status = 'completed'
                GROUP BY category
            ''', (start_date, end_date))
            
            completed_tasks = cursor.fetchall()
            
            # Pending tasks
            cursor.execute('''
                SELECT COUNT(*) FROM tasks 
                WHERE status = 'pending' AND due_date < ?
            ''', (end_date,))
            
            overdue_tasks = cursor.fetchone()[0]
            
            # Total tasks
            cursor.execute('SELECT COUNT(*) FROM tasks WHERE created_at BETWEEN ? AND ?', 
                         (start_date, end_date))
            total_tasks = cursor.fetchone()[0]
            
            return {
                'period_days': days,
                'total_tasks_created': total_tasks,
                'completed_tasks_by_category': completed_tasks,
                'overdue_tasks': overdue_tasks,
                'completion_rate': len(completed_tasks) / total_tasks if total_tasks > 0 else 0
            }
    
    def suggest_schedule_optimization(self) -> List[str]:
        """Suggest schedule optimizations based on patterns"""
        suggestions = []
        
        # Get upcoming tasks and events
        upcoming_tasks = self.get_tasks(status='pending', limit=20)
        upcoming_events = self.get_upcoming_events(days=7)
        
        # Check for overdue tasks
        overdue_tasks = [t for t in upcoming_tasks if t.due_date and t.due_date < datetime.now()]
        if overdue_tasks:
            suggestions.append(f"You have {len(overdue_tasks)} overdue tasks. Consider rescheduling or completing them.")
        
        # Check for time conflicts
        today_events = self.get_today_events()
        if len(today_events) > 5:
            suggestions.append("Your schedule is quite busy today. Consider rescheduling non-critical meetings.")
        
        # Check for tasks without due dates
        no_due_date = [t for t in upcoming_tasks if not t.due_date]
        if no_due_date:
            suggestions.append(f"{len(no_due_date)} tasks don't have due dates. Consider setting deadlines to improve prioritization.")
        
        return suggestions