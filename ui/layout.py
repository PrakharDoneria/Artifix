import flet as ft
import time

class UI:
    def __init__(self, on_send, on_voice):
        self.on_send = on_send
        self.on_voice = on_voice
        self.page = None
        self.chat = None
        self.input = None
        self.typing = None

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
            on_submit=self.on_send,
            text_size=16,
        )

        send_btn = ft.IconButton(icon=ft.Icons.SEND_ROUNDED, icon_color="#007AFF", tooltip="Send", on_click=self.on_send)
        mic_btn = ft.IconButton(icon=ft.Icons.MIC, icon_color="#007AFF", tooltip="Speak", on_click=self.on_voice)

        input_container = ft.Container(
            content=ft.Row([mic_btn, self.input, send_btn], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            padding=ft.padding.only(left=20, right=20, bottom=20, top=10),
            bgcolor="#1a1a1a",
        )

        header = ft.Container(
            content=ft.Row([
                ft.CircleAvatar(content=ft.Text("A", size=20, weight=ft.FontWeight.BOLD), color=ft.colors.WHITE, bgcolor="#007AFF", radius=20),
                ft.Text("Artifix", size=24, weight=ft.FontWeight.BOLD, color=ft.colors.WHITE),
                ft.Container(content=ft.Row([
                    ft.Container(width=8, height=8, bgcolor="#4CAF50", border_radius=ft.border_radius.all(4)),
                    ft.Text("Online", color="#4CAF50", size=12)
                ], spacing=5), margin=ft.margin.only(left=10)),
            ], alignment=ft.MainAxisAlignment.START),
            padding=20,
            bgcolor="#2d2d2d"
        )

        page.add(
            header,
            ft.Container(content=self.chat, expand=True, bgcolor="#1a1a1a"),
            self.typing,
            input_container
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
        self.input.value = ""
        self.input.update()