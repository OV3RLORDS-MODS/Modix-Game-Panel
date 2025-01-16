import tkinter as tk
from tkinter import filedialog, messagebox
import subprocess
import psutil
import json
import os
import configparser
from datetime import datetime
import logging
import requests  # For retrieving public IP and sending Discord webhook messages
from mcrcon import MCRcon  # Generic RCON library

from mod_manager_text_editor import TextEditor

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

SERVER_STATE_FILE = "server_state.json"

class Terminal(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.setup_initial_state()
        self.create_widgets()
        self.after(100, self.load_last_config)
        self.after(1000, self.update_server_info)

    def setup_initial_state(self):
        # Server process and state variables
        self.batch_file_path = None
        self.process = None
        self.running = False

        # Discord webhook control
        self.webhook_enabled = False
        self.discord_webhook_url = ""  # URL for Discord webhook

        # Embed details for Discord messages
        self.embed_title = "Server Notification"
        self.embed_description = "The server has started."

        # RCON configuration
        self.rcon_enabled = False
        self.rcon_host = "127.0.0.1"
        self.rcon_port = 25575
        self.rcon_password = "password"

        # Server info dictionary
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
        self.load_server_state()

        # INI file parsing variables
        self.ini_path = None
        self.ini_data = configparser.ConfigParser()

        # UI style variables
        self.text_color = '#FFFFFF'
        self.bg_color = '#1E1E2E'
        self.card_bg = '#2B2B3B'

        # Command autocomplete list
        self.available_commands = [
            "/ban", "/kick", "/unban", "/mute", "/unmute",
            "/tp", "/additem", "/setaccesslevel",
            "/saveworld", "/shutdown", "/restart", "/stop", "/start",
            "/settime", "/setweather", "/clearzonemods", "/removebuildings",
            "/getplayers", "/getplayerdata",
            "/pause", "/unpause", "/givexp", "/resetpassword", "/teleport",
            "/spawnitem", "/spawnvehicle", "/setspawnregion", "/addvehicle",
            "/removevehicle", "/setdifficulty", "/setmaxplayers",
            "/setpvp", "/setservername", "/setmotd", "/listcommands"
        ]
        # Discover additional mod commands
        mods_directory = "./mods"
        discovered = self.discover_mod_commands(mods_directory)
        for cmd in discovered:
            if cmd not in self.available_commands:
                self.available_commands.append(cmd)

    def load_server_state(self):
        if os.path.exists(SERVER_STATE_FILE):
            try:
                with open(SERVER_STATE_FILE, "r") as f:
                    saved_state = json.load(f)
                    for key in self.server_info:
                        if key in saved_state:
                            self.server_info[key] = saved_state[key]
                    self.discord_webhook_url = saved_state.get("discord_webhook_url", "")
            except Exception as e:
                logging.error(f"Failed to load server state: {e}")

    def save_server_state(self):
        try:
            data = dict(self.server_info)
            data["discord_webhook_url"] = self.discord_webhook_url
            # You can also save RCON settings if desired
            with open(SERVER_STATE_FILE, "w") as f:
                json.dump(data, f)
        except Exception as e:
            logging.error(f"Failed to save server state: {e}")

    def discover_mod_commands(self, mods_directory):
        discovered_commands = []
        for root, dirs, files in os.walk(mods_directory):
            if 'commands.txt' in files:
                commands_file = os.path.join(root, 'commands.txt')
                try:
                    with open(commands_file, 'r') as cf:
                        for line in cf:
                            cmd = line.strip()
                            if cmd.startswith("/"):
                                discovered_commands.append(cmd)
                except Exception as e:
                    logging.error(f"Error reading {commands_file}: {e}")
        return discovered_commands

    def create_widgets(self):
        header_frame = tk.Frame(self, bg=self.bg_color)
        header_frame.pack(side=tk.TOP, pady=10, fill=tk.X)
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

        self.select_ini_button = tk.Button(
            button_frame, text="Select .ini", command=self.select_ini_file,
            bg='#2E2E2E', fg=self.text_color, font=('Consolas', 12),
            relief='flat', cursor='hand2'
        )
        self.select_ini_button.grid(row=0, column=4, padx=5)

        main_content_frame = tk.Frame(self, bg=self.bg_color)
        main_content_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        self.console_frame = tk.Frame(main_content_frame, bg=self.bg_color)
        self.console_frame.pack(side=tk.LEFT, padx=10, pady=10, fill=tk.BOTH, expand=True)

        self.console_text = tk.Text(
            self.console_frame, height=20, wrap=tk.WORD,
            bg=self.bg_color, fg=self.text_color, font=('Consolas', 12),
            state=tk.DISABLED
        )
        self.console_text.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        self.ini_editor_frame = tk.Frame(main_content_frame, bg=self.card_bg)
        self.ini_editor_frame.pack(side=tk.LEFT, fill=tk.BOTH, padx=10, pady=10)

        right_frame = tk.Frame(main_content_frame, bg=self.bg_color)
        right_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=10, pady=10)

        # Discord Webhook status section
        bot_frame = tk.Frame(right_frame, bg=self.card_bg, bd=0, highlightthickness=0)
        bot_frame.pack(fill=tk.X, pady=6, padx=2)
        bot_inner_frame = tk.Frame(bot_frame, bg=self.card_bg)
        bot_inner_frame.pack(fill=tk.X, padx=10, pady=5)

        bot_label = tk.Label(bot_inner_frame, text="Discord Webhook:", fg=self.text_color,
                             bg=self.card_bg, font=('Consolas', 12, 'bold'))
        bot_label.pack(side=tk.LEFT)

        self.bot_canvas = tk.Canvas(bot_inner_frame, width=20, height=20, bg=self.card_bg, highlightthickness=0)
        self.bot_canvas.pack(side=tk.LEFT, padx=(8, 0))
        self.bot_indicator = self.bot_canvas.create_oval(2, 2, 18, 18, fill="red")

        self.edit_bot_button = tk.Button(bot_inner_frame, text="Edit", command=self.open_webhook_dialog,
                                         bg='#2E2E2E', fg=self.text_color, font=('Consolas', 10),
                                         relief='flat', cursor='hand2')
        self.edit_bot_button.pack(side=tk.LEFT, padx=(8,0))

        self.edit_embed_button = tk.Button(bot_inner_frame, text="Edit Embed", command=self.open_embed_dialog,
                                           bg='#2E2E2E', fg=self.text_color, font=('Consolas', 10),
                                           relief='flat', cursor='hand2')
        self.edit_embed_button.pack(side=tk.LEFT, padx=(8,0))

        self.toggle_webhook_button = tk.Button(bot_inner_frame, text="Enable Webhook", command=self.toggle_webhook,
                                               bg='#2E2E2E', fg=self.text_color, font=('Consolas', 10),
                                               relief='flat', cursor='hand2')
        self.toggle_webhook_button.pack(side=tk.LEFT, padx=(8,0))

        server_info_keys = [
            "IP", "Port", "Player Slots", "CPU Usage", "Memory Usage",
            "Last Crash", "Last Closed", "Last Restart"
        ]
        for key in server_info_keys:
            card_frame = tk.Frame(right_frame, bg=self.card_bg, bd=0, highlightthickness=0)
            card_frame.pack(fill=tk.X, pady=6, padx=2)
            inner_frame = tk.Frame(card_frame, bg=self.card_bg)
            inner_frame.pack(fill=tk.X, padx=10, pady=5)
            key_label = tk.Label(inner_frame, text=f"{key}:", fg=self.text_color,
                                 bg=self.card_bg, font=('Consolas', 12, 'bold'))
            key_label.pack(side=tk.LEFT)
            value_label = tk.Label(inner_frame, text=self.server_info[key],
                                   fg=self.text_color, bg=self.card_bg, font=('Consolas', 12))
            value_label.pack(side=tk.LEFT, padx=(8, 0))
            self.server_info_labels[key] = value_label

        command_title = tk.Label(right_frame, text="Send Command", fg=self.text_color,
                                 bg=self.bg_color, font=('Consolas', 14, 'bold', 'underline'))
        command_title.pack(anchor="w", pady=(20, 5))

        self.command_entry = tk.Entry(right_frame, font=('Consolas', 12))
        self.command_entry.pack(fill=tk.X, pady=2)
        self.command_entry.bind("<KeyRelease>", self.update_suggestions)

        self.suggestion_box = tk.Listbox(right_frame, font=('Consolas', 12), height=5)
        self.suggestion_box.bind("<<ListboxSelect>>", self.on_suggestion_select)
        self.suggestion_box.bind("<Return>", self.on_suggestion_confirm)

        send_command_button = tk.Button(right_frame, text="Send Command", command=self.send_command,
                                        bg='#2E2E2E', fg=self.text_color, font=('Consolas', 12),
                                        relief='flat', cursor='hand2')
        send_command_button.pack(pady=5, anchor="e")

    def open_webhook_dialog(self):
        dialog = tk.Toplevel(self)
        dialog.title("Edit Discord Webhook")
        dialog.configure(bg=self.card_bg)

        lbl_url = tk.Label(dialog, text="Discord Webhook URL:", bg=self.card_bg, fg=self.text_color, font=('Consolas', 12))
        lbl_url.pack(pady=5)
        entry_url = tk.Entry(dialog, width=50, bg=self.bg_color, fg=self.text_color,
                             insertbackground=self.text_color, font=('Consolas', 12))
        entry_url.insert(0, self.discord_webhook_url)
        entry_url.pack(pady=5)

        def save_webhook():
            self.discord_webhook_url = entry_url.get()
            dialog.destroy()

        btn_save = tk.Button(dialog, text="Save", command=save_webhook,
                             bg='#2E2E2E', fg=self.text_color, font=('Consolas', 12),
                             relief='flat', cursor='hand2')
        btn_save.pack(pady=10)

        btn_cancel = tk.Button(dialog, text="Cancel", command=dialog.destroy,
                               bg='#2E2E2E', fg=self.text_color, font=('Consolas', 12),
                               relief='flat', cursor='hand2')
        btn_cancel.pack(pady=5)

    def open_embed_dialog(self):
        dialog = tk.Toplevel(self)
        dialog.title("Edit Embed")
        dialog.configure(bg=self.card_bg)

        lbl_title = tk.Label(dialog, text="Embed Title:", bg=self.card_bg, fg=self.text_color, font=('Consolas', 12))
        lbl_title.pack(pady=5)
        entry_title = tk.Entry(dialog, width=50, bg=self.bg_color, fg=self.text_color,
                               insertbackground=self.text_color, font=('Consolas', 12))
        entry_title.insert(0, self.embed_title)
        entry_title.pack(pady=5)

        lbl_desc = tk.Label(dialog, text="Embed Description:", bg=self.card_bg, fg=self.text_color, font=('Consolas', 12))
        lbl_desc.pack(pady=5)
        entry_desc = tk.Entry(dialog, width=50, bg=self.bg_color, fg=self.text_color,
                              insertbackground=self.text_color, font=('Consolas', 12))
        entry_desc.insert(0, self.embed_description)
        entry_desc.pack(pady=5)

        def save_embed():
            self.embed_title = entry_title.get()
            self.embed_description = entry_desc.get()
            dialog.destroy()

        btn_save = tk.Button(dialog, text="Save", command=save_embed,
                             bg='#2E2E2E', fg=self.text_color, font=('Consolas', 12),
                             relief='flat', cursor='hand2')
        btn_save.pack(pady=10)

        btn_cancel = tk.Button(dialog, text="Cancel", command=dialog.destroy,
                               bg='#2E2E2E', fg=self.text_color, font=('Consolas', 12),
                               relief='flat', cursor='hand2')
        btn_cancel.pack(pady=5)

    def toggle_webhook(self):
        self.webhook_enabled = not self.webhook_enabled
        new_text = "Disable Webhook" if self.webhook_enabled else "Enable Webhook"
        self.toggle_webhook_button.config(text=new_text)

    def update_suggestions(self, event):
        typed = self.command_entry.get().strip().lower()
        self.suggestion_box.delete(0, tk.END)
        if not typed:
            self.suggestion_box.forget()
            return
        suggestions = [cmd for cmd in self.available_commands if cmd.lower().startswith(typed)]
        if suggestions:
            for suggestion in suggestions:
                self.suggestion_box.insert(tk.END, suggestion)
            self.suggestion_box.pack(fill=tk.X, pady=(0,5))
        else:
            self.suggestion_box.forget()

    def on_suggestion_select(self, event):
        selection = self.suggestion_box.curselection()
        if selection:
            selected_command = self.suggestion_box.get(selection[0])
            self.command_entry.delete(0, tk.END)
            self.command_entry.insert(0, selected_command)
            self.suggestion_box.forget()

    def on_suggestion_confirm(self, event):
        self.on_suggestion_select(event)
        self.command_entry.focus()

    def select_ini_file(self):
        ini_path = filedialog.askopenfilename(
            filetypes=[("INI Files", "*.ini"), ("All Files", "*.*")],
            title="Select .ini File"
        )
        if not ini_path:
            return
        self.ini_path = ini_path
        self.print_to_console(f"Selected .ini file: {ini_path}\n")
        try:
            self.ini_data.read(ini_path)
            if "Server" in self.ini_data and "Port" in self.ini_data["Server"]:
                self.server_info["Port"] = self.ini_data["Server"]["Port"]
                if "Port" in self.server_info_labels:
                    self.server_info_labels["Port"].config(text=self.server_info["Port"])
        except Exception as e:
            self.print_to_console(f"Error reading .ini file: {e}\n")
        TextEditor(self, ini_path)

    def print_to_console(self, text: str):
        self.console_text.config(state=tk.NORMAL)
        self.console_text.insert(tk.END, text)
        self.console_text.config(state=tk.DISABLED)
        self.console_text.yview(tk.END)

    def select_batch_file(self):
        path = filedialog.askopenfilename(
            filetypes=[("Batch Files", "*.bat"), ("All Files", "*.*")]
        )
        if path:
            self.batch_file_path = path
            self.print_to_console(f"Selected batch file: {path}\n")
            self.start_button.config(state=tk.NORMAL)
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

                try:
                    public_ip = requests.get('https://api.ipify.org').text
                    self.server_info["IP"] = public_ip
                    if "IP" in self.server_info_labels:
                        self.server_info_labels["IP"].config(text=public_ip)
                except Exception as e:
                    self.server_info["IP"] = "Error retrieving IP"
                    logging.error(f"Failed to retrieve public IP: {e}")

                if self.webhook_enabled and self.discord_webhook_url:
                    self.send_webhook_message("Server started")

                self.server_info["Last Restart"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                self.save_server_state()
                self.print_to_console(f"Server started with PID {self.process.pid}.\n")
                self.start_button.config(state=tk.DISABLED)
                self.restart_button.config(state=tk.NORMAL)
                self.stop_button.config(state=tk.NORMAL)
                self.after(100, self.read_batch_output)
            except Exception as e:
                messagebox.showerror("Error", f"Failed to start server:\n{e}")

    def send_webhook_message(self, message):
        url = self.discord_webhook_url
        payload = {
            "content": message,
            "embeds": [{
                "title": self.embed_title,
                "description": self.embed_description,
                "color": 65280  # Green color
            }]
        }
        try:
            response = requests.post(url, json=payload, timeout=5)
            self.print_to_console(f"Discord Webhook response: {response.status_code}\n")
        except Exception as e:
            self.print_to_console(f"Error sending Discord webhook message: {e}\n")

    def read_batch_output(self):
        if self.process is None:
            return
        try:
            line = self.process.stdout.readline()
            if line:
                self.print_to_console(line)
        except Exception as e:
            self.print_to_console(f"Error reading server output: {e}\n")
        if self.process and self.process.poll() is None:
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
                self.server_info["Last Closed"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            except psutil.TimeoutExpired:
                self.print_to_console("Graceful termination failed. Killing process...\n")
                for child in parent.children(recursive=True):
                    child.kill()
                parent.kill()
                self.server_info["Last Crash"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.print_to_console("Server stopped.\n")
            self.running = False
            self.process = None
            self.start_button.config(state=tk.NORMAL)
            self.restart_button.config(state=tk.DISABLED)
            self.stop_button.config(state=tk.DISABLED)
            self.save_server_state()
        except Exception as e:
            self.print_to_console(f"Error stopping server:\n{e}\n")

    def send_command(self):
        command = self.command_entry.get().strip()
        if not command:
            self.print_to_console("Please enter a command.\n")
            return
        if not self.running:
            self.print_to_console("Server is not running.\n")
            return
        try:
            if self.rcon_enabled:
                self.send_rcon_command(command)
            else:
                if self.process and self.process.stdin:
                    self.process.stdin.write(command + "\n")
                    self.process.stdin.flush()
                    self.print_to_console(f"Command sent: {command}\n")
        except Exception as e:
            self.print_to_console(f"Error sending command: {e}\n")
        self.command_entry.delete(0, tk.END)

    def send_rcon_command(self, command):
        try:
            with MCRcon(self.rcon_host, self.rcon_password, port=self.rcon_port) as mcr:
                response = mcr.command(command)
                self.print_to_console(f"RCON response: {response}\n")
        except Exception as e:
            self.print_to_console(f"RCON error: {e}\n")

    def update_server_info(self):
        # Update Discord webhook status indicator
        if self.webhook_enabled and self.discord_webhook_url:
            self.bot_canvas.itemconfig(self.bot_indicator, fill="green")
        else:
            self.bot_canvas.itemconfig(self.bot_indicator, fill="red")

        if self.running and self.process:
            try:
                proc = psutil.Process(self.process.pid)
                cpu_usage = proc.cpu_percent(interval=0.1)
                mem_info = proc.memory_info()
                mem_usage = mem_info.rss / (1024 * 1024)
                self.server_info["CPU Usage"] = f"{cpu_usage}%"
                self.server_info["Memory Usage"] = f"{mem_usage:.2f} MB"

                if "IP" in self.server_info_labels:
                    self.server_info_labels["IP"].config(text=self.server_info["IP"])
                if "Port" in self.server_info_labels:
                    self.server_info_labels["Port"].config(text=self.server_info["Port"])

                for key, label in self.server_info_labels.items():
                    label.config(text=self.server_info.get(key, "N/A"))
            except Exception as e:
                logging.error(f"Error updating server info: {e}")
        self.after(1000, self.update_server_info)

    def save_config(self):
        data = {"last_batch_file": self.batch_file_path}
        try:
            with open("last_config.json", "w") as f:
                json.dump(data, f)
        except Exception as e:
            logging.error(f"Failed to save config: {e}")

    def load_last_config(self):
        if not os.path.exists("last_config.json"):
            return
        try:
            with open("last_config.json", "r") as f:
                data = json.load(f)
                self.batch_file_path = data.get("last_batch_file", None)
                if self.batch_file_path:
                    self.print_to_console(f"Loaded batch file from config: {self.batch_file_path}\n")
                    self.start_button.config(state=tk.NORMAL)
                    self.restart_button.config(state=tk.NORMAL)
                self.print_to_console("Loaded configuration.\n")
        except Exception as e:
            logging.error(f"Failed to load config: {e}")

    def on_close(self):
        if self.running:
            self.stop_server()
        self.master.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    root.title("Project Zomboid Server Manager")
    app = Terminal(root)
    app.pack(fill=tk.BOTH, expand=True)
    root.geometry("1200x600")
    root.protocol("WM_DELETE_WINDOW", app.on_close)
    root.mainloop()
