#!/usr/bin/env python3

"""
Artifix AI Desktop Assistant - Demo Script
This demonstrates the core functionality without requiring external dependencies
"""

import json
import sqlite3
from datetime import datetime
from pathlib import Path

def demo_memory_system():
    """Demonstrate the memory management system"""
    print("🧠 Testing Memory System...")
    
    try:
        from core.memory_manager import MemoryManager
        memory = MemoryManager(db_path="demo_memory.db")
        
        # Save a conversation
        memory.save_conversation(
            "What's the weather today?",
            "I don't have access to weather data, but I can help you with many other tasks!",
            ["information_query"]
        )
        
        # Search conversations
        results = memory.search_conversations("weather")
        print(f"✓ Found {len(results)} conversations about weather")
        
        # Get session summary
        summary = memory.get_session_summary()
        print(f"✓ Session has {summary.get('interaction_count', 0)} interactions")
        
        return True
    except Exception as e:
        print(f"❌ Memory system error: {e}")
        return False

def demo_agent_modes():
    """Demonstrate the agent mode system"""
    print("\n🎭 Testing Agent Modes...")
    
    try:
        from core.agent_modes import AgentModes, ModeBasedResponseGenerator
        
        modes = AgentModes()
        
        # List available modes
        available_modes = modes.get_modes()
        print(f"✓ Available modes: {[m['name'] for m in available_modes]}")
        
        # Switch to technical mode
        result = modes.set_active_mode("Technical")
        print(f"✓ Mode switch: {result}")
        
        # Get current mode details
        current = modes.get_current_mode()
        if current:
            print(f"✓ Current mode: {current.name} - {current.description}")
        
        # Test response generation
        generator = ModeBasedResponseGenerator(modes)
        enhanced_response = generator.generate_response(
            "How do I debug Python code?",
            "You can use debuggers like pdb or IDE debugging tools."
        )
        print(f"✓ Enhanced response generated")
        
        return True
    except Exception as e:
        print(f"❌ Agent modes error: {e}")
        return False

def demo_file_manager():
    """Demonstrate the file management system"""
    print("\n📁 Testing File Manager...")
    
    try:
        from core.file_manager import FileManager
        
        file_mgr = FileManager()
        
        # Create a test file
        test_content = "This is a test file created by Artifix AI"
        result = file_mgr.create_file("test_artifix.txt", test_content)
        print(f"✓ File creation: {result}")
        
        # Read the file back
        content = file_mgr.read_file("test_artifix.txt")
        print(f"✓ File read: Content length {len(content)} chars")
        
        # Get file info
        info = file_mgr.get_file_info("test_artifix.txt")
        if not info.get('error'):
            print(f"✓ File info: {info['name']} ({info['size']} bytes)")
        
        # Search for files
        results = file_mgr.search_files("artifix")
        print(f"✓ Found {len(results)} files matching 'artifix'")
        
        # Clean up
        file_mgr.delete_file("test_artifix.txt")
        
        return True
    except Exception as e:
        print(f"❌ File manager error: {e}")
        return False

def demo_task_manager():
    """Demonstrate the task management system"""
    print("\n📅 Testing Task Manager...")
    
    try:
        from core.task_manager import TaskManager, Task
        
        task_mgr = TaskManager(db_path="demo_tasks.db")
        
        # Create a sample task
        task = Task(
            title="Test Artifix AI features",
            description="Explore all the new capabilities",
            priority=3
        )
        
        task_id = task_mgr.add_task(task)
        print(f"✓ Created task with ID: {task_id}")
        
        # Get tasks
        tasks = task_mgr.get_tasks(status='pending', limit=5)
        print(f"✓ Found {len(tasks)} pending tasks")
        
        # Get productivity stats
        stats = task_mgr.get_productivity_stats(days=7)
        print(f"✓ Productivity stats: {stats['total_tasks_created']} tasks created this week")
        
        return True
    except Exception as e:
        print(f"❌ Task manager error: {e}")
        return False

def demo_query_processing():
    """Demonstrate basic query processing"""
    print("\n🤖 Testing Query Processing...")
    
    try:
        # Test with mock data since API might not be available
        test_queries = [
            "what time is it",
            "switch to casual mode",
            "list modes",
            "add task: Review Artifix features"
        ]
        
        # Import the query handler
        import query_handle
        
        for query in test_queries:
            try:
                # This might fail due to missing API keys, but we can test the routing
                response = query_handle.handle(query)
                print(f"✓ Query '{query}' -> Response received ({len(response)} chars)")
            except Exception as e:
                # Expected for queries requiring external APIs
                print(f"⚠ Query '{query}' -> {str(e)[:50]}...")
        
        return True
    except Exception as e:
        print(f"❌ Query processing error: {e}")
        return False

def run_demo():
    """Run the complete demo"""
    print("🚀 Artifix AI Desktop Assistant - Feature Demo")
    print("=" * 50)
    
    results = []
    
    # Test core components
    results.append(demo_memory_system())
    results.append(demo_agent_modes())
    results.append(demo_file_manager())
    results.append(demo_task_manager())
    results.append(demo_query_processing())
    
    # Summary
    print("\n" + "=" * 50)
    passed = sum(results)
    total = len(results)
    
    print(f"📊 Demo Results: {passed}/{total} components working")
    
    if passed == total:
        print("🎉 All core features are functional!")
    elif passed >= total * 0.8:
        print("✅ Most features are working! Some may need configuration.")
    else:
        print("⚠️ Some features need setup or dependencies.")
    
    print("\n🔧 To enable full functionality:")
    print("1. Install dependencies: pip install -r requirements.txt")
    print("2. Configure API keys in api/.env")
    print("3. Set up optional services (email, Slack, etc.)")
    
    # Cleanup demo files
    try:
        Path("demo_memory.db").unlink(missing_ok=True)
        Path("demo_tasks.db").unlink(missing_ok=True)
        print("\n🧹 Demo files cleaned up")
    except:
        pass

if __name__ == "__main__":
    run_demo()