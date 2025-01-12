import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import psutil
import socket
import platform
from datetime import datetime

class System(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.configure(bg="#1E1E1E")

        # Title Section
        title_frame = tk.Frame(self, bg="#1E1E1E")
        title_frame.pack(pady=20, fill=tk.X)

        title_label = tk.Label(title_frame, text="System Information", bg="#1E1E1E", fg="#FFFFFF", font=("Segoe UI", 22, "bold"))
        title_label.pack()

        subtitle_label = tk.Label(title_frame, text="Comprehensive System Overview and Project Zomboid Server Compatibility", 
                                  bg="#1E1E1E", fg="#CCCCCC", font=("Segoe UI", 12, "italic"))
        subtitle_label.pack()

        # Requirements Frame
        self.requirements_frame = tk.LabelFrame(self, text="Project Zomboid Server Requirements", bg="#2E2E2E", fg="#FFFFFF", 
                                                font=("Segoe UI", 12, "bold"), bd=2, relief=tk.GROOVE)
        self.requirements_frame.pack(fill=tk.X, padx=10, pady=5)

        self.create_requirements_widgets()

        # System Info Frame
        self.info_frame = tk.LabelFrame(self, text="Detailed System Information", bg="#2E2E2E", fg="#FFFFFF", 
                                        font=("Segoe UI", 12, "bold"), bd=2, relief=tk.GROOVE)
        self.info_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.info_text = tk.Text(self.info_frame, bg="#1E1E1E", fg="#FFFFFF", font=("Segoe UI", 10), wrap=tk.WORD, height=20)
        self.info_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Scrollbars
        self.v_scroll = tk.Scrollbar(self.info_frame, orient=tk.VERTICAL, command=self.info_text.yview)
        self.v_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.info_text.config(yscrollcommand=self.v_scroll.set)

        self.h_scroll = tk.Scrollbar(self.info_frame, orient=tk.HORIZONTAL, command=self.info_text.xview)
        self.h_scroll.pack(side=tk.BOTTOM, fill=tk.X)
        self.info_text.config(xscrollcommand=self.h_scroll.set)

        # Update button
        self.update_button = tk.Button(self, text="Update Info", command=self.update_info, bg="#4CAF50", fg="#FFFFFF",
                                       font=("Segoe UI", 12, "bold"))
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
            tk.Label(self.requirements_frame, text=f"{key}:", bg="#2E2E2E", fg="#FFFFFF", font=("Segoe UI", 10)).grid(row=row, column=0, padx=10, pady=5, sticky="w")
            value_label = tk.Label(self.requirements_frame, text=value, bg="#2E2E2E", fg="#FFFFFF", font=("Segoe UI", 10))
            value_label.grid(row=row, column=1, padx=10, pady=5, sticky="w")
            self.requirement_labels[key] = value_label
            row += 1

        # Result label for requirements check
        self.result_label = tk.Label(self.requirements_frame, text="Can I run it?", bg="#FFCC00", fg="#000000", 
                                     font=("Segoe UI", 12, "bold"))
        self.result_label.grid(row=row, column=0, padx=10, pady=10, sticky="w")

        self.result_status = tk.Label(self.requirements_frame, text="Checking...", bg="#FFCC00", fg="#000000", 
                                      font=("Segoe UI", 12, "bold"))
        self.result_status.grid(row=row, column=1, padx=10, pady=10, sticky="w")

    def get_system_info(self):
        try:
            uname = platform.uname()
            cpu_freq = psutil.cpu_freq().current / 1000  # GHz
            memory_info = psutil.virtual_memory()
            disk_info = psutil.disk_usage('/')
            ip_address = socket.gethostbyname(socket.gethostname())
            cpu_cores = psutil.cpu_count(logical=True)
            gpu_info = self.get_gpu_info()
            network_info = self.get_network_info()
            uptime = self.format_uptime(psutil.boot_time())

            # Placeholder for network speeds
            download_speed = 1  # Mbps
            upload_speed = 1    # Mbps

            # System info
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
                "Download Speed (Mbps)": f"{download_speed} Mbps",
                "Upload Speed (Mbps)": f"{upload_speed} Mbps",
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
            # Placeholder for DirectX version detection
            return "12"  # Example DirectX version
        except Exception as e:
            return "Unknown"

    def get_gpu_info(self):
        try:
            # Placeholder for GPU information
            return "NVIDIA GeForce GTX 1060"  # Example GPU info
        except Exception as e:
            return "Unknown"

    def get_network_info(self):
        try:
            interfaces = psutil.net_if_addrs()
            info = []
            for interface, addrs in interfaces.items():
                for addr in addrs:
                    info.append(f"{interface}: {addr.address} ({addr.family})")
            return "\n".join(info) if info else "No network interfaces found"
        except Exception as e:
            return "Error retrieving network information"

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

        # Check if system meets the Project Zomboid server requirements
        self.check_requirements()

        # Add a timestamp of when the information was last updated
        self.info_text.insert(tk.END, f"\nUpdated at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    def check_requirements(self):
        try:
            # Project Zomboid server requirements
            req_cpu_freq = 2.5  # GHz
            req_memory = 8      # GB
            req_disk_space = 20 # GB
            req_download_speed = 1  # Mbps
            req_upload_speed = 1    # Mbps
            req_directx_version = "11"

            system_info = self.get_system_info()

            cpu_freq = float(system_info.get("CPU Frequency (GHz)", "0").split()[0])
            memory_info = float(system_info.get("Total RAM (GB)", "0").split()[0])
            disk_info = float(system_info.get("Total Disk Space (GB)", "0").split()[0])
            download_speed = float(system_info.get("Download Speed (Mbps)", "0").split()[0])
            upload_speed = float(system_info.get("Upload Speed (Mbps)", "0").split()[0])
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

# Example usage in a Tkinter application
if __name__ == "__main__":
    root = tk.Tk()
    root.title("System Information")
    root.geometry("1000x800")
    app = System(root)
    app.pack(fill=tk.BOTH, expand=True)
    root.mainloop()