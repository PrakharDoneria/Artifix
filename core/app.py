import threading
import speech_recognition as sr
import time
from ui.layout import UI
from core.speech import SpeechEngine
from clapDetector import ClapDetector
import query_handle

class ChatApp:
    def __init__(self):
        self.engine = SpeechEngine()
        self.recognizer = sr.Recognizer()
        self.ui = UI(self.send_message, self.start_voice_input)
        self.clap_detector = ClapDetector(inputDevice=-1, logLevel=10)
        self.clap_detector.initAudio()
        threading.Thread(target=self.listen_for_claps, daemon=True).start()

    def main(self, page):
        self.ui.build(page)
        self.ui.add_message("Hello! I'm Artifix, your AI assistant. How can I help you today?", False)

    def listen_for_claps(self):
        while True:
            audio = self.clap_detector.getAudio()
            result = self.clap_detector.run(thresholdBias=6000, lowcut=200, highcut=3200, audioData=audio)
            if len(result) == 1:
                self.single_clap()
            elif len(result) == 2:
                self.double_clap()
            time.sleep(1 / 60)

    def single_clap(self):
        self.ui.add_message("Single clap detected", False)
        self.engine.speak("Hello! How can I assist you today?")

    def double_clap(self):
        self.ui.add_message("Double clap detected", False)
        self.engine.speak("Hey sir, I'm here to help you out")

    def process_bot_response(self, message):
        self.ui.show_typing(True)
        try:
            reply = query_handle.handle(message.lower())
            self.ui.show_typing(False)
            self.ui.add_message(reply, False)
            threading.Thread(target=self.engine.speak, args=(reply,), daemon=True).start()
        except Exception as e:
            self.ui.show_typing(False)
            self.ui.add_message(f"Sorry, I encountered an error: {str(e)}", False)

    def send_message(self, _):
        msg = self.ui.get_input()
        if not msg:
            return
        self.ui.clear_input()
        self.ui.add_message(msg, True)
        threading.Thread(target=self.process_bot_response, args=(msg,), daemon=True).start()

    def start_voice_input(self, _):
        def listen():
            with sr.Microphone() as source:
                self.ui.add_message("Listening...", False)
                try:
                    audio = self.recognizer.listen(source, timeout=5)
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