import tkinter as tk
from tkinter import ttk, messagebox
import requests
import webbrowser

# Define your Discord bot URL here
DISCORD_BOT_URL = 'http://your-discord-bot-url/verify_code'

class MainApp(tk.Tk):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.title("GSMGame Server Manager V1.0.0")
        self.geometry("1000x700")
        self.configure(bg="#2E2E2E")

        # Define styling variables
        self.primary_bg = "#2E2E2E"
        self.highlight_color = "#4CAF50"
        self.hover_color = "#424242"
        self.font_style = ("Segoe UI", 10)
        self.button_style = "flat"

        self.create_main_frame()
        self.create_sidebar()
        self.create_tabs()
        self.show_terminal_tab()
        self.trigger_verification_on_startup()

    def create_main_frame(self):
        """Create and configure the main frame and notebook."""
        self.main_frame = tk.Frame(self, bg=self.primary_bg)
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        self.notebook = ttk.Notebook(self.main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    def create_sidebar(self):
        """Create and configure the sidebar with navigation buttons."""
        self.sidebar_frame = tk.Frame(self.main_frame, bg=self.primary_bg, width=200)
        self.sidebar_frame.pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=5)

        self.create_sidebar_header()
        self.create_sidebar_buttons()

    def create_sidebar_header(self):
        """Create the header widgets in the sidebar."""
        tk.Label(self.sidebar_frame, text="GSM", bg=self.primary_bg, fg="#FFFFFF",
                 font=("Segoe UI", 16, "bold")).pack(pady=(10, 5))

        tk.Label(self.sidebar_frame, text="Server Manager", bg=self.primary_bg, fg="#FFFFFF",
                 font=self.font_style).pack(pady=(0, 20))

    def create_sidebar_buttons(self):
        """Create and place sidebar navigation buttons."""
        buttons = {
            "Terminal": self.show_terminal_tab,
            "Info": self.show_info_tab,
            "Discord": self.open_discord_link,
            "Game Settings": self.show_game_settings_tab
        }

        for text, command in buttons.items():
            self.create_sidebar_button(text, command)

        self.create_verify_button()

    def create_sidebar_button(self, text, command):
        """Create a button in the sidebar."""
        button = tk.Button(self.sidebar_frame, text=text, command=command, bg=self.highlight_color, fg="#FFFFFF",
                           font=self.font_style, width=20, relief=self.button_style, pady=5, padx=5)
        button.pack(pady=5, padx=5, fill=tk.X)
        button.bind("<Enter>", lambda e, b=button: b.config(bg=self.hover_color))
        button.bind("<Leave>", lambda e, b=button: b.config(bg=self.highlight_color))

    def create_verify_button(self):
        """Create the 'Verify' button at the bottom of the sidebar."""
        verify_button = tk.Button(self.sidebar_frame, text="Discord/Help", command=self.open_verification_window, 
                                  bg="#FF5722", fg="#FFFFFF", font=self.font_style, width=20, relief=self.button_style)
        verify_button.pack(side=tk.BOTTOM, pady=10, padx=5, fill=tk.X)
        verify_button.bind("<Enter>", lambda e, b=verify_button: b.config(bg="#E64A19"))
        verify_button.bind("<Leave>", lambda e, b=verify_button: b.config(bg="#FF5722"))

    def create_tabs(self):
        """Create and add tabs to the notebook."""
        self.terminal_tab = Terminal(self.notebook, bg="#1E1E1E")
        self.mod_manager_tab = ModManager(self.notebook, "YOUR_STEAM_API_KEY")
        self.player_management_tab = PlayerManagement(self.notebook)
        self.discord_tools_tab = DiscordTools(self.notebook)
        self.info_tab = Info(self.notebook)
        self.game_settings_tab = GameSettings(self.notebook)

        tabs = {
            "Terminal": self.terminal_tab,
            "Mod Manager": self.mod_manager_tab,
            "Player Management": self.player_management_tab,
            "Discord Tools": self.discord_tools_tab,
            "Info": self.info_tab,
            "Game Settings": self.game_settings_tab
        }

        for text, tab in tabs.items():
            self.notebook.add(tab, text=text)

    def trigger_verification_on_startup(self):
        """Open the verification window on startup."""
        self.open_verification_window()

    def open_verification_window(self):
        """Create and display the verification window."""
        self.verify_window = tk.Toplevel(self)
        self.verify_window.title("GSM Verification")
        self.verify_window.geometry("400x300")
        self.verify_window.configure(bg=self.primary_bg)

        tk.Label(self.verify_window, text="Verification Required", bg=self.primary_bg, fg="#FFFFFF",
                 font=("Segoe UI", 16, "bold")).pack(pady=10)

        tk.Label(self.verify_window, text="Enter Verification Code:", bg=self.primary_bg, fg="#FFFFFF",
                 font=self.font_style).pack(pady=(10, 5))

        self.code_entry = tk.Entry(self.verify_window, font=self.font_style)
        self.code_entry.pack(pady=5)

        tk.Button(self.verify_window, text="Verify", command=self.verify_code, bg=self.highlight_color,
                  fg="#FFFFFF", font=self.font_style).pack(pady=10)

        tk.Button(self.verify_window, text="Cancel", command=self.verify_window.destroy, bg="#FF5722",
                  fg="#FFFFFF", font=self.font_style).pack(pady=10)

    def verify_code(self):
        """Verify the entered code with the Discord bot."""
        code = self.code_entry.get()
        user_id = "123456789"  # Replace with actual user ID or method to get it dynamically

        if self.verify_code_with_discord_bot(code, user_id):
            messagebox.showinfo("Success", "Verification successful!")
            self.verify_window.destroy()
        else:
            messagebox.showerror("Error", "Invalid verification code. Please try again.")

    def verify_code_with_discord_bot(self, code, user_id):
        """Send the verification request to the Discord bot."""
        data = {"user_id": user_id, "code": code}
        try:
            response = requests.post(DISCORD_BOT_URL, json=data)
            return response.status_code == 200
        except requests.exceptions.RequestException:
            messagebox.showerror("Error", "Failed to contact Discord bot.")
            return False

    def show_terminal_tab(self):
        """Switch to the Terminal tab."""
        self.notebook.select(self.terminal_tab)

    def show_info_tab(self):
        """Switch to the Info tab."""
        self.notebook.select(self.info_tab)

    def open_discord_link(self):
        """Open the Discord website."""
        webbrowser.open("https://discord.com")

    def show_game_settings_tab(self):
        """Switch to the Game Settings tab."""
        self.notebook.select(self.game_settings_tab)

if __name__ == "__main__":
    app = MainApp()
    app.mainloop()