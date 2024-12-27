# main.py
import flet as ft
import time
import threading
import pyttsx3
import speech_recognition as sr
import psutil
import datetime

class ArtifixChat:
    def __init__(self):
        self.engine = None
        self.speech_lock = threading.Lock()
        self.setup_speech_engine()
        self.recognizer = sr.Recognizer()
        
    def setup_speech_engine(self):
        """Initialize the speech synthesis engine with retries."""
        try:
            self.engine = pyttsx3.init()
            voices = self.engine.getProperty('voices')
            # Try to set a male voice for Artifix
            for voice in voices:
                if "male" in voice.name.lower():
                    self.engine.setProperty('voice', voice.id)
                    break
            else:
                self.engine.setProperty('voice', voices[0].id)
            
            self.engine.setProperty('rate', 175)
            self.engine.setProperty('volume', 1.0)
            
            # Test speech
            self.engine.say("System initialized")
            self.engine.runAndWait()
            
        except Exception as e:
            print(f"Speech engine initialization error: {e}")
            # Retry after delay if initialization fails
            time.sleep(2)
            self.setup_speech_engine()

    def create_status_indicator(self, size: float = 10):
        return ft.Container(
            width=size,
            height=size,
            border_radius=size/2,
            bgcolor="#007AFF",
            animate=ft.animation.Animation(1000, "linear"),
            animate_opacity=ft.animation.Animation(1000, "linear"),
            opacity=1,
        )

    def get_system_time(self):
        return datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S")
    
    def create_system_details(self):
        try:
            battery = psutil.sensors_battery()
            if battery:
                battery_percent = battery.percent
                battery_status = "Charging" if battery.power_plugged else "Discharging"
                system_details = f"Battery: {battery_percent}% ({battery_status})"
            else:
                system_details = "Battery: N/A"
                
            cpu_percent = psutil.cpu_percent()
            memory = psutil.virtual_memory()
            system_details += f" | CPU: {cpu_percent}% | RAM: {memory.percent}%"
            
            return ft.Container(
                content=ft.Text(system_details, size=12, color="#007AFF"),
                padding=8,
                bgcolor="#007AFF22",
                border_radius=5,
            )
        except Exception as e:
            print(f"Error getting system details: {e}")
            return ft.Container(
                content=ft.Text("System Info Unavailable", size=12, color="#007AFF"),
                padding=8,
                bgcolor="#007AFF22",
                border_radius=5,
            )

    def main(self, page: ft.Page):
        page.title = "Artifix"
        page.theme_mode = ft.ThemeMode.DARK
        page.bgcolor = "#000716"
        page.padding = 0
        page.spacing = 0
        
        # Create animated status indicator
        self.status_indicator = self.create_status_indicator()
        
        def animate_status():
            while True:
                self.status_indicator.opacity = 0.3
                self.status_indicator.update()
                time.sleep(1)
                self.status_indicator.opacity = 1
                self.status_indicator.update()
                time.sleep(1)
        
        # System info containers
        system_info = ft.Container(
            content=self.create_system_details(),
            padding=8,
            bgcolor="#007AFF22",
            border_radius=5,
        )

        time_display = ft.Container(
            content=ft.Text(self.get_system_time(), color="#007AFF", size=12),
            padding=8,
            bgcolor="#007AFF22",
            border_radius=5,
        )

        def update_system_info():
            while True:
                try:
                    system_info.content = self.create_system_details()
                    time_display.content = ft.Text(self.get_system_time(), color="#007AFF", size=12)
                    system_info.update()
                    time_display.update()
                except Exception as e:
                    print(f"Error updating system info: {e}")
                time.sleep(1)

        # Start background threads
        threading.Thread(target=animate_status, daemon=True).start()
        threading.Thread(target=update_system_info, daemon=True).start()

        # Header
        header = ft.Container(
            content=ft.Row([
                ft.Row([
                    self.status_indicator,
                    ft.Text(
                        "Artifix INTERFACE",
                        size=24,
                        weight=ft.FontWeight.BOLD,
                        color="#007AFF",
                    ),
                ], spacing=15),
                ft.Row([
                    ft.Container(
                        bgcolor="#007AFF22",
                        border_radius=5,
                        padding=8,
                        content=ft.Text("SYSTEM ACTIVE", color="#007AFF", size=12),
                    ),
                    time_display,
                    system_info,
                ], spacing=10),
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            padding=20,
            bgcolor="#001429",
        )

        # Chat area
        self.chat = ft.ListView(
            expand=True,
            spacing=15,
            padding=20,
            auto_scroll=True,
        )

        # Typing indicator
        self.typing_indicator = ft.Row([
            ft.Container(
                content=ft.Row([
                    *[ft.Container(
                        width=4,
                        height=4,
                        bgcolor="#007AFF",
                        border_radius=2,
                        animate_opacity=ft.animation.Animation(300, "easeInOut"),
                        opacity=0.3,
                    ) for _ in range(3)],
                ], spacing=5),
                visible=False,
                padding=10,
                bgcolor="#001429",
                border_radius=20,
            )
        ])

        # Input field
        self.input_field = ft.TextField(
            hint_text="Enter command...",
            border_radius=25,
            min_lines=1,
            max_lines=5,
            filled=True,
            expand=True,
            bgcolor="#001429",
            color="#007AFF",
            cursor_color="#007AFF",
            border_color="#007AFF22",
            hint_style=ft.TextStyle(color="#007AFF66"),
            on_submit=self.send_message,
            text_size=14,
        )

        # Action buttons
        send_button = ft.IconButton(
            icon=ft.icons.SEND_ROUNDED,
            icon_color="#007AFF",
            tooltip="Send message",
            on_click=self.send_message,
        )

        voice_button = ft.IconButton(
            icon=ft.icons.MIC,
            icon_color="#007AFF",
            tooltip="Voice command",
            on_click=self.start_voice_input,
        )

        # Input container
        input_container = ft.Container(
            content=ft.Row([
                voice_button,
                self.input_field,
                send_button,
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            padding=ft.padding.only(left=15, right=15, bottom=15, top=10),
            bgcolor="#000716",
            border=ft.border.all(1, "#007AFF33"),
            border_radius=30,
        )

        # Add elements to page
        page.add(
            header,
            ft.Container(
                content=self.chat,
                expand=True,
                bgcolor="#000716",
            ),
            self.typing_indicator,
            input_container,
        )

        # Welcome message
        self.add_message(
            "Initializing Artifix interface... Welcome, sir. How may I assist you today?",
            False
        )

    def add_message(self, message: str, is_user: bool):
        message_container = ft.Container(
            content=ft.Column([
                ft.Text(
                    "USER" if is_user else "Artifix",
                    size=10,
                    color="#007AFF",
                    weight=ft.FontWeight.BOLD,
                ),
                ft.Text(
                    message,
                    size=14,
                    color="#FFFFFF",
                    selectable=True,
                    no_wrap=False,
                    max_lines=None,
                ),
                ft.Text(
                    self.get_system_time(),
                    size=9,
                    color="#007AFF88",
                ),
            ], spacing=5),
            bgcolor="#001429",
            padding=15,
            border_radius=15,
            border=ft.border.all(1, "#007AFF33"),
            margin=ft.margin.only(
                left=50 if is_user else 0,
                right=0 if is_user else 50,
            ),
            width=400,  # Fixed width for better control
            animate_opacity=ft.animation.Animation(500, "easeOutCubic"),
            opacity=0,
        )
        
        self.chat.controls.append(
            ft.Row([message_container],
                alignment=ft.MainAxisAlignment.END if is_user else ft.MainAxisAlignment.START,
            )
        )
        message_container.opacity = 1
        self.chat.update()

    def show_typing_indicator(self, show: bool):
        for i, dot in enumerate(self.typing_indicator.controls[0].content.controls):
            dot.opacity = 0.3 + (i * 0.2) if show else 0.3
        self.typing_indicator.controls[0].visible = show
        self.typing_indicator.update()

    def speak(self, text: str):
        def speech_task():
            if self.speech_lock.acquire(blocking=False):
                try:
                    if not self.engine:
                        self.setup_speech_engine()
                    self.engine.say(text)
                    self.engine.runAndWait()
                except Exception as e:
                    print(f"Speech error: {e}")
                    self.setup_speech_engine()
                finally:
                    self.speech_lock.release()

        threading.Thread(target=speech_task, daemon=True).start()

    def handle_message(self, message: str) -> str:
        """Process user messages and return appropriate responses."""
        message = message.lower().strip()
        
        # Basic responses
        if "hello" in message or "hi" in message:
            return "Hello! How can I assist you today?"
        elif "how are you" in message:
            return "I'm functioning optimally. Thank you for asking. How may I help you?"
        elif "goodbye" in message or "bye" in message:
            return "Goodbye! Feel free to return if you need assistance."
        elif "time" in message:
            return f"The current time is {self.get_system_time()}"
        elif "battery" in message:
            battery = psutil.sensors_battery()
            if battery:
                return f"Battery is at {battery.percent}% and {'charging' if battery.power_plugged else 'discharging'}."
            return "Battery information is not available."
        elif "system" in message:
            cpu = psutil.cpu_percent()
            memory = psutil.virtual_memory()
            return f"System Status:\nCPU Usage: {cpu}%\nMemory Usage: {memory.percent}%"
        else:
            return "I'm not sure how to respond to that. Could you please rephrase or ask something else?"

    def process_bot_response(self, user_message: str):
        self.show_typing_indicator(True)
        try:
            response = self.handle_message(user_message)
            time.sleep(0.5)  # Simulate processing time
            self.show_typing_indicator(False)
            self.add_message(response, False)
            self.speak(response)
        except Exception as e:
            self.show_typing_indicator(False)
            error_msg = f"System error detected: {str(e)}"
            self.add_message(error_msg, False)
            self.speak("I encountered an error processing your request")

    def send_message(self, e):
        user_message = self.input_field.value
        if not user_message:
            return
        
        self.input_field.value = ""
        self.input_field.update()
        self.add_message(user_message, True)
        threading.Thread(target=self.process_bot_response, args=(user_message,), daemon=True).start()

    def start_voice_input(self, e):
        def voice_input_thread():
            with sr.Microphone() as source:
                self.add_message("Voice recognition activated. Awaiting input...", False)
                try:
                    audio = self.recognizer.listen(source, timeout=5)
                    text = self.recognizer.recognize_google(audio)
                    self.add_message(text, True)
                    self.process_bot_response(text)
                except sr.WaitTimeoutError:
                    self.add_message("Voice input timeout. Please try again.", False)
                except sr.UnknownValueError:
                    self.add_message("Voice command not recognized. Please try again.", False)
                except Exception as ex:
                    self.add_message(f"System error in voice recognition: {str(ex)}", False)

        threading.Thread(target=voice_input_thread, daemon=True).start()

def main():
    app = ArtifixChat()
    ft.app(target=app.main)

if __name__ == "__main__":
    main()