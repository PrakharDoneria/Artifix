import flet as ft
from core.app import ChatApp

def main():
    app = ChatApp()
    ft.app(target=app.main)

if __name__ == "__main__":
    main()