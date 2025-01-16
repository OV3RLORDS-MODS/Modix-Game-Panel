import tkinter as tk
from tkinter import ttk, messagebox
import psutil
import socket
import platform
import time
from datetime import datetime

class System(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        # Check if this script is being run directly
        if __name__ == "__main__":
            messagebox.showerror("Error", "You cannot run mods.py directly. Please run app.py.")
            sys.exit()  # Exit if the script is executed directly without going through app.py

        # Theme settings
        self.bg_color = "#1E1E1E"
        self.card_bg = "#282A36"
        self.text_color = "#FFFFFF"
        self.font_title = ("Segoe UI", 22, "bold")
        self.font_subtitle = ("Segoe UI", 12, "italic")
        self.font_header = ("Segoe UI", 12, "bold")
        self.font_normal = ("Segoe UI", 10)

        super().__init__(parent, bg=self.bg_color, *args, **kwargs)

        # Title Section
        title_frame = tk.Frame(self, bg=self.bg_color)
        title_frame.pack(pady=20, fill=tk.X)

        title_label = tk.Label(title_frame, text="System Information", bg=self.bg_color, 
                               fg=self.text_color, font=self.font_title)
        title_label.pack()

        subtitle_label = tk.Label(title_frame, text="Comprehensive System Overview and Project Zomboid Server Compatibility", 
                                  bg=self.bg_color, fg="#CCCCCC", font=self.font_subtitle)
        subtitle_label.pack()

        # Main Content Frame
        content_frame = tk.Frame(self, bg=self.bg_color)
        content_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Requirements Frame on Left
        self.requirements_frame = tk.LabelFrame(content_frame, text="Project Zomboid Server Requirements", 
                                                bg=self.card_bg, fg=self.text_color, font=self.font_header, bd=2, relief=tk.GROOVE)
        self.requirements_frame.grid(row=0, column=0, sticky="nsew", padx=(0,10), pady=5)
        self.create_requirements_widgets()

        # System Info Frame on Right
        self.info_frame = tk.LabelFrame(content_frame, text="Detailed System Information", 
                                        bg=self.card_bg, fg=self.text_color, font=self.font_header, bd=2, relief=tk.GROOVE)
        self.info_frame.grid(row=0, column=1, sticky="nsew", pady=5)

        self.info_text = tk.Text(self.info_frame, bg=self.bg_color, fg=self.text_color, 
                                 font=self.font_normal, wrap=tk.WORD, height=20)
        self.info_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Scrollbars for Info Text
        v_scroll = tk.Scrollbar(self.info_frame, orient=tk.VERTICAL, command=self.info_text.yview)
        v_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.info_text.config(yscrollcommand=v_scroll.set)

        h_scroll = tk.Scrollbar(self.info_frame, orient=tk.HORIZONTAL, command=self.info_text.xview)
        h_scroll.pack(side=tk.BOTTOM, fill=tk.X)
        self.info_text.config(xscrollcommand=h_scroll.set)

        # Configure grid weights for equal distribution
        content_frame.columnconfigure(0, weight=1)
        content_frame.columnconfigure(1, weight=2)
        content_frame.rowconfigure(0, weight=1)

        # Update button at bottom
        self.update_button = tk.Button(self, text="Update Info", command=self.update_info, 
                                       bg="#4CAF50", fg="#FFFFFF", font=self.font_header)
        self.update_button.pack(pady=10)

        # Initial Info Update
        self.update_info()

    def create_requirements_widgets(self):
        requirements = {
            "CPU Frequency (GHz)": "2.5",
            "Total RAM (GB)": "8",
            "Total Disk Space (GB)": "20",
            "Network Download Speed (Mbps)": "1",
            "Network Upload Speed (Mbps)": "1",
            "DirectX Version": "11"
        }

        self.requirement_labels = {}
        row = 0
        for key, value in requirements.items():
            label = tk.Label(self.requirements_frame, text=f"{key}:", bg=self.card_bg, 
                             fg=self.text_color, font=self.font_normal)
            label.grid(row=row, column=0, padx=10, pady=5, sticky="w")
            value_label = tk.Label(self.requirements_frame, text=value, bg=self.card_bg, 
                                   fg=self.text_color, font=self.font_normal)
            value_label.grid(row=row, column=1, padx=10, pady=5, sticky="w")
            self.requirement_labels[key] = value_label
            row += 1

        self.result_label = tk.Label(self.requirements_frame, text="Can I run it?", 
                                     bg="#FFCC00", fg="#000000", font=self.font_header)
        self.result_label.grid(row=row, column=0, padx=10, pady=10, sticky="w")

        self.result_status = tk.Label(self.requirements_frame, text="Checking...", 
                                      bg="#FFCC00", fg="#000000", font=self.font_header)
        self.result_status.grid(row=row, column=1, padx=10, pady=10, sticky="w")

    def get_system_info(self):
        try:
            uname = platform.uname()
            cpu_freq = psutil.cpu_freq().current / 1000
            memory_info = psutil.virtual_memory()
            disk_info = psutil.disk_usage('/')
            ip_address = socket.gethostbyname(socket.gethostname())
            cpu_cores = psutil.cpu_count(logical=True)
            # Placeholder GPU & network info
            gpu_info = "GPU info not implemented"
            network_info = "Network info not implemented"
            uptime = self.format_uptime(psutil.boot_time())

            system_info = {
                "Operating System": uname.system,
                "Node Name": uname.node,
                "Release": uname.release,
                "Version": uname.version,
                "Machine": uname.machine,
                "Processor": uname.processor,
                "CPU Frequency (GHz)": f"{round(cpu_freq, 2)} GHz",
                "CPU Cores": f"{cpu_cores}",
                "Total RAM (GB)": f"{round(memory_info.total / (1024 ** 3), 2)} GB",
                "Available RAM (GB)": f"{round(memory_info.available / (1024 ** 3), 2)} GB",
                "Used RAM (GB)": f"{round(memory_info.used / (1024 ** 3), 2)} GB",
                "Total Disk Space (GB)": f"{round(disk_info.total / (1024 ** 3), 2)} GB",
                "Used Disk Space (GB)": f"{round(disk_info.used / (1024 ** 3), 2)} GB",
                "Free Disk Space (GB)": f"{round(disk_info.free / (1024 ** 3), 2)} GB",
                "IP Address": ip_address,
                "DirectX Version": self.get_directx_version(),
                "GPU Info": gpu_info,
                "Network Interfaces": network_info,
                "System Uptime": uptime
            }
            return system_info
        except Exception as e:
            return {"Error": f"Failed to fetch system info: {e}"}

    def get_directx_version(self):
        try:
            return "12"
        except Exception as e:
            return "Unknown"

    def format_uptime(self, boot_time):
        try:
            uptime_seconds = time.time() - boot_time
            days = int(uptime_seconds // (24 * 3600))
            uptime_seconds %= (24 * 3600)
            hours = int(uptime_seconds // 3600)
            uptime_seconds %= 3600
            minutes = int(uptime_seconds // 60)
            seconds = int(uptime_seconds % 60)
            return f"{days} days, {hours} hours, {minutes} minutes, {seconds} seconds"
        except Exception as e:
            return "Error formatting uptime"

    def update_info(self):
        self.info_text.delete(1.0, tk.END)
        system_info = self.get_system_info()
        for key, value in system_info.items():
            self.info_text.insert(tk.END, f"{key}: {value}\n")
        self.check_requirements()
        self.info_text.insert(tk.END, f"\nUpdated at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    def check_requirements(self):
        try:
            req_cpu_freq = 2.5
            req_memory = 8
            req_disk_space = 20
            req_download_speed = 1
            req_upload_speed = 1
            req_directx_version = "11"

            system_info = self.get_system_info()

            cpu_freq = float(system_info.get("CPU Frequency (GHz)", "0").split()[0])
            memory_info = float(system_info.get("Total RAM (GB)", "0").split()[0])
            disk_info = float(system_info.get("Total Disk Space (GB)", "0").split()[0])
            # Placeholder speeds
            download_speed = 1
            upload_speed = 1
            directx_version = system_info.get("DirectX Version", "0")

            meets_requirements = (
                cpu_freq >= req_cpu_freq and
                memory_info >= req_memory and
                disk_info >= req_disk_space and
                download_speed >= req_download_speed and
                upload_speed >= req_upload_speed and
                directx_version >= req_directx_version
            )

            if meets_requirements:
                self.result_status.config(text="Yes", bg="#00FF00", fg="#000000")
            else:
                self.result_status.config(text="No", bg="#FF0000", fg="#FFFFFF")
        except Exception as e:
            self.result_status.config(text="Error", bg="#FFCC00", fg="#000000")
            print(f"Error checking requirements: {e}")

    # The remaining methods (get_gpu_info, get_network_info) are not used in the above functions but can be added if needed.

if __name__ == "__main__":
    root = tk.Tk()
    root.title("System Information")
    root.geometry("1000x800")
    app = System(root)
    app.pack(fill=tk.BOTH, expand=True)
    root.mainloop()
