import json
import sqlite3
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from pathlib import Path
import hashlib

class MemoryManager:
    """Manages persistent memory, context, and session recall for the AI assistant"""
    
    def __init__(self, db_path: str = "memory/assistant_memory.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.init_database()
        self.current_session_id = self._generate_session_id()
        self.context_buffer = []
        self.max_context_length = 50  # Maximum number of exchanges to keep in context
    
    def init_database(self):
        """Initialize the memory database"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Conversations table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS conversations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT NOT NULL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    user_input TEXT NOT NULL,
                    assistant_response TEXT NOT NULL,
                    context_tags TEXT,
                    importance_score INTEGER DEFAULT 1
                )
            ''')
            
            # User preferences table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS user_preferences (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Facts and knowledge base
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS knowledge_base (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    topic TEXT NOT NULL,
                    fact TEXT NOT NULL,
                    source TEXT,
                    confidence_score REAL DEFAULT 1.0,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Tasks and reminders
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS tasks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    description TEXT,
                    status TEXT DEFAULT 'pending',
                    priority INTEGER DEFAULT 1,
                    due_date DATETIME,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    completed_at DATETIME
                )
            ''')
            
            # Session metadata
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS sessions (
                    session_id TEXT PRIMARY KEY,
                    start_time DATETIME DEFAULT CURRENT_TIMESTAMP,
                    end_time DATETIME,
                    interaction_count INTEGER DEFAULT 0,
                    session_summary TEXT
                )
            ''')
            
            conn.commit()
    
    def save_conversation(self, user_input: str, assistant_response: str, 
                         context_tags: List[str] = None, importance: int = 1):
        """Save a conversation exchange to memory"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            tags_json = json.dumps(context_tags) if context_tags else None
            
            cursor.execute('''
                INSERT INTO conversations 
                (session_id, user_input, assistant_response, context_tags, importance_score)
                VALUES (?, ?, ?, ?, ?)
            ''', (self.current_session_id, user_input, assistant_response, tags_json, importance))
            
            # Update session interaction count
            cursor.execute('''
                INSERT OR REPLACE INTO sessions (session_id, interaction_count)
                VALUES (?, COALESCE((SELECT interaction_count FROM sessions WHERE session_id = ?), 0) + 1)
            ''', (self.current_session_id, self.current_session_id))
            
            conn.commit()
        
        # Add to context buffer
        self.context_buffer.append({
            'user_input': user_input,
            'assistant_response': assistant_response,
            'timestamp': datetime.now().isoformat(),
            'tags': context_tags
        })
        
        # Trim context buffer if too long
        if len(self.context_buffer) > self.max_context_length:
            self.context_buffer = self.context_buffer[-self.max_context_length:]
    
    def get_conversation_history(self, limit: int = 20, session_id: str = None) -> List[Dict[str, Any]]:
        """Retrieve recent conversation history"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            if session_id:
                cursor.execute('''
                    SELECT user_input, assistant_response, timestamp, context_tags
                    FROM conversations
                    WHERE session_id = ?
                    ORDER BY timestamp DESC
                    LIMIT ?
                ''', (session_id, limit))
            else:
                cursor.execute('''
                    SELECT user_input, assistant_response, timestamp, context_tags
                    FROM conversations
                    ORDER BY timestamp DESC
                    LIMIT ?
                ''', (limit,))
            
            results = cursor.fetchall()
            
            conversations = []
            for row in results:
                conversations.append({
                    'user_input': row[0],
                    'assistant_response': row[1],
                    'timestamp': row[2],
                    'context_tags': json.loads(row[3]) if row[3] else []
                })
            
            return list(reversed(conversations))  # Return in chronological order
    
    def search_conversations(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Search through conversation history"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT user_input, assistant_response, timestamp, context_tags, session_id
                FROM conversations
                WHERE user_input LIKE ? OR assistant_response LIKE ?
                ORDER BY timestamp DESC
                LIMIT ?
            ''', (f'%{query}%', f'%{query}%', limit))
            
            results = cursor.fetchall()
            
            conversations = []
            for row in results:
                conversations.append({
                    'user_input': row[0],
                    'assistant_response': row[1],
                    'timestamp': row[2],
                    'context_tags': json.loads(row[3]) if row[3] else [],
                    'session_id': row[4]
                })
            
            return conversations
    
    def get_current_context(self) -> str:
        """Get formatted context from recent conversations"""
        if not self.context_buffer:
            return ""
        
        context_parts = []
        for exchange in self.context_buffer[-10:]:  # Last 10 exchanges
            context_parts.append(f"User: {exchange['user_input']}")
            context_parts.append(f"Assistant: {exchange['assistant_response']}")
        
        return "\n".join(context_parts)
    
    def save_user_preference(self, key: str, value: str):
        """Save user preference or setting"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO user_preferences (key, value, updated_at)
                VALUES (?, ?, CURRENT_TIMESTAMP)
            ''', (key, value))
            
            conn.commit()
    
    def get_user_preference(self, key: str, default: str = None) -> Optional[str]:
        """Get user preference or setting"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute('SELECT value FROM user_preferences WHERE key = ?', (key,))
            result = cursor.fetchone()
            
            return result[0] if result else default
    
    def add_knowledge(self, topic: str, fact: str, source: str = None, confidence: float = 1.0):
        """Add information to the knowledge base"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO knowledge_base (topic, fact, source, confidence_score)
                VALUES (?, ?, ?, ?)
            ''', (topic, fact, source, confidence))
            
            conn.commit()
    
    def search_knowledge(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Search the knowledge base"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT topic, fact, source, confidence_score, created_at
                FROM knowledge_base
                WHERE topic LIKE ? OR fact LIKE ?
                ORDER BY confidence_score DESC, created_at DESC
                LIMIT ?
            ''', (f'%{query}%', f'%{query}%', limit))
            
            results = cursor.fetchall()
            
            knowledge = []
            for row in results:
                knowledge.append({
                    'topic': row[0],
                    'fact': row[1],
                    'source': row[2],
                    'confidence': row[3],
                    'created_at': row[4]
                })
            
            return knowledge
    
    def add_task(self, title: str, description: str = None, due_date: str = None, priority: int = 1) -> int:
        """Add a task or reminder"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            due_datetime = None
            if due_date:
                try:
                    due_datetime = datetime.fromisoformat(due_date)
                except ValueError:
                    pass
            
            cursor.execute('''
                INSERT INTO tasks (title, description, priority, due_date)
                VALUES (?, ?, ?, ?)
            ''', (title, description, priority, due_datetime))
            
            task_id = cursor.lastrowid
            conn.commit()
            
            return task_id
    
    def get_tasks(self, status: str = 'pending', limit: int = 20) -> List[Dict[str, Any]]:
        """Get tasks with specified status"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT id, title, description, status, priority, due_date, created_at
                FROM tasks
                WHERE status = ?
                ORDER BY priority DESC, due_date ASC
                LIMIT ?
            ''', (status, limit))
            
            results = cursor.fetchall()
            
            tasks = []
            for row in results:
                tasks.append({
                    'id': row[0],
                    'title': row[1],
                    'description': row[2],
                    'status': row[3],
                    'priority': row[4],
                    'due_date': row[5],
                    'created_at': row[6]
                })
            
            return tasks
    
    def complete_task(self, task_id: int) -> bool:
        """Mark a task as completed"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE tasks
                SET status = 'completed', completed_at = CURRENT_TIMESTAMP
                WHERE id = ?
            ''', (task_id,))
            
            success = cursor.rowcount > 0
            conn.commit()
            
            return success
    
    def get_session_summary(self, session_id: str = None) -> Dict[str, Any]:
        """Get summary of a session"""
        target_session = session_id or self.current_session_id
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Get session metadata
            cursor.execute('''
                SELECT start_time, end_time, interaction_count, session_summary
                FROM sessions
                WHERE session_id = ?
            ''', (target_session,))
            
            session_data = cursor.fetchone()
            
            # Get conversation count and topics
            cursor.execute('''
                SELECT COUNT(*), GROUP_CONCAT(DISTINCT context_tags)
                FROM conversations
                WHERE session_id = ?
            ''', (target_session,))
            
            conv_data = cursor.fetchone()
            
            return {
                'session_id': target_session,
                'start_time': session_data[0] if session_data else None,
                'end_time': session_data[1] if session_data else None,
                'interaction_count': session_data[2] if session_data else 0,
                'conversation_count': conv_data[0] if conv_data else 0,
                'summary': session_data[3] if session_data else None
            }
    
    def end_session(self, summary: str = None):
        """End the current session and start a new one"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE sessions
                SET end_time = CURRENT_TIMESTAMP, session_summary = ?
                WHERE session_id = ?
            ''', (summary, self.current_session_id))
            
            conn.commit()
        
        # Start new session
        self.current_session_id = self._generate_session_id()
        self.context_buffer = []
    
    def _generate_session_id(self) -> str:
        """Generate a unique session ID"""
        timestamp = datetime.now().isoformat()
        return hashlib.md5(timestamp.encode()).hexdigest()[:12]