import api.wikipedia as wiki
import datetime
import api.sarvam as sarvam
from core.system_control import SystemController
from core.file_manager import FileManager
from core.memory_manager import MemoryManager
from core.communication import CommunicationHub
from core.task_manager import TaskManager, Task, Event, Reminder
from core.developer_tools import DeveloperTools
from core.agent_modes import AgentModes, ModeBasedResponseGenerator
from core.camera import CameraManager, MultimodalProcessor
import re
import json

# Initialize modules
system_controller = SystemController()
file_manager = FileManager()
memory_manager = MemoryManager()
communication_hub = CommunicationHub()
task_manager = TaskManager()
developer_tools = DeveloperTools()
agent_modes = AgentModes()
response_generator = ModeBasedResponseGenerator(agent_modes)

# Initialize camera system
camera_manager = CameraManager()
multimodal_processor = MultimodalProcessor(camera_manager)

def handle(query):
    if not query or not isinstance(query, str):
        return "Invalid query. Please provide a valid string."

    original_query = query
    query = query.lower().strip()
    
    # Save conversation to memory
    try:
        response = _process_query(query, original_query)
        memory_manager.save_conversation(original_query, response, _extract_context_tags(query))
        
        # Apply mode-based response generation
        response = response_generator.generate_response(original_query, response)
        
        return response
    except Exception as e:
        error_response = f"I encountered an error: {str(e)}"
        memory_manager.save_conversation(original_query, error_response)
        return error_response

def _process_query(query, original_query):
    """Process the query and return appropriate response"""
    
    # Camera and visual commands
    visual_response = multimodal_processor.handle_visual_commands(original_query)
    if visual_response:
        return visual_response
    
    # System control commands
    if any(word in query for word in ['volume', 'sound']):
        return _handle_volume_control(query)
    
    elif any(word in query for word in ['launch', 'open', 'start']) and any(word in query for word in ['app', 'application', 'program']):
        return _handle_app_launch(query)
    
    elif any(word in query for word in ['system', 'cpu', 'memory', 'battery', 'disk']):
        return _handle_system_info(query)
    
    elif any(word in query for word in ['shutdown', 'restart', 'sleep', 'power']):
        return _handle_power_management(query)
    
    # File management commands
    elif any(word in query for word in ['file', 'folder', 'directory']):
        return _handle_file_operations(query)
    
    elif 'search files' in query or 'find file' in query:
        return _handle_file_search(query)
    
    # Task management commands
    elif any(word in query for word in ['task', 'todo', 'reminder']):
        return _handle_task_management(query)
    
    elif any(word in query for word in ['calendar', 'event', 'meeting', 'appointment']):
        return _handle_calendar_management(query)
    
    # Communication commands
    elif any(word in query for word in ['email', 'send mail']):
        return _handle_email_operations(query)
    
    elif 'translate' in query:
        return _handle_translation(query)
    
    # Developer tools commands
    elif any(word in query for word in ['git', 'commit', 'push', 'pull']):
        return _handle_git_operations(query)
    
    elif any(word in query for word in ['test', 'lint', 'build']):
        return _handle_development_tasks(query)
    
    # Agent mode commands
    elif any(word in query for word in ['mode', 'personality', 'switch']):
        return _handle_agent_mode(query)
    
    # Memory and context commands
    elif any(word in query for word in ['remember', 'recall', 'history']):
        return _handle_memory_operations(query)
    
    # Basic queries
    elif 'who is' in query:
        search_term = query.replace("who is", "").strip()
        return wiki.wiki(search_term)
    
    elif any(word in query for word in ['time', 'clock']):
        str_time = datetime.datetime.now().strftime("%H:%M:%S")
        return f"The time is {str_time}."
    
    elif 'date' in query:
        str_date = datetime.datetime.now().strftime("%A, %B %d, %Y")
        return f"Today is {str_date}."
    
    # Fallback to AI assistant with multimodal context
    else:
        try:
            # Add context from memory
            context = memory_manager.get_current_context()
            
            # Add visual context if query might benefit from it
            enhanced_query = multimodal_processor.process_multimodal_query(original_query)
            
            if context:
                enhanced_query = f"Previous context:\n{context}\n\nCurrent query: {enhanced_query}"
            
            # Use current mode's system prompt
            system_prompt = agent_modes.get_system_prompt()
            response = sarvam.ask(enhanced_query)
            return response
        except Exception as e:
            return f"I couldn't process that request. Error: {str(e)}"

