try:
    import flet as ft
except ImportError:
    from core.mock_deps import ft
import time
from core.audio_visualizer import AudioVisualizationManager

class UI:
    def __init__(self, on_send, on_voice):
        self.on_send = on_send
        self.on_voice = on_voice
        self.page = None
        self.chat = None
        self.input = None
        self.typing = None
        
        # Initialize audio visualization
        self.audio_viz_manager = AudioVisualizationManager()
        self.status_text = None

    def build(self, page):
        self.page = page
        page.title = "Artifix"
        page.theme_mode = ft.ThemeMode.LIGHT
        page.bgcolor = "#1a1a1a"
        page.padding = 0
        page.spacing = 0

        self.chat = ft.ListView(expand=True, spacing=15, padding=20, auto_scroll=True)

        self.typing = ft.Row(
            controls=[
                ft.Container(
                    content=ft.Row(
                        controls=[
                            ft.Container(width=8, height=8, bgcolor="#007AFF", border_radius=ft.border_radius.all(4), animate=ft.animation.Animation(300, "bounceOut")),
                            ft.Container(width=8, height=8, bgcolor="#007AFF", border_radius=ft.border_radius.all(4), animate=ft.animation.Animation(300, "bounceOut"), opacity=0.7),
                            ft.Container(width=8, height=8, bgcolor="#007AFF", border_radius=ft.border_radius.all(4), animate=ft.animation.Animation(300, "bounceOut"), opacity=0.4),
                        ],
                        spacing=5,
                    ),
                    visible=False,
                    padding=10,
                    bgcolor="#2d2d2d",
                    border_radius=ft.border_radius.all(20),
                )
            ]
        )

        self.input = ft.TextField(
            hint_text="Voice-only mode: Use microphone or double clap to speak",
            border_radius=30,
            min_lines=1,
            max_lines=3,
            filled=True,
            expand=True,
            bgcolor="#2d2d2d",
            color="#666666",
            cursor_color=ft.colors.TRANSPARENT,
            border_color=ft.colors.TRANSPARENT,
            hint_style=ft.TextStyle(color="#666666"),
            text_size=14,
            read_only=True,  # Make it read-only since we're removing text input
        )

        # Voice button - now the primary interaction method
        mic_btn = ft.IconButton(
            icon=ft.Icons.MIC, 
            icon_color="#007AFF", 
            tooltip="Click to speak or double clap", 
            on_click=self.on_voice,
            icon_size=30
        )
        
        # Status text for showing current mode
        self.status_text = ft.Text(
            "Ready - Say 'Hey Artifix' or double clap to start",
            size=14,
            color="#666666",
            text_align=ft.TextAlign.CENTER
        )

        # Audio visualization widget
        audio_viz_widget = self.audio_viz_manager.get_visualization_widget()

        # Create voice control container (replacing input container)
        voice_container = ft.Container(
            content=ft.Column([
                audio_viz_widget,
                ft.Row([
                    ft.Container(expand=True),  # Spacer
                    mic_btn,
                    ft.Container(expand=True),  # Spacer
                ], alignment=ft.MainAxisAlignment.CENTER),
                self.status_text
            ], spacing=10, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            padding=ft.padding.only(left=20, right=20, bottom=20, top=10),
            bgcolor="#1a1a1a",
        )

        header = ft.Container(
            content=ft.Row([
                ft.CircleAvatar(content=ft.Text("A", size=20, weight=ft.FontWeight.BOLD), color=ft.colors.WHITE, bgcolor="#007AFF", radius=20),
                ft.Text("Artifix - Voice Assistant", size=24, weight=ft.FontWeight.BOLD, color=ft.colors.WHITE),
                ft.Container(content=ft.Row([
                    ft.Container(width=8, height=8, bgcolor="#4CAF50", border_radius=ft.border_radius.all(4)),
                    ft.Text("Voice Mode", color="#4CAF50", size=12)
                ], spacing=5), margin=ft.margin.only(left=10)),
            ], alignment=ft.MainAxisAlignment.START),
            padding=20,
            bgcolor="#2d2d2d"
        )

        page.add(
            header,
            ft.Container(content=self.chat, expand=True, bgcolor="#1a1a1a"),
            self.typing,
            voice_container  # Changed from input_container
        )

    def add_message(self, message, is_user):
        self.chat.controls.append(
            ft.Row(
                controls=[
                    ft.Container(
                        content=ft.Column(
                            controls=[
                                ft.Text("You" if is_user else "Artifix", size=12, color="#666666"),
                                ft.Text(message, size=16, color="#ffffff" if is_user else "#000000", selectable=True),
                                ft.Text(time.strftime("%H:%M"), size=10, color="#666666")
                            ],
                            spacing=5
                        ),
                        bgcolor="#007AFF" if is_user else "#e4e4e4",
                        padding=15,
                        border_radius=ft.border_radius.all(20),
                        margin=ft.margin.only(left=50 if is_user else 0, right=0 if is_user else 50),
                        width=self.page.width * 0.5
                    )
                ],
                alignment=ft.MainAxisAlignment.END if is_user else ft.MainAxisAlignment.START
            )
        )
        self.chat.update()

    def show_typing(self, show):
        self.typing.controls[0].visible = show
        self.typing.update()

    def get_input(self):
        return self.input.value.strip()

    def clear_input(self):
        # No longer needed since we removed text input, but keeping for compatibility
        pass
    
    def start_listening_visualization(self):
        """Start the audio visualization for listening mode"""
        self.audio_viz_manager.start_listening_visualization()
        if self.status_text:
            self.status_text.value = "Listening... Speak now"
            self.status_text.update()
    
    def stop_listening_visualization(self):
        """Stop the audio visualization"""
        self.audio_viz_manager.stop_listening_visualization()
        if self.status_text:
            self.status_text.value = "Ready - Say 'Hey Artifix' or double clap to start"
            self.status_text.update()
    
    def show_response_pulse(self):
        """Show a visual pulse when AI is responding"""
        self.audio_viz_manager.show_response_pulse()
    
    def update_status(self, message):
        """Update the status text"""
        if self.status_text:
            self.status_text.value = message
            self.status_text.update()