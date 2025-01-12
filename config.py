import tkinter as tk
from tkinter import filedialog, messagebox

class ConfigManager:
    def __init__(self, root, config_file_path):
        self.root = root
        self.config_file_path = config_file_path
        self.config_text = None

    def create_config_tab(self, parent):
        config_frame = tk.Frame(parent, bg="#1e1e1e", padx=10, pady=10)
        config_frame.pack(fill=tk.BOTH, expand=True)

        tk.Label(config_frame, text="Config File Path:", bg="#1e1e1e", fg="#00ff00").pack(side=tk.LEFT, padx=5)
        self.config_file_entry = tk.Entry(config_frame, bg="#000000", fg="#00ff00")
        self.config_file_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        self.config_file_entry.insert(0, self.config_file_path)
        tk.Button(config_frame, text="Browses", command=self.browse_config_file, bg="#00ff00", fg="#000000", relief=tk.FLAT).pack(side=tk.LEFT, padx=5)
        
        self.config_text = tk.Text(config_frame, wrap=tk.WORD, bg="#000000", fg="#00ff00", font=("Courier New", 12))
        self.config_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.load_config_file()

        tk.Button(config_frame, text="Save", command=self.save_config_file, bg="#00ff00", fg="#000000", relief=tk.FLAT).pack(side=tk.BOTTOM, padx=5, pady=5)

    def browse_config_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("INI Files", "*.ini")])
        if file_path:
            self.config_file_path = file_path
            self.config_file_entry.delete(0, tk.END)
            self.config_file_entry.insert(0, self.config_file_path)
            self.load_config_file()

    def load_config_file(self):
        if self.config_file_path:
            try:
                with open(self.config_file_path, 'r') as file:
                    content = file.read()
                    self.config_text.delete(1.0, tk.END)
                    self.config_text.insert(tk.END, content)
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load config file: {e}")

    def save_config_file(self):
        if self.config_file_path:
            try:
                with open(self.config_file_path, 'w') as file:
                    content = self.config_text.get(1.0, tk.END)
                    file.write(content)
                messagebox.showinfo("Success", "Config file saved successfully.")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save config file: {e}")
2. Update Your Main Application Code
In your main application file, import ConfigManager from config.py and use it to create the config tab:

python
Copy code
import tkinter as tk
from tkinter import ttk
from config import ConfigManager  # Import the ConfigManager class

class AdvancedTerminalApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Advanced Terminal for Project Zomboid")
        self.geometry("1200x900")
        self.configure(bg="#1e1e1e")

        self.config_file_path = r"C:\Users\daleb\Zomboid\Server\servertest.ini"
        self.batch_file_path = None

        self.notebook = ttk.Notebook(self)
        self.notebook.pack(expand=True, fill='both')

        self.console_tab = tk.Frame(self.notebook, bg="#1e1e1e")
        self.map_tab = tk.Frame(self.notebook, bg="#1e1e1e")
        self.stats_tab = tk.Frame(self.notebook, bg="#1e1e1e")
        self.config_tab = tk.Frame(self.notebook, bg="#1e1e1e")

        self.notebook.add(self.console_tab, text="Console")
        self.notebook.add(self.map_tab, text="Map")
        self.notebook.add(self.stats_tab, text="Statistics")
        self.notebook.add(self.config_tab, text="Config")

        self.create_console_ui()
        self.create_map_tab()
        self.create_stats_tab()
        
        # Initialize ConfigManager and create config tab
        self.config_manager = ConfigManager(self, self.config_file_path)
        self.config_manager.create_config_tab(self.config_tab)

        self.command_history = []
        self.history_index = -1

        self.server_process = None
        self.log_monitor = None

    def create_console_ui(self):
        # Existing code for creating console UI
        pass

    def create_map_tab(self):
        pass

    def create_stats_tab(self):
        pass

    # Existing methods for handling server commands, start/stop/restart server, etc.

if __name__ == "__main__":
    app = AdvancedTerminalApp()
    app.mainloop()