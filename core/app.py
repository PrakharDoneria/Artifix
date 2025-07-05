import threading
import speech_recognition as sr
import time
from ui.layout import UI
from core.speech import SpeechEngine
from core.wake_word import WakeWordDetector, WakeWordConfig, ContinuousListener
from core.memory_manager import MemoryManager
from core.agent_modes import AgentModes
import query_handle

class ChatApp:
    def __init__(self):
        self.engine = SpeechEngine()
        self.recognizer = sr.Recognizer()
        self.ui = UI(self.send_message, self.start_voice_input)
        
        # Initialize new components
        self.memory_manager = MemoryManager()
        self.agent_modes = AgentModes()
        
        # Setup wake word detection
        wake_config = WakeWordConfig(
            wake_words=["hey artifix", "artifix", "hello artifix"],
            sensitivity=0.5,
            enabled=True
        )
        self.wake_detector = WakeWordDetector(wake_config, self.on_wake_word_detected)
        self.continuous_listener = ContinuousListener(self.wake_detector)
        
        # Start continuous listening
        self.start_continuous_listening()
        
        # Start reminder monitoring
        from core.task_manager import TaskManager
        self.task_manager = TaskManager()
        self.task_manager.start_reminder_monitoring(self.on_reminder_due)

    def main(self, page):
        self.ui.build(page)
        current_mode = self.agent_modes.get_current_mode()
        mode_name = current_mode.name if current_mode else "Assistant"
        
        welcome_msg = f"Hello! I'm Artifix, your AI assistant in {mode_name} mode. How can I help you today?"
        self.ui.add_message(welcome_msg, False)
        
        # Apply current mode's UI theme
        self.apply_current_theme()

    def start_continuous_listening(self):
        """Start continuous wake word detection"""
        try:
            self.continuous_listener.start_continuous_listening()
            print("Continuous wake word detection started")
        except Exception as e:
            print(f"Failed to start continuous listening: {e}")
            # Fallback to manual activation
            self.ui.add_message("Wake word detection unavailable. Use voice button for speech input.", False)

    def on_wake_word_detected(self, wake_word):
        """Callback when wake word is detected"""
        self.ui.add_message(f"Wake word detected: {wake_word}", False)
        self.engine.speak("Yes, I'm listening.")
        
        # Enter conversation mode
        self.continuous_listener.enter_conversation_mode()
        
        # Start listening for command
        threading.Thread(target=self.listen_for_command, daemon=True).start()

    def listen_for_command(self):
        """Listen for voice command after wake word"""
        try:
            with sr.Microphone() as source:
                self.ui.add_message("Listening for your command...", False)
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                
                # Listen with longer timeout for command
                audio = self.recognizer.listen(source, timeout=10, phrase_time_limit=8)
                text = self.recognizer.recognize_google(audio)
                
                self.ui.add_message(text, True)
                self.process_bot_response(text)
                
                # Update activity for conversation mode
                self.continuous_listener.update_activity()
                
        except sr.WaitTimeoutError:
            self.ui.add_message("No command received", False)
            self.continuous_listener.exit_conversation_mode()
        except sr.UnknownValueError:
            self.ui.add_message("Could not understand the command", False)
            self.engine.speak("I didn't understand that. Could you repeat?")
        except Exception as e:
            self.ui.add_message(f"Error: {str(e)}", False)

    def on_reminder_due(self, reminder):
        """Callback when a reminder is due"""
        self.ui.add_message(f"Reminder: {reminder.title}", False)
        self.engine.speak(f"Reminder: {reminder.message or reminder.title}")

    def apply_current_theme(self):
        """Apply the current agent mode's theme to UI"""
        try:
            theme = self.agent_modes.get_ui_theme()
            # This would apply theme colors to the UI
            # For now, just log the theme
            print(f"Applied theme: {theme}")
        except Exception as e:
            print(f"Failed to apply theme: {e}")

    def process_bot_response(self, message):
        self.ui.show_typing(True)
        try:
            # Get response with enhanced context
            reply = query_handle.handle(message)
            self.ui.show_typing(False)
            self.ui.add_message(reply, False)
            
            # Use current mode's voice settings
            voice_settings = self.agent_modes.get_voice_settings()
            
            # Update speech engine settings
            if hasattr(self.engine, 'engine') and self.engine.engine:
                try:
                    self.engine.engine.setProperty('rate', voice_settings.get('rate', 175))
                    self.engine.engine.setProperty('volume', voice_settings.get('volume', 0.8))
                except:
                    pass
            
            # Speak response
            threading.Thread(target=self.engine.speak, args=(reply,), daemon=True).start()
            
        except Exception as e:
            self.ui.show_typing(False)
            error_msg = f"Sorry, I encountered an error: {str(e)}"
            self.ui.add_message(error_msg, False)
            self.engine.speak("Sorry, I encountered an error.")

    def send_message(self, _):
        msg = self.ui.get_input()
        if not msg:
            return
        self.ui.clear_input()
        self.ui.add_message(msg, True)
        
        # Check for mode switching commands
        if self.handle_mode_commands(msg):
            return
        
        threading.Thread(target=self.process_bot_response, args=(msg,), daemon=True).start()

    def handle_mode_commands(self, message):
        """Handle special mode switching commands"""
        msg_lower = message.lower()
        
        if 'switch to' in msg_lower and 'mode' in msg_lower:
            # Extract mode name
            words = msg_lower.split()
            if 'to' in words:
                mode_idx = words.index('to') + 1
                if mode_idx < len(words):
                    mode_name = words[mode_idx].title()
                    result = self.agent_modes.set_active_mode(mode_name)
                    self.ui.add_message(result, False)
                    self.apply_current_theme()
                    self.engine.speak(result)
                    return True
        
        return False

    def start_voice_input(self, _):
        """Manual voice input activation"""
        def listen():
            with sr.Microphone() as source:
                self.ui.add_message("Listening...", False)
                try:
                    self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                    audio = self.recognizer.listen(source, timeout=8, phrase_time_limit=6)
                    text = self.recognizer.recognize_google(audio)
                    self.ui.add_message(text, True)
                    self.process_bot_response(text)
                except sr.WaitTimeoutError:
                    self.ui.add_message("No speech detected", False)
                except sr.UnknownValueError:
                    self.ui.add_message("Could not understand audio", False)
                except Exception as e:
                    self.ui.add_message(f"Error: {str(e)}", False)
        threading.Thread(target=listen, daemon=True).start()

    def shutdown(self):
        """Cleanup when shutting down"""
        try:
            self.continuous_listener.stop_continuous_listening()
            self.task_manager.stop_reminder_monitoring()
            self.memory_manager.end_session("Session ended by user")
        except Exception as e:
            print(f"Error during shutdown: {e}")