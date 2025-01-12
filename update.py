# update.py
import tkinter as tk
import requests

class Update(tk.Frame):
    def __init__(self, parent, current_version="1.0.2", *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        self.current_version = current_version
        self.latest_version = None
        self.update_url = "https://example.com/modix/latest"  # Replace with your real endpoint

        # Match your main background color
        self.configure(bg="#1E1E2E")

        # Create a sub-frame to center the content
        center_frame = tk.Frame(self, bg="#1E1E2E")
        center_frame.place(relx=0.5, rely=0.5, anchor="center")

        # Title Label
        title_label = tk.Label(
            center_frame,
            text="Modix Updater",
            font=("Segoe UI", 16, "bold"),
            fg="#FFFFFF",
            bg="#1E1E2E"
        )
        title_label.pack(pady=(20, 10))

        # **Warning Label** at top (bold, red)
        warning_label = tk.Label(
            center_frame,
            text=(
                "WARNING: This will override everything.\n"
                "Please make sure to create a backup before updating."
            ),
            font=("Segoe UI", 10, "bold"),
            fg="#FF5555",   # red text
            bg="#1E1E2E",
            justify="center"
        )
        warning_label.pack(pady=5)

        # Info Label (show current version)
        self.info_label = tk.Label(
            center_frame,
            text=f"Current Version: {self.current_version}",
            font=("Segoe UI", 12),
            fg="#FFFFFF",
            bg="#1E1E2E"
        )
        self.info_label.pack(pady=5)

        # Button to Check for Updates
        check_button = tk.Button(
            center_frame,
            text="Check for Updates",
            font=("Segoe UI", 10, "bold"),
            bg="#44475A",
            fg="#FFFFFF",
            relief="flat",
            bd=0,
            padx=15,  # extra padding for a nicer look
            pady=5,
            command=self.check_for_updates
        )
        check_button.pack(pady=(10, 10))

        # Label for status messages (below the Check button)
        self.status_label = tk.Label(
            center_frame,
            text="",
            font=("Segoe UI", 10),
            fg="#FFFFFF",
            bg="#1E1E2E",
            wraplength=300,  # Wrap text if it's too long
            justify="center"
        )
        self.status_label.pack(pady=5)

        # Button to Perform Update (disabled until a new version is found)
        self.update_button = tk.Button(
            center_frame,
            text="Perform Update",
            font=("Segoe UI", 10, "bold"),
            bg="#44475A",
            fg="#FFFFFF",
            relief="flat",
            bd=0,
            padx=15,
            pady=5,
            state=tk.DISABLED,
            command=self.perform_update
        )
        self.update_button.pack(pady=(5, 20))

    def check_for_updates(self):
        """
        Example function to check a remote endpoint for the latest version.
        Replace with real logic to get the version from your VPS or a release server.
        """
        self.status_label.config(text="Checking for updates...")
        self.update_button.config(state=tk.DISABLED)

        try:
            # Example: fetch the latest version text, e.g. "1.0.3"
            response = requests.get(self.update_url, timeout=5)
            response.raise_for_status()

            self.latest_version = response.text.strip()
            if self._is_newer_version(self.latest_version, self.current_version):
                self.status_label.config(
                    text=f"New version available: {self.latest_version}"
                )
                self.update_button.config(state=tk.NORMAL)
            else:
                self.status_label.config(
                    text=f"You are up-to-date! (Latest: {self.latest_version})"
                )
        except Exception as e:
            self.status_label.config(text=f"Error checking updates:\n{e}")

    def perform_update(self):
        """
        Example function to actually perform the update:
        - Download new files
        - Replace current files
        - Possibly restart the application
        """
        self.status_label.config(text="Performing update... (Placeholder)")
        # Implement your real update procedure here
        self.update_button.config(state=tk.DISABLED)

    def _is_newer_version(self, latest, current):
        """
        Simple example version check.
        Assumes versions are like "1.0.3".
        Convert them to tuples for comparison: (1,0,3) > (1,0,2).
        """
        def to_tuple(ver):
            return tuple(int(x) for x in ver.split(".") if x.isdigit())

        try:
            return to_tuple(latest) > to_tuple(current)
        except:
            return False
