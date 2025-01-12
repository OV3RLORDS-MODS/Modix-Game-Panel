import tkinter as tk
from tkinter import messagebox
import subprocess
import os
from mod_manager_text_editor import TextEditor

def open_edit_dialog(parent, file_path):
    """Open a dialog to choose between GSM Editor and default application."""
    edit_dialog = tk.Toplevel(parent)
    edit_dialog.title("Choose Editor")
    edit_dialog.geometry("300x150")
    edit_dialog.configure(bg="#1E1E1E")

    tk.Label(edit_dialog, text="Choose an editor to open the file:", bg="#1E1E1E", fg="#00FF00", font=("Consolas", 12)).pack(pady=10)

    def use_gsm_editor():
        # Open the text editor for the file
        TextEditor(parent, file_path)
        edit_dialog.destroy()

    def use_default_application():
        if os.name == 'nt':  # Windows
            os.startfile(file_path)
        elif os.name == 'posix':  # macOS and Linux
            subprocess.call(['xdg-open', file_path])
        edit_dialog.destroy()

    tk.Button(edit_dialog, text="Use GSM Editor", command=use_gsm_editor, bg="#2E2E2E", fg="#00FF00", font=("Consolas", 12), relief="flat", cursor="hand2").pack(pady=5)
    tk.Button(edit_dialog, text="Use Your Editor", command=use_default_application, bg="#2E2E2E", fg="#00FF00", font=("Consolas", 12), relief="flat", cursor="hand2").pack(pady=5)