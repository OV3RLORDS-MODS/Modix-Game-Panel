import tkinter as tk
from tkinter import filedialog, messagebox, colorchooser
import subprocess
import threading
import psutil
import json
import os

class Terminal(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.setup_initial_state()
        self.create_widgets()
        self.update_styles()
        self.display_welcome_message()

        # Deferred loading
        self.after(100, self.load_last_batch_file)
        self.after(200, self.load_command_history)

    def setup_initial_state(self):
        self.batch_file_path = None
        self.process = None
        self.running = False
        self.booting_up = False
        self.server_info = {
            "IP": "N/A", "Port": "N/A", "Player Slots": "N/A",
            "CPU Usage": "N/A", "Memory Usage": "N/A",
            "Last Crash": "N/A", "Last Closed": "N/A", "Last Restart": "N/A"
        }
        self.server_info_labels = {}
        self.command_history = []
        self.history_index = -1
        self.text_color = '#00FF00'
        self.bg_color = '#1E1E1E'
        self.highlight_tag = 'highlight'

    def create_widgets(self):
        # Header frame and buttons
        header_frame = tk.Frame(self, bg=self.bg_color)
        header_frame.pack(pady=10, fill=tk.X)

        button_frame = tk.Frame(header_frame, bg=self.bg_color)
        button_frame.pack(side=tk.TOP, fill=tk.X)

        self.select_button = tk.Button(
            button_frame, text="Select Batch File", command=self.select_batch_file,
            bg='#2E2E2E', fg=self.text_color, font=('Consolas', 12), relief='flat', cursor='hand2'
        )
        self.select_button.grid(row=0, column=0, padx=5)

        self.start_button = tk.Button(
            button_frame, text="Start Server", command=self.start_server,
            bg='#2E2E2E', fg=self.text_color, font=('Consolas', 12), relief='flat', cursor='hand2', state=tk.DISABLED
        )
        self.start_button.grid(row=0, column=1, padx=5)

        self.restart_button = tk.Button(
            button_frame, text="Restart Server", command=self.restart_server,
            bg='#2E2E2E', fg=self.text_color, font=('Consolas', 12), relief='flat', cursor='hand2', state=tk.DISABLED
        )
        self.restart_button.grid(row=0, column=2, padx=5)

        self.stop_button = tk.Button(
            button_frame, text="Stop Server", command=self.stop_server,
            bg='#2E2E2E', fg=self.text_color, font=('Consolas', 12), relief='flat', cursor='hand2', state=tk.DISABLED
        )
        self.stop_button.grid(row=0, column=3, padx=5)

        self.edit_db_button = tk.Button(
            button_frame, text="EDIT DB", command=self.edit_db,
            bg='#2E2E2E', fg=self.text_color, font=('Consolas', 12), relief='flat', cursor='hand2'
        )
        self.edit_db_button.grid(row=0, column=4, padx=5)

        self.color_button = tk.Button(
            button_frame, text="Change Text Color", command=self.change_text_color,
            bg='#2E2E2E', fg=self.text_color, font=('Consolas', 12), relief='flat', cursor='hand2'
        )
        self.color_button.grid(row=0, column=5, padx=5)

        self.bg_color_button = tk.Button(
            button_frame, text="Change Background Color", command=self.change_background_color,
            bg='#2E2E2E', fg=self.text_color, font=('Consolas', 12), relief='flat', cursor='hand2'
        )
        self.bg_color_button.grid(row=0, column=6, padx=5)

        # Console frame and text
        self.console_frame = tk.Frame(self, bg=self.bg_color)
        self.console_frame.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        self.console_text = tk.Text(
            self.console_frame, height=20, wrap=tk.WORD,
            bg=self.bg_color, fg=self.text_color, font=('Consolas', 12), state=tk.DISABLED
        )
        self.console_text.pack(fill=tk.BOTH, expand=True)

        # Command entry and execute button
        self.command_box_frame = tk.Frame(self, bg=self.bg_color)
        self.command_box_frame.pack(fill=tk.X, padx=10, pady=5)

        self.command_entry = tk.Entry(
            self.command_box_frame, font=('Consolas', 12),
            bg='#2E2E2E', fg=self.text_color, insertbackground='white'
        )
        self.command_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.command_entry.bind("<Return>", self.send_command)

        self.execute_button = tk.Button(
            self.command_box_frame, text="Execute", command=self.send_command,
            bg='#2E2E2E', fg=self.text_color, font=('Consolas', 12), relief='flat', cursor='hand2'
        )
        self.execute_button.pack(side=tk.RIGHT, padx=5)

        # Search frame and button
        search_frame = tk.Frame(self, bg=self.bg_color)
        search_frame.pack(pady=5, fill=tk.X, padx=10)

        self.search_entry = tk.Entry(
            search_frame, font=('Consolas', 12),
            bg='#2E2E2E', fg=self.text_color, insertbackground='white'
        )
        self.search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.search_entry.bind("<KeyRelease>", self.search_output)

        self.search_button = tk.Button(
            search_frame, text="Search", command=self.search_output,
            bg='#2E2E2E', fg=self.text_color, font=('Consolas', 12), relief='flat', cursor='hand2'
        )
        self.search_button.pack(side=tk.RIGHT, padx=5)

        # Status frame
        bottom_frame = tk.Frame(self, bg=self.bg_color, bd=2, relief='solid')
        bottom_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=10)

        self.status_indicator = tk.Canvas(bottom_frame, width=20, height=20, bg=self.bg_color, highlightthickness=0)
        self.status_indicator.grid(row=0, column=0, padx=10)

        self.status_text = tk.Label(
            bottom_frame, text="Offline", fg='#FF0000', bg=self.bg_color, font=('Consolas', 12)
        )
        self.status_text.grid(row=0, column=1, padx=(5, 10))

        # Server info labels
        server_info_labels = [
            "IP", "Port", "Player Slots", "CPU Usage", "Memory Usage",
            "Last Crash", "Last Closed", "Last Restart"
        ]
        for idx, key in enumerate(server_info_labels):
            label = tk.Label(
                bottom_frame, text=f"{key}:", fg=self.text_color, bg=self.bg_color, font=('Consolas', 12, 'bold')
            )
            label.grid(row=0, column=2 + 2 * idx, padx=(10, 2), pady=5, sticky=tk.W)
            value = tk.Label(
                bottom_frame, text=self.server_info[key], fg=self.text_color, bg=self.bg_color, font=('Consolas', 12)
            )
            value.grid(row=0, column=2 + 2 * idx + 1, padx=(2, 10), pady=5, sticky=tk.W)
            self.server_info_labels[key] = value

    def update_styles(self):
        self.configure(bg=self.bg_color)
        self.console_text.config(bg=self.bg_color, fg=self.text_color)
        self.command_entry.config(bg='#2E2E2E', fg=self.text_color, insertbackground='white')
        self.execute_button.config(bg='#2E2E2E', fg=self.text_color)
        self.status_text.config(bg=self.bg_color, fg=self.text_color)
        self.status_indicator.config(bg=self.bg_color)
        for label in self.server_info_labels.values():
            label.config(bg=self.bg_color, fg=self.text_color)

    def display_welcome_message(self):
        welcome_message = (
            "--------------------------------------------------\n"
            "             Welcome to Node Manager v1.0.2\n"
            "--------------------------------------------------\n"
            "if you encounter any bugs or have suggestions for improvements, please let us know! Join our community on Discord and report any issues or provide feedback. Your input helps us improve and deliver a better experience.\n"
            "--------------------------------------------------\n"
        )
        self.console_text.config(state=tk.NORMAL)
        self.console_text.insert(tk.END, welcome_message)
        self.console_text.config(state=tk.DISABLED)
        self.console_text.yview(tk.END)

    def select_batch_file(self):
        self.batch_file_path = filedialog.askopenfilename(
            filetypes=[("Batch Files", "*.bat"), ("All Files", "*.*")]
        )
        if self.batch_file_path:
            self.start_button.config(state=tk.NORMAL)
            self.save_last_batch_file()

    def start_server(self):
        if not self.batch_file_path:
            messagebox.showwarning("Warning", "No batch file selected.")
            return

        if not self.running:
            try:
                self.booting_up = True
                self.process = subprocess.Popen(
                    [self.batch_file_path],
                    stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE, shell=True, text=True
                )
                self.running = True
                self.start_button.config(state=tk.DISABLED)
                self.restart_button.config(state=tk.NORMAL)
                self.stop_button.config(state=tk.NORMAL)
                self.update_status_indicator()
                self.read_output()
                self.update_server_info()
                self.console_text.config(state=tk.NORMAL)
                self.console_text.insert(tk.END, f"Server started with PID {self.process.pid}.\n")
                self.console_text.config(state=tk.DISABLED)
                self.console_text.yview(tk.END)
                self.booting_up = False
            except Exception as e:
                messagebox.showerror("Error", f"Failed to start server: {e}")

    def restart_server(self):
        self.stop_server()
        self.start_server()

    def stop_server(self):
        if self.running:
            try:
                if self.process:
                    pid = self.process.pid
                    self.console_text.config(state=tk.NORMAL)
                    self.console_text.insert(tk.END, f"Attempting to stop server with PID {pid}...\n")

                    # Attempt to terminate the process gracefully
                    parent = psutil.Process(pid)
                    for child in parent.children(recursive=True):
                        self.console_text.insert(tk.END, f"Terminating child process PID {child.pid}...\n")
                        child.terminate()

                    parent.terminate()
                    try:
                        parent.wait(timeout=10)  # Wait for up to 10 seconds for the process to terminate
                    except psutil.TimeoutExpired:
                        # Forcefully kill the process if it didn't terminate gracefully
                        self.console_text.insert(tk.END, "Graceful termination failed. Forcefully killing the process...\n")
                        for child in parent.children(recursive=True):
                            child.kill()
                        parent.kill()
                    
                    self.console_text.insert(tk.END, "Server stopped.\n")
                    self.console_text.config(state=tk.DISABLED)
                    self.console_text.yview(tk.END)
                    self.running = False
                    self.process = None
                    self.start_button.config(state=tk.NORMAL)
                    self.restart_button.config(state=tk.DISABLED)
                    self.stop_button.config(state=tk.DISABLED)
                    self.update_status_indicator()
            except Exception as e:
                self.console_text.config(state=tk.NORMAL)
                self.console_text.insert(tk.END, f"Error stopping server: {e}\n")
                self.console_text.config(state=tk.DISABLED)
                self.console_text.yview(tk.END)

    def read_output(self):
        def output_reader(process):
            while process.poll() is None:
                output = process.stdout.readline()
                if output:
                    self.console_text.config(state=tk.NORMAL)
                    self.console_text.insert(tk.END, output)
                    self.console_text.config(state=tk.DISABLED)
                    self.console_text.yview(tk.END)

        if self.process:
            threading.Thread(target=output_reader, args=(self.process,), daemon=True).start()

    def update_server_info(self):
        # Update the server info dictionary with actual data.
        pass

    def update_status_indicator(self):
        if self.running:
            self.status_indicator.config(bg='#00FF00')  # Green for running
            self.status_text.config(text="Online", fg='#00FF00')
        else:
            self.status_indicator.config(bg='#FF0000')  # Red for offline
            self.status_text.config(text="Offline", fg='#FF0000')

    def edit_db(self):
        # Implement database editing functionality
        pass

    def change_text_color(self):
        color = colorchooser.askcolor(initialcolor=self.text_color)[1]
        if color:
            self.text_color = color
            self.update_styles()

    def change_background_color(self):
        color = colorchooser.askcolor(initialcolor=self.bg_color)[1]
        if color:
            self.bg_color = color
            self.update_styles()

    def send_command(self, event=None):
        command = self.command_entry.get()
        if command:
            if self.process:
                self.process.stdin.write(command + '\n')
                self.process.stdin.flush()
                self.command_entry.delete(0, tk.END)
                self.command_history.append(command)
                self.history_index = len(self.command_history)

    def search_output(self, event=None):
        search_term = self.search_entry.get()
        self.console_text.config(state=tk.NORMAL)
        self.console_text.tag_remove(self.highlight_tag, '1.0', tk.END)

        if not search_term:
            self.console_text.config(state=tk.DISABLED)
            return

        start_pos = '1.0'
        while True:
            start_pos = self.console_text.search(search_term, start_pos, nocase=True, stopindex=tk.END)
            if not start_pos:
                break

            end_pos = f"{start_pos}+{len(search_term)}c"
            self.console_text.tag_add(self.highlight_tag, start_pos, end_pos)
            start_pos = end_pos

        self.console_text.tag_configure(self.highlight_tag, background='yellow', foreground='black')
        self.console_text.config(state=tk.DISABLED)
        if start_pos:
            self.console_text.see(start_pos)

    def save_last_batch_file(self):
        try:
            with open("last_batch_file.json", "w") as f:
                json.dump({"last_batch_file": self.batch_file_path}, f)
        except Exception as e:
            print(f"Failed to save last batch file path: {e}")

    def load_last_batch_file(self):
        try:
            if os.path.exists("last_batch_file.json"):
                with open("last_batch_file.json", "r") as f:
                    data = json.load(f)
                    self.batch_file_path = data.get("last_batch_file", None)
                    if self.batch_file_path:
                        self.start_button.config(state=tk.NORMAL)
                        self.restart_button.config(state=tk.NORMAL)
        except Exception as e:
            print(f"Failed to load last batch file path: {e}")

    def load_command_history(self):
        try:
            if os.path.exists("command_history.json"):
                with open("command_history.json", "r") as f:
                    self.command_history = json.load(f)
                    self.history_index = len(self.command_history)
        except Exception as e:
            print(f"Failed to load command history: {e}")

    def save_command_history(self):
        try:
            with open("command_history.json", "w") as f:
                json.dump(self.command_history, f)
        except Exception as e:
            print(f"Failed to save command history: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    root.title("Server Manager")
    app = Terminal(root)
    app.pack(fill=tk.BOTH, expand=True)
    root.geometry("800x600")
    root.mainloop()
