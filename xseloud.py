import os
import sys
import customtkinter as ctk
from gui.main_window import XseloudTool

def main():
    # Инициализация customtkinter
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")
    
    app = XseloudTool()
    app.protocol("WM_DELETE_WINDOW", app.on_closing)
    app.mainloop()

if __name__ == "__main__":
    main() 