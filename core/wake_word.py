import threading
import time
import json
from typing import Callable, Optional, List
from dataclasses import dataclass

@dataclass
class WakeWordConfig:
    """Configuration for wake word detection"""
    wake_words: List[str]
    sensitivity: float = 0.5
    timeout: float = 1.0
    enabled: bool = True

class WakeWordDetector:
    """Wake word detection system for voice activation"""
    
    def __init__(self, config: WakeWordConfig, callback: Callable = None):
        self.config = config
        self.callback = callback
        self.is_listening = False
        self.listen_thread = None
        self._stop_event = threading.Event()
        
        # For now, we'll use a simple keyword matching approach
        # In a real implementation, this would use a more sophisticated model
        self.wake_words = [word.lower() for word in config.wake_words]
        
    def start_listening(self):
        """Start continuous wake word detection"""
        if self.is_listening:
            return
        
        self.is_listening = True
        self._stop_event.clear()
        self.listen_thread = threading.Thread(target=self._listen_loop, daemon=True)
        self.listen_thread.start()
        print(f"Wake word detection started. Listening for: {', '.join(self.config.wake_words)}")
    
    def stop_listening(self):
        """Stop wake word detection"""
        if not self.is_listening:
            return
        
        self.is_listening = False
        self._stop_event.set()
        
        if self.listen_thread and self.listen_thread.is_alive():
            self.listen_thread.join(timeout=2.0)
        
        print("Wake word detection stopped")
    
    def _listen_loop(self):
        """Main listening loop for wake word detection"""
        try:
            import speech_recognition as sr
            recognizer = sr.Recognizer()
            microphone = sr.Microphone()
            
            # Adjust for ambient noise
            with microphone as source:
                recognizer.adjust_for_ambient_noise(source, duration=1)
            
            while self.is_listening and not self._stop_event.is_set():
                try:
                    with microphone as source:
                        # Listen for wake word with shorter timeout
                        audio = recognizer.listen(source, timeout=0.5, phrase_time_limit=3)
                    
                    try:
                        # Recognize speech
                        text = recognizer.recognize_google(audio).lower()
                        print(f"Heard: {text}")
                        
                        # Check for wake words
                        if self._contains_wake_word(text):
                            print(f"Wake word detected: {text}")
                            if self.callback:
                                threading.Thread(target=self.callback, args=(text,), daemon=True).start()
                            
                            # Brief pause after wake word detection
                            time.sleep(1)
                    
                    except sr.UnknownValueError:
                        # Could not understand audio - this is normal
                        pass
                    except sr.RequestError as e:
                        print(f"Speech recognition service error: {e}")
                        time.sleep(5)  # Wait before retrying
                
                except sr.WaitTimeoutError:
                    # No speech detected - this is normal for continuous listening
                    pass
                except Exception as e:
                    print(f"Error in wake word detection: {e}")
                    time.sleep(1)
        
        except ImportError:
            print("Speech recognition not available - wake word detection disabled")
        except Exception as e:
            print(f"Failed to initialize wake word detection: {e}")
    
    def _contains_wake_word(self, text: str) -> bool:
        """Check if text contains any wake words"""
        text = text.lower().strip()
        
        for wake_word in self.wake_words:
            if wake_word in text:
                return True
        
        return False
    
    def add_wake_word(self, word: str):
        """Add a new wake word"""
        word = word.lower()
        if word not in self.wake_words:
            self.wake_words.append(word)
            self.config.wake_words.append(word)
            print(f"Added wake word: {word}")
    
    def remove_wake_word(self, word: str):
        """Remove a wake word"""
        word = word.lower()
        if word in self.wake_words:
            self.wake_words.remove(word)
            self.config.wake_words.remove(word)
            print(f"Removed wake word: {word}")
    
    def get_wake_words(self) -> List[str]:
        """Get list of current wake words"""
        return self.config.wake_words.copy()
    
    def set_sensitivity(self, sensitivity: float):
        """Set detection sensitivity (0.0 to 1.0)"""
        self.config.sensitivity = max(0.0, min(1.0, sensitivity))
        print(f"Wake word sensitivity set to: {self.config.sensitivity}")

# Simple wake word implementation for demonstration
class SimpleWakeWordDetector:
    """Simplified wake word detector that doesn't require external models"""
    
    def __init__(self, wake_words: List[str], callback: Callable = None):
        self.wake_words = [word.lower() for word in wake_words]
        self.callback = callback
        self.is_active = False
        self.last_input = ""
    
    def check_input(self, text: str) -> bool:
        """Check if input contains wake word"""
        if not text:
            return False
        
        text_lower = text.lower()
        for wake_word in self.wake_words:
            if wake_word in text_lower:
                if self.callback:
                    self.callback(wake_word)
                return True
        return False
    
    def add_wake_word(self, word: str):
        """Add a wake word"""
        word = word.lower()
        if word not in self.wake_words:
            self.wake_words.append(word)
    
    def remove_wake_word(self, word: str):
        """Remove a wake word"""
        word = word.lower()
        if word in self.wake_words:
            self.wake_words.remove(word)
    
    def get_wake_words(self) -> List[str]:
        """Get current wake words"""
        return self.wake_words.copy()

# Voice Activity Detection helper
class VoiceActivityDetector:
    """Detects when user is speaking"""
    
    def __init__(self, energy_threshold: int = 300):
        self.energy_threshold = energy_threshold
        self.is_speaking = False
    
    def detect_speech(self, audio_data) -> bool:
        """Detect if audio contains speech"""
        try:
            import audioop
            # Calculate RMS energy
            rms = audioop.rms(audio_data, 2)
            return rms > self.energy_threshold
        except:
            return False
    
    def set_threshold(self, threshold: int):
        """Set energy threshold for speech detection"""
        self.energy_threshold = threshold

# Continuous listening manager
class ContinuousListener:
    """Manages continuous listening with wake word detection"""
    
    def __init__(self, wake_word_detector: WakeWordDetector):
        self.wake_word_detector = wake_word_detector
        self.voice_detector = VoiceActivityDetector()
        self.is_listening = False
        self.conversation_mode = False
        self.conversation_timeout = 10  # seconds
        self.last_activity = time.time()
        
    def start_continuous_listening(self):
        """Start continuous listening mode"""
        self.is_listening = True
        self.wake_word_detector.start_listening()
        
        # Monitor thread for conversation timeout
        threading.Thread(target=self._monitor_conversation, daemon=True).start()
    
    def stop_continuous_listening(self):
        """Stop continuous listening mode"""
        self.is_listening = False
        self.conversation_mode = False
        self.wake_word_detector.stop_listening()
    
    def enter_conversation_mode(self):
        """Enter conversation mode after wake word detection"""
        self.conversation_mode = True
        self.last_activity = time.time()
        print("Entering conversation mode...")
    
    def exit_conversation_mode(self):
        """Exit conversation mode"""
        self.conversation_mode = False
        print("Exiting conversation mode...")
    
    def update_activity(self):
        """Update last activity timestamp"""
        self.last_activity = time.time()
    
    def _monitor_conversation(self):
        """Monitor conversation timeout"""
        while self.is_listening:
            if self.conversation_mode:
                if time.time() - self.last_activity > self.conversation_timeout:
                    self.exit_conversation_mode()
            time.sleep(1)