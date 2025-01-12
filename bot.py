import tkinter as tk
from tkinter import messagebox

class Bot(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.configure(bg="#1E1E2E")

        # Title
        title_label = tk.Label(
            self, text="Bot Management", font=("Segoe UI", 14, "bold"), fg="#FFFFFF", bg="#1E1E2E"
        )
        title_label.pack(pady=(10, 20))

        # Start Bot Button
        start_bot_button = tk.Button(
            self,
            text="Start Bot",
            command=self.start_bot,
            font=("Segoe UI", 10, "bold"),
            bg="#44475A",
            fg="#FFFFFF",
            relief="flat",
            padx=10,
            pady=5,
        )
        start_bot_button.pack(pady=10)

        # Stop Bot Button
        stop_bot_button = tk.Button(
            self,
            text="Stop Bot",
            command=self.stop_bot,
            font=("Segoe UI", 10, "bold"),
            bg="#44475A",
            fg="#FFFFFF",
            relief="flat",
            padx=10,
            pady=5,
        )
        stop_bot_button.pack(pady=10)

        # Status Label
        self.status_label = tk.Label(
            self, text="Bot Status: Stopped", font=("Segoe UI", 10), fg="#FFFFFF", bg="#1E1E2E"
        )
        self.status_label.pack(pady=(20, 0))

    def start_bot(self):
        # Placeholder logic to start the bot
        messagebox.showinfo("Bot", "Starting the bot...")
        self.status_label.config(text="Bot Status: Running")

    def stop_bot(self):
        # Placeholder logic to stop the bot
        messagebox.showinfo("Bot", "Stopping the bot...")
        self.status_label.config(text="Bot Status: Stopped")

if __name__ == "__main__":
    root = tk.Tk()
    root.title("Bot Management")
    root.geometry("400x300")
    root.configure(bg="#1E1E2E")

    bot_page = Bot(root)
    bot_page.pack(fill="both", expand=True)

    root.mainloop()