def _handle_volume_control(query):
    """Handle volume control commands"""
    if 'up' in query or 'increase' in query:
        return system_controller.control_volume('up')
    elif 'down' in query or 'decrease' in query or 'lower' in query:
        return system_controller.control_volume('down')
    elif 'mute' in query:
        return system_controller.control_volume('mute')
    else:
        # Extract volume level if specified
        match = re.search(r'(\d+)%?', query)
        if match:
            level = int(match.group(1))
            return system_controller.control_volume('set', level)
        return "Please specify volume action: up, down, mute, or set level"

def _handle_app_launch(query):
    """Handle application launch commands"""
    # Extract app name
    words = query.split()
    app_keywords = ['launch', 'open', 'start', 'run']
    
    for i, word in enumerate(words):
        if word in app_keywords and i + 1 < len(words):
            app_name = words[i + 1]
            return system_controller.launch_application(app_name)
    
    return "Please specify which application to launch"

def _handle_system_info(query):
    """Handle system information requests"""
    info = system_controller.get_system_info()
    
    if 'battery' in query:
        return f"Battery level: {info.get('battery_percent', 'N/A')}%"
    elif 'cpu' in query:
        return f"CPU usage: {info.get('cpu_percent', 'N/A')}%"
    elif 'memory' in query or 'ram' in query:
        return f"Memory usage: {info.get('memory_percent', 'N/A')}%"
    elif 'disk' in query:
        return f"Disk usage: {info.get('disk_usage', 'N/A')}%"
    else:
        # Return comprehensive system info
        return f"""System Status:
- CPU: {info.get('cpu_percent', 'N/A')}%
- Memory: {info.get('memory_percent', 'N/A')}%
- Battery: {info.get('battery_percent', 'N/A')}%
- Disk: {info.get('disk_usage', 'N/A')}%
- Network: {'Connected' if info.get('network_connected') else 'Disconnected'}
- Uptime: {info.get('uptime', 'N/A')}"""

def _handle_power_management(query):
    """Handle power management commands"""
    if 'shutdown' in query:
        return system_controller.power_management('shutdown')
    elif 'restart' in query or 'reboot' in query:
        return system_controller.power_management('restart')
    elif 'sleep' in query:
        return system_controller.power_management('sleep')
    else:
        return "Available power options: shutdown, restart, sleep"

def _handle_file_operations(query):
    """Handle file operations"""
    if 'list' in query or 'show' in query:
        files = file_manager.list_files()
        if files and not files[0].get('error'):
            file_list = '\n'.join([f"- {f['name']} ({f['type']})" for f in files[:10]])
            return f"Recent files:\n{file_list}"
        return "No files found or access denied"
    
    elif 'create' in query:
        # Basic file creation
        return "Please specify the file path and content to create"
    
    elif 'delete' in query:
        return "Please specify the file path to delete"
    
    else:
        return "Available file operations: list, create, delete, copy, move"

def _handle_file_search(query):
    """Handle file search operations"""
    # Extract search term
    search_terms = ['search files', 'find file', 'search for', 'find']
    search_term = query
    
    for term in search_terms:
        if term in query:
            search_term = query.replace(term, '').strip()
            break
    
    if search_term:
        results = file_manager.search_files(search_term)
        if results and not results[0].get('error'):
            file_list = '\n'.join([f"- {r['name']} in {r['path']}" for r in results[:5]])
            return f"Found files matching '{search_term}':\n{file_list}"
        return f"No files found matching '{search_term}'"
    
    return "Please specify what to search for"

def _handle_task_management(query):
    """Handle task management operations"""
    if 'add task' in query or 'create task' in query:
        # Extract task title
        task_title = query.replace('add task', '').replace('create task', '').strip()
        if task_title:
            task = Task(title=task_title)
            task_id = task_manager.add_task(task)
            return f"Added task: {task_title} (ID: {task_id})"
        return "Please specify the task title"
    
    elif 'list tasks' in query or 'show tasks' in query:
        tasks = task_manager.get_tasks(status='pending', limit=10)
        if tasks:
            task_list = '\n'.join([f"- {t.title} (Priority: {t.priority})" for t in tasks])
            return f"Pending tasks:\n{task_list}"
        return "No pending tasks"
    
    elif 'complete task' in query:
        # For now, just acknowledge
        return "Please specify which task to complete"
    
    else:
        return "Available task operations: add task, list tasks, complete task"

