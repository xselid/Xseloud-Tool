import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox, scrolledtext
import threading
import os
import sys
from PIL import Image, ImageTk
import queue
import time

# Добавляем путь к корневой директории проекта
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.system_utils import (
    is_admin, run_as_admin, disable_uac, unlock_policies,
    enable_windows_features, clear_temp_files, optimize_system,
    show_system_info, repair_system, disable_windows_defender,
    optimize_network, disable_telemetry, optimize_gaming
)

class ConsoleRedirector:
    def __init__(self, text_widget):
        self.text_widget = text_widget
        self.queue = queue.Queue()
        self.running = True
        self.update_thread = threading.Thread(target=self._update_text)
        self.update_thread.daemon = True
        self.update_thread.start()

    def write(self, string):
        self.queue.put(string)

    def flush(self):
        pass

    def _update_text(self):
        while self.running:
            try:
                text = self.queue.get_nowait()
                self.text_widget.configure(state="normal")
                self.text_widget.insert("end", text)
                self.text_widget.see("end")
                self.text_widget.configure(state="disabled")
            except queue.Empty:
                time.sleep(0.1)

    def stop(self):
        self.running = False
        self.update_thread.join()

class XseloudTool(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Настройка окна
        self.title("Xseloud Tool")
        self.geometry("1200x800")
        self.minsize(1200, 800)
        
        # Установка темы
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        # Создание основного контейнера
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Создание фрейма для контента
        self.content_frame = ctk.CTkFrame(self, fg_color="#1a1a1a")
        self.content_frame.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")
        self.content_frame.grid_columnconfigure(0, weight=1)
        self.content_frame.grid_rowconfigure(1, weight=1)

        # Заголовок
        self.title_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        self.title_frame.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="ew")
        self.title_frame.grid_columnconfigure(0, weight=1)

        # Логотип студии
        self.studio_label = ctk.CTkLabel(
            self.title_frame,
            text="XSELID CORE",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color="#b388ff"  # Светло-сиреневый
        )
        self.studio_label.grid(row=0, column=0, padx=20, pady=(20, 5))

        # Название приложения
        self.title_label = ctk.CTkLabel(
            self.title_frame,
            text="XSELOUD TOOL",
            font=ctk.CTkFont(size=36, weight="bold"),
            text_color="#7c4dff"  # Яркий сиреневый
        )
        self.title_label.grid(row=1, column=0, padx=20, pady=(5, 5))

        self.subtitle_label = ctk.CTkLabel(
            self.title_frame,
            text="Системный инструмент для оптимизации Windows",
            font=ctk.CTkFont(size=14),
            text_color="#9575cd"  # Средний сиреневый
        )
        self.subtitle_label.grid(row=2, column=0, padx=20, pady=(0, 20))

        # Создание фрейма для кнопок
        self.buttons_frame = ctk.CTkFrame(self.content_frame, fg_color="#1a1a1a")
        self.buttons_frame.grid(row=1, column=0, padx=20, pady=10, sticky="nsew")
        self.buttons_frame.grid_columnconfigure((0, 1, 2), weight=1)
        self.buttons_frame.grid_rowconfigure((0, 1, 2, 3), weight=1)

        # Создание кнопок
        self.create_buttons()

        # Консоль вывода
        self.console_frame = ctk.CTkFrame(self.content_frame, fg_color="#1a1a1a")
        self.console_frame.grid(row=2, column=0, padx=20, pady=(10, 20), sticky="nsew")
        self.console_frame.grid_columnconfigure(0, weight=1)
        self.console_frame.grid_rowconfigure(0, weight=1)

        self.console_label = ctk.CTkLabel(
            self.console_frame,
            text="Консоль вывода",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#b388ff"  # Светло-сиреневый
        )
        self.console_label.grid(row=0, column=0, padx=10, pady=(10, 5), sticky="w")

        self.console = scrolledtext.ScrolledText(
            self.console_frame,
            wrap=tk.WORD,
            width=100,
            height=10,
            bg="#2d2d2d",
            fg="#e1bee7",  # Светло-сиреневый для текста
            font=("Consolas", 10),
            insertbackground="#b388ff"  # Светло-сиреневый для курсора
        )
        self.console.grid(row=1, column=0, padx=10, pady=(0, 10), sticky="nsew")
        self.console.configure(state="disabled")

        # Перенаправление вывода консоли
        self.console_redirector = ConsoleRedirector(self.console)
        sys.stdout = self.console_redirector
        sys.stderr = self.console_redirector

        # Статус бар
        self.status_bar = ctk.CTkLabel(
            self.content_frame,
            text="Готов к работе",
            font=ctk.CTkFont(size=12),
            text_color="#9575cd"  # Средний сиреневый
        )
        self.status_bar.grid(row=3, column=0, padx=20, pady=(0, 10), sticky="w")

        # Прогресс бар (изначально скрыт)
        self.progress_bar = ctk.CTkProgressBar(self.content_frame)
        self.progress_bar.grid(row=4, column=0, padx=20, pady=(0, 20), sticky="ew")
        self.progress_bar.grid_remove()
        self.progress_bar.set(0)

        # Копирайт
        self.copyright_label = ctk.CTkLabel(
            self.content_frame,
            text="© 2024 Xselid Core. Все права защищены.",
            font=ctk.CTkFont(size=10),
            text_color="#9575cd"  # Средний сиреневый
        )
        self.copyright_label.grid(row=5, column=0, padx=20, pady=(0, 10), sticky="e")

        # Проверка прав администратора
        if not is_admin():
            self.show_admin_warning()

    def create_buttons(self):
        # Создание кнопок с иконками и описаниями
        buttons_data = [
            ("Отключить UAC", self.disable_uac),
            ("Разблокировать ограничения", self.unlock_policies),
            ("Включить функции Windows", self.enable_windows_features),
            ("Очистить временные файлы", self.clear_temp_files),
            ("Оптимизировать систему", self.optimize_system),
            ("Информация о системе", self.show_system_info),
            ("Восстановить систему", self.repair_system),
            ("Отключить Windows Defender", self.disable_windows_defender),
            ("Оптимизировать сеть", self.optimize_network),
            ("Отключить телеметрию", self.disable_telemetry),
            ("Оптимизация для игр", self.optimize_gaming),
            ("Выход", self.quit)
        ]

        for i, (text, command) in enumerate(buttons_data):
            row = i // 3
            col = i % 3
            
            button = ctk.CTkButton(
                self.buttons_frame,
                text=text,
                command=command,
                height=40,
                font=ctk.CTkFont(size=14, weight="bold"),
                fg_color="#2d2d2d",
                hover_color="#7c4dff",  # Яркий сиреневый при наведении
                border_width=1,
                border_color="#b388ff"  # Светло-сиреневый для границы
            )
            button.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")

    def show_progress(self, show=True):
        if show:
            self.progress_bar.grid()
            self.progress_bar.set(0)
        else:
            self.progress_bar.grid_remove()

    def update_status(self, message):
        self.status_bar.configure(text=message)
        self.update()

    def run_with_progress(self, func, *args):
        self.show_progress(True)
        self.update_status("Выполняется...")
        
        def run():
            try:
                print(f"\n[{time.strftime('%H:%M:%S')}] Запуск операции: {func.__name__}")
                success, message = func(*args)
                print(f"[{time.strftime('%H:%M:%S')}] Операция завершена")
                self.after(0, lambda: self.show_result(success, message))
            except Exception as e:
                print(f"[{time.strftime('%H:%M:%S')}] Ошибка: {str(e)}")
                self.after(0, lambda: self.show_result(False, str(e)))
            finally:
                self.after(0, lambda: self.show_progress(False))
                self.after(0, lambda: self.update_status("Готов к работе"))
        
        threading.Thread(target=run, daemon=True).start()

    def show_result(self, success, message):
        if success:
            if isinstance(message, list):
                message = "\n".join(message)
            messagebox.showinfo("Успех", message)
        else:
            messagebox.showerror("Ошибка", message)

    def show_admin_warning(self):
        if messagebox.askyesno(
            "Требуются права администратора",
            "Для корректной работы программы требуются права администратора.\nПерезапустить программу с правами администратора?"
        ):
            run_as_admin()
            self.quit()

    def on_closing(self):
        self.console_redirector.stop()
        self.quit()

    # Обработчики кнопок
    def disable_uac(self):
        self.run_with_progress(disable_uac)

    def unlock_policies(self):
        self.run_with_progress(unlock_policies)

    def enable_windows_features(self):
        self.run_with_progress(enable_windows_features)

    def clear_temp_files(self):
        self.run_with_progress(clear_temp_files)

    def optimize_system(self):
        self.run_with_progress(optimize_system)

    def show_system_info(self):
        self.run_with_progress(show_system_info)

    def repair_system(self):
        self.run_with_progress(repair_system)

    def disable_windows_defender(self):
        self.run_with_progress(disable_windows_defender)

    def optimize_network(self):
        self.run_with_progress(optimize_network)

    def disable_telemetry(self):
        self.run_with_progress(disable_telemetry)

    def optimize_gaming(self):
        self.run_with_progress(optimize_gaming) 