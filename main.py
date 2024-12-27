import flet as ft
import time
import threading
import pyttsx3
import speech_recognition as sr
import query_handle
from clapDetector import ClapDetector

class ChatApp:
    def __init__(self):
        self.engine = None
        self.speech_lock = threading.Lock()
        self.setup_speech_engine()
        self.recognizer = sr.Recognizer()
        self.clap_detector = None
        self.setup_clap_detector()
        
    def setup_speech_engine(self):
        try:
            self.engine = pyttsx3.init()
            voices = self.engine.getProperty('voices')
            self.engine.setProperty('voice', voices[0].id)
            self.engine.setProperty('rate', 175)
        except Exception as e:
            print(f"Speech engine initialization error: {e}")
        
    def setup_clap_detector(self):
        try:
            # Initialize clap detector
            self.clap_detector = ClapDetector(inputDevice=-1, logLevel=10)
            self.clap_detector.initAudio()
            threading.Thread(target=self.listen_for_claps, daemon=True).start()
        except Exception as e:
            print(f"Clap detection setup failed: {e}")
        
    def listen_for_claps(self):
        """Listen for claps (single and double) and trigger corresponding response."""
        thresholdBias = 6000
        lowcut = 200
        highcut = 3200
        
        try:
            while True:
                audioData = self.clap_detector.getAudio()
                result = self.clap_detector.run(thresholdBias=thresholdBias, lowcut=lowcut, highcut=highcut, audioData=audioData)
                
                if len(result) == 1:
                    self.handle_single_clap()  # Handle single clap
                elif len(result) == 2:
                    self.handle_double_clap()  # Handle double clap
                
                time.sleep(1/60)
        except Exception as e:
            print(f"Error during clap detection: {e}")
        
    def handle_single_clap(self):
        """Respond to a single clap."""
        print("Single clap detected!")
        self.speak("Hello! How can I assist you today?")

    def handle_double_clap(self):
        """Respond to a double clap."""
        print("Double clap detected!")
        self.speak("Hey sir, I'm here to help you out")

    def main(self, page: ft.Page):
        self.page = page  # Save the page reference
        page.title = "Artifix"
        page.theme_mode = ft.ThemeMode.LIGHT
        page.bgcolor = "#1a1a1a"
        page.padding = 0
        page.spacing = 0
        
        # Header configuration
        header = ft.Container(
            content=ft.Row(
                controls=[
                    ft.CircleAvatar(
                        content=ft.Text("A", size=20, weight=ft.FontWeight.BOLD),
                        color=ft.colors.WHITE,
                        bgcolor="#007AFF",
                        radius=20,
                    ),
                    ft.Text("Artifix", size=24, weight=ft.FontWeight.BOLD, color=ft.colors.WHITE),
                    ft.Container(
                        content=ft.Row(
                            controls=[
                                ft.Container(
                                    width=8,
                                    height=8,
                                    bgcolor="#4CAF50",
                                    border_radius=ft.border_radius.all(4),
                                ),
                                ft.Text("Online", color="#4CAF50", size=12),
                            ],
                            spacing=5,
                        ),
                        margin=ft.margin.only(left=10),
                    ),
                ],
                alignment=ft.MainAxisAlignment.START,
            ),
            padding=20,
            bgcolor="#2d2d2d",
        )

        # Chat container setup
        self.chat = ft.ListView(
            expand=True,
            spacing=15,
            padding=20,
            auto_scroll=True,
        )

        # Typing indicator setup
        self.typing_indicator = ft.Row(
            controls=[
                ft.Container(
                    content=ft.Row(
                        controls=[
                            ft.Container(
                                width=8,
                                height=8,
                                bgcolor="#007AFF",
                                border_radius=ft.border_radius.all(4),
                                animate=ft.animation.Animation(300, "bounceOut"),
                            ),
                            ft.Container(
                                width=8,
                                height=8,
                                bgcolor="#007AFF",
                                border_radius=ft.border_radius.all(4),
                                animate=ft.animation.Animation(300, "bounceOut"),
                                opacity=0.7,
                            ),
                            ft.Container(
                                width=8,
                                height=8,
                                bgcolor="#007AFF",
                                border_radius=ft.border_radius.all(4),
                                animate=ft.animation.Animation(300, "bounceOut"),
                                opacity=0.4,
                            ),
                        ],
                        spacing=5,
                    ),
                    visible=False,
                    padding=10,
                    bgcolor="#2d2d2d",
                    border_radius=ft.border_radius.all(20),
                )
            ],
        )

        # Input field setup
        self.input_field = ft.TextField(
            hint_text="Message Artifix...",
            border_radius=30,
            min_lines=1,
            max_lines=5,
            filled=True,
            expand=True,
            bgcolor="#2d2d2d",
            color=ft.colors.WHITE,
            cursor_color=ft.colors.WHITE,
            border_color=ft.colors.TRANSPARENT,
            hint_style=ft.TextStyle(color="#666666"),
            on_submit=self.send_message,
            text_size=16,
        )

        # Buttons configuration
        send_button = ft.IconButton(
            icon=ft.Icons.SEND_ROUNDED,
            icon_color="#007AFF",
            tooltip="Send message",
            on_click=self.send_message,
        )

        voice_button = ft.IconButton(
            icon=ft.Icons.MIC,
            icon_color="#007AFF",
            tooltip="Voice input",
            on_click=self.start_voice_input,
        )

        # Input container for buttons and text field
        input_container = ft.Container(
            content=ft.Row(
                controls=[
                    voice_button,
                    self.input_field,
                    send_button,
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            ),
            padding=ft.padding.only(left=20, right=20, bottom=20, top=10),
            bgcolor="#1a1a1a",
        )

        # Add components to the page
        page.add(
            header,
            ft.Container(
                content=self.chat,
                expand=True,
                bgcolor="#1a1a1a",
            ),
            self.typing_indicator,
            input_container,
        )

        # Welcome message
        self.add_message("Hello! I'm Artifix, your AI assistant. How can I help you today?", False)

    def add_message(self, message: str, is_user: bool):
        """Add a message to the chat."""
        self.chat.controls.append(
            ft.Row(
                controls=[
                    ft.Container(
                        content=ft.Column(
                            controls=[
                                ft.Text(
                                    "You" if is_user else "Artifix",
                                    size=12,
                                    color="#666666",
                                    weight=ft.FontWeight.BOLD,
                                ),
                                ft.Text(
                                    message,
                                    size=16,
                                    color="#ffffff" if is_user else "#000000",
                                    selectable=True,
                                ),
                                ft.Text(
                                    time.strftime("%H:%M"),
                                    size=10,
                                    color="#666666",
                                ),
                            ],
                            spacing=5,
                        ),
                        bgcolor="#007AFF" if is_user else "#e4e4e4",
                        padding=15,
                        border_radius=ft.border_radius.all(20),
                        margin=ft.margin.only(
                            left=50 if is_user else 0,
                            right=0 if is_user else 50,
                        ),
                        width=self.page.width * 0.5,  # Set width to 50% of page width
                    )
                ],
                alignment=ft.MainAxisAlignment.END if is_user else ft.MainAxisAlignment.START,
            )
        )
        self.chat.update()

    def show_typing_indicator(self, show: bool):
        """Control visibility of typing indicator."""
        self.typing_indicator.controls[0].visible = show
        self.typing_indicator.update()

    def speak(self, text: str):
        """Speak the provided text, silently reinitializing the engine if it fails."""
        if self.speech_lock.acquire(blocking=False):
            try:
                # If the engine is not initialized or not working, reinitialize it
                if not self.engine or not hasattr(self.engine, 'say'):
                    self.setup_speech_engine()

                # Speak the text
                self.engine.say(text)
                self.engine.runAndWait()
            except Exception as e:
                print(f"Speech error: {e}")
                try:
                    # Reinitialize engine if it fails
                    self.setup_speech_engine()
                    self.engine.say(text)
                    self.engine.runAndWait()
                except Exception as inner_exception:
                    print(f"Reinitialization failed: {inner_exception}")
            finally:
                self.speech_lock.release()

    def process_bot_response(self, user_message: str):
        """Process response from the bot."""
        self.show_typing_indicator(True)
        try:
            response = query_handle.handle(user_message.lower())
            time.sleep(0.5)
            self.show_typing_indicator(False)
            self.add_message(response, False)
            threading.Thread(target=self.speak, args=(response,), daemon=True).start()
        except Exception as e:
            self.show_typing_indicator(False)
            self.add_message(f"Sorry, I encountered an error: {str(e)}", False)

    def send_message(self, e):
        """Send user message."""
        user_message = self.input_field.value
        if not user_message:
            return
        
        self.input_field.value = ""
        self.input_field.update()
        self.add_message(user_message, True)
        threading.Thread(target=self.process_bot_response, args=(user_message,), daemon=True).start()

    def start_voice_input(self, e):
        """Start voice input."""
        def voice_input_thread():
            with sr.Microphone() as source:
                self.add_message("Listening...", False)
                try:
                    audio = self.recognizer.listen(source, timeout=5)
                    text = self.recognizer.recognize_google(audio)
                    self.add_message(text, True)
                    self.process_bot_response(text)
                except sr.WaitTimeoutError:
                    self.add_message("No speech detected", False)
                except sr.UnknownValueError:
                    self.add_message("Could not understand audio", False)
                except Exception as ex:
                    self.add_message(f"Error: {str(ex)}", False)

        threading.Thread(target=voice_input_thread, daemon=True).start()

def main():
    app = ChatApp()
    ft.app(target=app.main)

if __name__ == "__main__":
    main()
