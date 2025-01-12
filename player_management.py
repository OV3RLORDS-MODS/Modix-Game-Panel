import tkinter as tk

class PlayerManagement(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg="#1E1E1E")
        self.pack(fill=tk.BOTH, expand=True)
        self.show_under_development_message()

    def show_under_development_message(self):
        """Display a message indicating that this section is still under development."""
        message = "This section is still under development."
        tk.Label(self, text=message, bg="#1E1E1E", fg="#FFFFFF", font=("Segoe UI", 12)).pack(pady=20)

if __name__ == "__main__":
    root = tk.Tk()
    root.title("Player Management")
    root.geometry("500x400")
    app = PlayerManagement(root)
    app.pack(fill=tk.BOTH, expand=True)
    root.mainloop()
