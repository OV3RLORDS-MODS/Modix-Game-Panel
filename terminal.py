import tkinter as tk
import tkinter.simpledialog as simpledialog
from tkinter import filedialog, messagebox
import subprocess
import psutil
import json
import os
import configparser
from datetime import datetime

# 1) Import your custom TextEditor class from the file that contains it.
#    E.g. if your mod_manager_text_editor.py is in the same folder:
from mod_manager_text_editor import TextEditor

class Terminal(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.setup_initial_state()
        self.create_widgets()

        # Deferred loading of last config (batch file & RCON)
        self.after(100, self.load_last_config)

    def setup_initial_state(self):
        # --------------- SERVER BATCH STATE ---------------
        self.batch_file_path = None
        self.process = None
        self.running = False

        # --------------- RCON STATE ---------------
        self.rcon_ip = tk.StringVar(value="")
        self.rcon_port = tk.StringVar(value="")
        self.rcon_password = tk.StringVar(value="")
        self.rcon_status = tk.StringVar(value="Disconnected")

        # --------------- SERVER INFO ---------------
        self.server_info = {
            "IP": "N/A",
            "Port": "N/A",
            "Player Slots": "N/A",
            "CPU Usage": "N/A",
            "Memory Usage": "N/A",
            "Last Crash": "N/A",
            "Last Closed": "N/A",
            "Last Restart": "N/A"
        }
        self.server_info_labels = {}

        # --------------- INI EDITOR STATE ---------------
        # (If you no longer need built-in INI logic, you can remove these.)
        self.ini_path = None
        self.ini_data = configparser.ConfigParser()
        self.ini_entries = {}  # dict of {key: tk.StringVar for the value}

        # --------------- COLORS & STYLES ---------------
        self.text_color = '#FFFFFF'
        self.bg_color = '#1E1E2E'
        self.card_bg = '#2B2B3B'

    def create_widgets(self):
        # ================= TOP HEADER =================
        header_frame = tk.Frame(self, bg=self.bg_color)
        header_frame.pack(side=tk.TOP, pady=10, fill=tk.X)

        # --- Buttons for batch management ---
        button_frame = tk.Frame(header_frame, bg=self.bg_color)
        button_frame.pack(side=tk.TOP, fill=tk.X)

        self.select_button = tk.Button(
            button_frame, text="Select Batch File", command=self.select_batch_file,
            bg='#2E2E2E', fg=self.text_color, font=('Consolas', 12),
            relief='flat', cursor='hand2'
        )
        self.select_button.grid(row=0, column=0, padx=5)

        self.start_button = tk.Button(
            button_frame, text="Start Server", command=self.start_server,
            bg='#2E2E2E', fg=self.text_color, font=('Consolas', 12),
            relief='flat', cursor='hand2', state=tk.DISABLED
        )
        self.start_button.grid(row=0, column=1, padx=5)

        self.restart_button = tk.Button(
            button_frame, text="Restart Server", command=self.restart_server,
            bg='#2E2E2E', fg=self.text_color, font=('Consolas', 12),
            relief='flat', cursor='hand2', state=tk.DISABLED
        )
        self.restart_button.grid(row=0, column=2, padx=5)

        self.stop_button = tk.Button(
            button_frame, text="Stop Server", command=self.stop_server,
            bg='#2E2E2E', fg=self.text_color, font=('Consolas', 12),
            relief='flat', cursor='hand2', state=tk.DISABLED
        )
        self.stop_button.grid(row=0, column=3, padx=5)

        # 2) Updated "Select .ini" button → opens TextEditor
        self.select_ini_button = tk.Button(
            button_frame, text="Select .ini", command=self.select_ini_file,
            bg='#2E2E2E', fg=self.text_color, font=('Consolas', 12),
            relief='flat', cursor='hand2'
        )
        self.select_ini_button.grid(row=0, column=4, padx=5)

        # ================= MAIN CONTENT =================
        main_content_frame = tk.Frame(self, bg=self.bg_color)
        main_content_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        # --------------- LEFT: CONSOLE ---------------
        self.console_frame = tk.Frame(main_content_frame, bg=self.bg_color)
        self.console_frame.pack(side=tk.LEFT, padx=10, pady=10, fill=tk.BOTH, expand=True)

        self.console_text = tk.Text(
            self.console_frame, height=20, wrap=tk.WORD,
            bg=self.bg_color, fg=self.text_color, font=('Consolas', 12),
            state=tk.DISABLED
        )
        self.console_text.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        # --------------- MIDDLE: INI EDITOR ---------------
        # If you no longer need the built-in INI logic or the middle frame,
        # you can safely remove these lines:
        self.ini_editor_frame = tk.Frame(main_content_frame, bg=self.card_bg)
        self.ini_editor_frame.pack(side=tk.LEFT, fill=tk.BOTH, padx=10, pady=10)

        # --------------- RIGHT: SERVER INFO + RCON ---------------
        right_frame = tk.Frame(main_content_frame, bg=self.bg_color)
        right_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=10, pady=10)

        # --- Server Info Cards ---
        server_info_keys = [
            "IP", "Port", "Player Slots", "CPU Usage", "Memory Usage",
            "Last Crash", "Last Closed", "Last Restart"
        ]
        for key in server_info_keys:
            card_frame = tk.Frame(right_frame, bg=self.card_bg,
                                  bd=0, highlightthickness=0)
            card_frame.pack(fill=tk.X, pady=6, padx=2)

            inner_frame = tk.Frame(card_frame, bg=self.card_bg)
            inner_frame.pack(fill=tk.X, padx=10, pady=5)

            key_label = tk.Label(
                inner_frame, text=f"{key}:", fg=self.text_color, bg=self.card_bg,
                font=('Consolas', 12, 'bold')
            )
            key_label.pack(side=tk.LEFT)

            value_label = tk.Label(
                inner_frame, text=self.server_info[key],
                fg=self.text_color, bg=self.card_bg, font=('Consolas', 12)
            )
            value_label.pack(side=tk.LEFT, padx=(8, 0))

            self.server_info_labels[key] = value_label

        # --------------- RCON STATUS CARD ---------------
        rcon_status_frame = tk.Frame(right_frame, bg=self.card_bg, bd=0, highlightthickness=0)
        rcon_status_frame.pack(fill=tk.X, pady=6, padx=2)

        status_inner_frame = tk.Frame(rcon_status_frame, bg=self.card_bg)
        status_inner_frame.pack(fill=tk.X, padx=10, pady=5)

        status_key_label = tk.Label(
            status_inner_frame, text="RCON Status:",
            fg=self.text_color, bg=self.card_bg,
            font=('Consolas', 12, 'bold')
        )
        status_key_label.pack(side=tk.LEFT)

        self.rcon_status_label = tk.Label(
            status_inner_frame, textvariable=self.rcon_status,
            fg=self.text_color, bg=self.card_bg,
            font=('Consolas', 12)
        )
        self.rcon_status_label.pack(side=tk.LEFT, padx=(8, 0))

        # ============== RCON Panel ==============
        rcon_title = tk.Label(
            right_frame, text="RCON Settings", fg=self.text_color,
            bg=self.bg_color, font=('Consolas', 14, 'bold', 'underline')
        )
        rcon_title.pack(anchor="w", pady=(10, 5))

        # IP
        tk.Label(
            right_frame, text="RCON IP:", fg=self.text_color,
            bg=self.bg_color, font=('Consolas', 12)
        ).pack(anchor="w")
        ip_entry = tk.Entry(right_frame, textvariable=self.rcon_ip, font=('Consolas', 12))
        ip_entry.pack(fill=tk.X, pady=2)

        # Port
        tk.Label(
            right_frame, text="RCON Port:", fg=self.text_color,
            bg=self.bg_color, font=('Consolas', 12)
        ).pack(anchor="w")
        port_entry = tk.Entry(right_frame, textvariable=self.rcon_port, font=('Consolas', 12))
        port_entry.pack(fill=tk.X, pady=2)

        # Password
        tk.Label(
            right_frame, text="Password:", fg=self.text_color,
            bg=self.bg_color, font=('Consolas', 12)
        ).pack(anchor="w")
        pass_entry = tk.Entry(right_frame, textvariable=self.rcon_password,
                              font=('Consolas', 12), show="*")
        pass_entry.pack(fill=tk.X, pady=2)

        connect_button = tk.Button(
            right_frame, text="Connect RCON", command=self.connect_rcon,
            bg='#2E2E2E', fg=self.text_color, font=('Consolas', 12),
            relief='flat', cursor='hand2'
        )
        connect_button.pack(pady=10, anchor="e")

    # -------------------------------------------------------------------
    # SELECTING THE .INI FILE → now opens the TextEditor
    # -------------------------------------------------------------------
    def select_ini_file(self):
        """
        Prompts user to pick an .ini file, then opens it in the custom TextEditor.
        """
        ini_path = filedialog.askopenfilename(
            filetypes=[("INI Files", "*.ini"), ("All Files", "*.*")],
            title="Select .ini File"
        )
        if not ini_path:
            return

        # Print path to console
        self.print_to_console(f"Selected .ini file: {ini_path}\n")

        # 3) Instead of parsing in code, open our custom text editor
        editor = TextEditor(self, ini_path)
        # Because it's a Toplevel, we don't call editor.mainloop() here;
        # the new window will appear, and we can continue using the main app.

    # -------------------------------------------------------------------
    # HELPER METHOD: Print to console
    # -------------------------------------------------------------------
    def print_to_console(self, text: str):
        self.console_text.config(state=tk.NORMAL)
        self.console_text.insert(tk.END, text)
        self.console_text.config(state=tk.DISABLED)
        self.console_text.yview(tk.END)

    # -------------------------------------------------------------------
    # BATCH FILE CONTROL
    # -------------------------------------------------------------------
    def select_batch_file(self):
        path = filedialog.askopenfilename(
            filetypes=[("Batch Files", "*.bat"), ("All Files", "*.*")]
        )
        if path:
            self.batch_file_path = path
            self.print_to_console(f"Selected batch file: {path}\n")
            self.start_button.config(state=tk.NORMAL)
            # Save so we remember
            self.save_config()

    def start_server(self):
        if not self.batch_file_path:
            messagebox.showwarning("Warning", "No batch file selected.")
            return

        if not self.running:
            try:
                self.process = subprocess.Popen(
                    [self.batch_file_path],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    stdin=subprocess.PIPE,
                    shell=True,
                    text=True,
                    bufsize=1
                )
                self.running = True
                self.print_to_console(f"Server started with PID {self.process.pid}.\n")

                self.start_button.config(state=tk.DISABLED)
                self.restart_button.config(state=tk.NORMAL)
                self.stop_button.config(state=tk.NORMAL)

                # Read batch file output
                self.after(100, self.read_batch_output)

            except Exception as e:
                messagebox.showerror("Error", f"Failed to start server:\n{e}")

    def read_batch_output(self):
        if self.process is None:
            return

        line = self.process.stdout.readline()
        if line:
            self.print_to_console(line)

        # If still running, schedule another read
        if self.process.poll() is None:
            self.after(100, self.read_batch_output)

    def restart_server(self):
        self.stop_server()
        self.start_server()

    def stop_server(self):
        if not self.running:
            return
        try:
            pid = self.process.pid
            self.print_to_console(f"Attempting to stop server with PID {pid}...\n")

            parent = psutil.Process(pid)
            for child in parent.children(recursive=True):
                self.print_to_console(f"Terminating child PID {child.pid}...\n")
                child.terminate()

            parent.terminate()
            try:
                parent.wait(timeout=10)
            except psutil.TimeoutExpired:
                self.print_to_console("Graceful termination failed. Killing process...\n")
                for child in parent.children(recursive=True):
                    child.kill()
                parent.kill()

            self.print_to_console("Server stopped.\n")

            self.running = False
            self.process = None

            self.start_button.config(state=tk.NORMAL)
            self.restart_button.config(state=tk.DISABLED)
            self.stop_button.config(state=tk.DISABLED)

        except Exception as e:
            self.print_to_console(f"Error stopping server:\n{e}\n")

    # -------------------------------------------------------------------
    # RCON (Stub)
    # -------------------------------------------------------------------
    def connect_rcon(self):
        ip = self.rcon_ip.get().strip()
        port = self.rcon_port.get().strip()
        password = self.rcon_password.get()

        if not ip or not port or not password:
            self.print_to_console("RCON info incomplete. Please fill out IP, Port, and Password.\n")
            # Set status to Disconnected
            self.rcon_status.set("Disconnected")
            return

        # Save config with updated RCON info
        self.save_config()

        # Here, you'd do real RCON logic. If successful:
        self.print_to_console(f"Attempting RCON connection at {ip}:{port}\n")
        self.print_to_console("(Stub) Implement real PZ RCON logic here.\n")

        # On success, set status:
        self.rcon_status.set("Connected")
        # If it fails, you'd do:
        # self.rcon_status.set("Disconnected")

    # -------------------------------------------------------------------
    # CONFIG SAVE/LOAD
    # -------------------------------------------------------------------
    def save_config(self):
        data = {
            "last_batch_file": self.batch_file_path,
            "rcon_ip": self.rcon_ip.get(),
            "rcon_port": self.rcon_port.get(),
            "rcon_password": self.rcon_password.get()
        }
        try:
            with open("last_config.json", "w") as f:
                json.dump(data, f)
        except Exception as e:
            print(f"Failed to save config: {e}")

    def load_last_config(self):
        if not os.path.exists("last_config.json"):
            return
        try:
            with open("last_config.json", "r") as f:
                data = json.load(f)
                # Load batch path
                self.batch_file_path = data.get("last_batch_file", None)
                if self.batch_file_path:
                    self.print_to_console(f"Loaded batch file from config: {self.batch_file_path}\n")
                    self.start_button.config(state=tk.NORMAL)
                    self.restart_button.config(state=tk.NORMAL)

                # Load RCON
                self.rcon_ip.set(data.get("rcon_ip", ""))
                self.rcon_port.set(data.get("rcon_port", ""))
                self.rcon_password.set(data.get("rcon_password", ""))

                self.print_to_console("Loaded RCON settings from config.\n")

        except Exception as e:
            print(f"Failed to load config: {e}")


# --------------------------- MAIN ---------------------------------- #
if __name__ == "__main__":
    root = tk.Tk()
    root.title("Project Zomboid Server Manager - INI Editor in the Middle")
    app = Terminal(root)
    app.pack(fill=tk.BOTH, expand=True)
    root.geometry("1200x600")  # Extra width for the 3-column layout
    root.mainloop()
