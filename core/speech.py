import pyttsx3
import threading

class SpeechEngine:
    def __init__(self):
        self.lock = threading.Lock()
        self.engine = None
        self.init_engine()

    def init_engine(self):
        try:
            self.engine = pyttsx3.init()
            voices = self.engine.getProperty('voices')
            self.engine.setProperty('voice', voices[0].id)
            self.engine.setProperty('rate', 175)
        except Exception as e:
            print(f"Speech engine init failed: {e}")

    def speak(self, text):
        if self.lock.acquire(blocking=False):
            try:
                if not self.engine or not hasattr(self.engine, 'say'):
                    self.init_engine()
                self.engine.say(text)
                self.engine.runAndWait()
            except Exception as e:
                print(f"Speech error: {e}")
                self.init_engine()
            finally:
                self.lock.release()