def _handle_calendar_management(query):
    """Handle calendar and event management"""
    if 'today' in query:
        events = task_manager.get_today_events()
        if events:
            event_list = '\n'.join([f"- {e.title} at {e.start_time.strftime('%H:%M')}" for e in events])
            return f"Today's events:\n{event_list}"
        return "No events scheduled for today"
    
    elif 'upcoming' in query:
        events = task_manager.get_upcoming_events(days=7)
        if events:
            event_list = '\n'.join([f"- {e.title} on {e.start_time.strftime('%m/%d at %H:%M')}" for e in events[:5]])
            return f"Upcoming events:\n{event_list}"
        return "No upcoming events in the next 7 days"
    
    else:
        return "Available calendar operations: today's events, upcoming events"

def _handle_email_operations(query):
    """Handle email operations"""
    return "Email functionality requires configuration. Please set up your email credentials first."

def _handle_translation(query):
    """Handle translation requests"""
    # Extract text to translate and target language
    return "Translation feature requires API configuration"

def _handle_git_operations(query):
    """Handle Git operations"""
    if 'status' in query:
        status = developer_tools.git_manager.get_status()
        if status.get('error'):
            return status['error']
        
        return f"""Git Status:
- Branch: {status.get('branch', 'unknown')}
- Clean: {'Yes' if not status.get('is_dirty') else 'No'}
- Untracked files: {len(status.get('untracked_files', []))}
- Modified files: {len(status.get('modified_files', []))}"""
    
    elif 'commit' in query:
        return "Please specify commit message"
    
    elif 'push' in query:
        return developer_tools.git_manager.push()
    
    elif 'pull' in query:
        return developer_tools.git_manager.pull()
    
    else:
        return "Available Git operations: status, commit, push, pull"

def _handle_development_tasks(query):
    """Handle development tasks"""
    if 'test' in query:
        return developer_tools.run_tests()
    elif 'lint' in query:
        return developer_tools.lint_code()
    elif 'build' in query:
        return developer_tools.build_project()
    else:
        return "Available development tasks: test, lint, build"

def _handle_agent_mode(query):
    """Handle agent mode changes"""
    if 'switch to' in query or 'change to' in query:
        # Extract mode name
        mode_name = query.split('to')[-1].strip().title()
        return agent_modes.set_active_mode(mode_name)
    
    elif 'list modes' in query or 'show modes' in query:
        modes = agent_modes.get_modes()
        mode_list = '\n'.join([f"- {m['name']}: {m['description']} {'(active)' if m['active'] else ''}" for m in modes])
        return f"Available modes:\n{mode_list}"
    
    elif 'current mode' in query:
        current = agent_modes.get_current_mode()
        if current:
            return f"Current mode: {current.name} - {current.description}"
        return "No active mode"
    
    else:
        return "Available mode operations: switch to [mode], list modes, current mode"

def _handle_memory_operations(query):
    """Handle memory and recall operations"""
    if 'search' in query or 'recall' in query:
        # Extract search term
        search_term = query.replace('search', '').replace('recall', '').replace('remember', '').strip()
        if search_term:
            results = memory_manager.search_conversations(search_term)
            if results:
                conv_list = '\n'.join([f"- {r['user_input'][:50]}..." for r in results[:3]])
                return f"Found conversations about '{search_term}':\n{conv_list}"
            return f"No conversations found about '{search_term}'"
    
    elif 'history' in query:
        history = memory_manager.get_conversation_history(limit=5)
        if history:
            hist_list = '\n'.join([f"- You: {h['user_input'][:30]}..." for h in history])
            return f"Recent conversation history:\n{hist_list}"
        return "No conversation history found"
    
    else:
        return "Available memory operations: search [topic], recall [topic], history"

def _extract_context_tags(query):
    """Extract context tags from query for memory categorization"""
    tags = []
    
    # System tags
    if any(word in query for word in ['volume', 'app', 'system', 'power']):
        tags.append('system_control')
    
    # File tags
    if any(word in query for word in ['file', 'folder', 'search files']):
        tags.append('file_management')
    
    # Task tags
    if any(word in query for word in ['task', 'calendar', 'reminder']):
        tags.append('task_management')
    
    # Development tags
    if any(word in query for word in ['git', 'code', 'test', 'build']):
        tags.append('development')
    
    # Visual tags
    if any(word in query for word in ['camera', 'picture', 'see', 'look']):
        tags.append('visual_interaction')
    
    # General tags
    if any(word in query for word in ['who is', 'what is']):
        tags.append('information_query')
    
    return tags