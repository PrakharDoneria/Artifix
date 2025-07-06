import threading
import time
import logging
from typing import Callable, Optional

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ClapDetectionManager:
    """Double clap detection system for voice activation"""
    
    def __init__(self, callback: Optional[Callable] = None):
        self.callback = callback
        self.is_listening = False
        self.clap_detector = None
        self.listen_thread = None
        self.last_clap_time = 0
        self.clap_timeout = 2.0  # seconds between double claps
        self.clap_count = 0
        
        # Try to initialize clap detector
        self._init_clap_detector()
    
    def _init_clap_detector(self):
        """Initialize the clap detector"""
        try:
            # Try to import and initialize clap detector
            from clapDetector import ClapDetector
            
            self.clap_detector = ClapDetector()
            logger.info("Clap detector initialized successfully")
            
        except ImportError:
            logger.warning("clap-detector package not available, using mock implementation")
            self.clap_detector = MockClapDetector()
        except Exception as e:
            logger.error(f"Failed to initialize clap detector: {e}")
            self.clap_detector = MockClapDetector()
    
    def start_listening(self):
        """Start listening for double claps"""
        if self.is_listening:
            return
        
        self.is_listening = True
        self.listen_thread = threading.Thread(target=self._listen_loop, daemon=True)
        self.listen_thread.start()
        logger.info("Started listening for double claps")
    
    def stop_listening(self):
        """Stop listening for double claps"""
        if not self.is_listening:
            return
        
        self.is_listening = False
        
        if self.listen_thread and self.listen_thread.is_alive():
            self.listen_thread.join(timeout=2.0)
        
        logger.info("Stopped listening for double claps")
    
    def _listen_loop(self):
        """Main listening loop for clap detection"""
        if not self.clap_detector:
            logger.error("No clap detector available")
            return
        
        while self.is_listening:
            try:
                # Check for clap
                if self.clap_detector.detect_clap():
                    self._handle_clap_detected()
                
                time.sleep(0.1)  # Small delay to prevent excessive CPU usage
                
            except Exception as e:
                logger.error(f"Error in clap detection loop: {e}")
                time.sleep(1)  # Longer delay on error
    
    def _handle_clap_detected(self):
        """Handle when a clap is detected"""
        current_time = time.time()
        
        # Check if this is part of a double clap sequence
        if current_time - self.last_clap_time <= self.clap_timeout:
            self.clap_count += 1
            
            # Double clap detected!
            if self.clap_count >= 2:
                logger.info("Double clap detected!")
                self._trigger_callback()
                self.clap_count = 0  # Reset counter
        else:
            # First clap or timeout exceeded
            self.clap_count = 1
        
        self.last_clap_time = current_time
    
    def _trigger_callback(self):
        """Trigger the callback function for double clap detection"""
        if self.callback:
            try:
                # Run callback in separate thread to avoid blocking
                threading.Thread(target=self.callback, daemon=True).start()
            except Exception as e:
                logger.error(f"Error triggering clap callback: {e}")
    
    def set_callback(self, callback: Callable):
        """Set the callback function for double clap detection"""
        self.callback = callback
    
    def set_clap_timeout(self, timeout: float):
        """Set the timeout between claps for double clap detection"""
        self.clap_timeout = timeout

class MockClapDetector:
    """Mock clap detector for development/fallback"""
    
    def __init__(self):
        self.last_mock_clap = 0
        self.mock_interval = 10  # Mock clap every 10 seconds for testing
        logger.info("Using mock clap detector")
    
    def detect_clap(self):
        """Mock clap detection - returns True occasionally for testing"""
        current_time = time.time()
        
        # Simulate clap detection for testing
        if current_time - self.last_mock_clap > self.mock_interval:
            self.last_mock_clap = current_time
            # Simulate double clap by returning True twice quickly
            time.sleep(0.5)
            return True
        
        return False

class EnhancedClapDetector:
    """Enhanced clap detector with better accuracy"""
    
    def __init__(self):
        self.detector = None
        self.audio_buffer = []
        self.sample_rate = 44100
        self.buffer_size = 1024
        
        try:
            import pyaudio
            import numpy as np
            
            self.pyaudio = pyaudio
            self.np = np
            self._init_audio_stream()
            
        except ImportError:
            logger.warning("PyAudio or NumPy not available for enhanced clap detection")
            self.detector = MockClapDetector()
    
    def _init_audio_stream(self):
        """Initialize audio stream for clap detection"""
        try:
            self.pa = self.pyaudio.PyAudio()
            
            self.stream = self.pa.open(
                format=self.pyaudio.paFloat32,
                channels=1,
                rate=self.sample_rate,
                input=True,
                frames_per_buffer=self.buffer_size
            )
            
            logger.info("Enhanced clap detector audio stream initialized")
            
        except Exception as e:
            logger.error(f"Failed to initialize audio stream: {e}")
            self.detector = MockClapDetector()
    
    def detect_clap(self):
        """Detect clap using audio analysis"""
        if self.detector:
            return self.detector.detect_clap()
        
        try:
            # Read audio data
            data = self.stream.read(self.buffer_size, exception_on_overflow=False)
            audio_data = self.np.frombuffer(data, dtype=self.np.float32)
            
            # Simple clap detection based on sudden amplitude increase
            rms = self.np.sqrt(self.np.mean(audio_data**2))
            
            # Threshold for clap detection (adjust as needed)
            clap_threshold = 0.1
            
            return rms > clap_threshold
            
        except Exception as e:
            logger.error(f"Error in enhanced clap detection: {e}")
            return False
    
    def cleanup(self):
        """Cleanup audio resources"""
        try:
            if hasattr(self, 'stream'):
                self.stream.stop_stream()
                self.stream.close()
            if hasattr(self, 'pa'):
                self.pa.terminate()
        except Exception as e:
            logger.error(f"Error cleaning up audio resources: {e}")

# Factory function to create appropriate clap detector
def create_clap_detector(enhanced=False):
    """Create a clap detector instance"""
    if enhanced:
        return EnhancedClapDetector()
    else:
        try:
            from clapDetector import ClapDetector
            return ClapDetector()
        except ImportError:
            return MockClapDetector()