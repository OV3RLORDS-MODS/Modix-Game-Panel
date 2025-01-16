import tkinter as tk
from tkinter import Menu, messagebox, ttk
import requests

# Placeholder imports for ModixApp functionality
from terminal import Terminal
from file_manager import FileManager
from player_management import PlayerManagement
from mods import Mods
from discord_tools import DiscordTools
from system import System
from update import Update

SERVER_URL = "http://45.10.161.92:5050"  # Replace with your server's URL

class ModixApp(tk.Tk):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.title("Modix - Game Server Manager V1.0.2")
        self.geometry("1000x600")
        self.configure(bg="#1E1E2E")  # Dark background

        # Styling
        self.primary_bg = "#1E1E2E"
        self.sidebar_bg = "#282A36"
        self.button_color = "#44475A"
        self.hover_color = "#6272A4"
        self.font_style = ("Segoe UI", 10)
        self.button_font = ("Segoe UI", 10, "bold")

        # Track if the user is logged in
        self.logged_in = False
        self.username = ""

        # Main Layout
        main_frame = tk.Frame(self, bg=self.primary_bg)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Sidebar
        self.sidebar_frame = tk.Frame(main_frame, bg=self.sidebar_bg, width=200)
        self.sidebar_frame.pack(side=tk.LEFT, fill=tk.Y)

        # Main Content Area
        self.content_frame = tk.Frame(main_frame, bg=self.primary_bg)
        self.content_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # Create Sidebar Widgets
        self.create_sidebar_widgets()

        # Default Tab
        self.current_tab = None
        self.show_terminal_tab()

    def create_sidebar_widgets(self):
        # Sidebar Header
        header_label = tk.Label(
            self.sidebar_frame,
            text="Modix",
            bg=self.sidebar_bg,
            fg="#FFFFFF",
            font=("Segoe UI", 14, "bold"),
            pady=10,
        )
        header_label.pack(pady=(10, 10))

        # Sidebar Buttons
        buttons = [
            ("💻 Terminal", self.show_terminal_tab),
            ("📁 Files", self.show_file_manager_tab),
            ("🔧 Mods", self.show_mod_manager_tab),
            ("👥 Players", self.show_player_management_tab),
            ("👨 Staff", self.show_staff_tab),
            ("🔑 Licenses", self.show_licenses_tab),
        ]

        for text, command in buttons:
            self.create_sidebar_button(text, command)

        self.add_tools_button()
        self.create_sidebar_button("❓ Help", self.show_help_tab)

        # Login/Logout Button
        self.login_logout_button = tk.Button(
            self.sidebar_frame,
            text="Login",  # Default text
            command=self.toggle_login_logout,  # Command for toggling login/logout
            bg="#FF5555",
            fg="#FFFFFF",
            font=self.button_font,
            relief="flat",
            padx=10,
            pady=5,
        )
        self.login_logout_button.pack(side=tk.BOTTOM, fill=tk.X, pady=(20, 10))

    def create_sidebar_button(self, text, command):
        button = tk.Button(
            self.sidebar_frame,
            text=text,
            command=command,
            bg=self.button_color,
            fg="#FFFFFF",
            font=self.button_font,
            anchor="w",
            relief="flat",
            padx=10,
            pady=5,
        )
        button.pack(fill=tk.X, pady=5, padx=10)

        if not self.logged_in:
            # Disable the button if user is not logged in
            button.config(state=tk.DISABLED)
            # Add a tooltip that explains why the button is disabled
            button.bind("<Enter>", lambda e, b=button: self.show_tooltip(b, "You must be logged in to use this."))
            button.bind("<Leave>", lambda e, b=button: self.hide_tooltip(b))

        button.bind("<Enter>", lambda e, b=button: b.config(bg=self.hover_color))
        button.bind("<Leave>", lambda e, b=button: b.config(bg=self.button_color))

    def show_tooltip(self, button, message):
        """Show tooltip message when the user hovers over a disabled button."""
        self.tooltip = tk.Label(
            self.sidebar_frame, text=message, fg="#FFFFFF", bg="#282A36", font=("Segoe UI", 8)
        )
        self.tooltip.place(x=button.winfo_x() + button.winfo_width(), y=button.winfo_y())

    def hide_tooltip(self, button):
        """Hide the tooltip when mouse leaves the button."""
        if hasattr(self, 'tooltip'):
            self.tooltip.place_forget()

    def add_tools_button(self):
        """Creates a Tools menu button with submenu items."""
        tools_button = tk.Menubutton(
            self.sidebar_frame,
            text="🔨 Tools",
            bg=self.button_color,
            fg="#FFFFFF",
            font=self.button_font,
            anchor="w",
            relief="flat",
            padx=10,
            pady=5,
            activebackground=self.hover_color,
        )

        # Create the menu for Tools
        tools_menu = Menu(tools_button, tearoff=0, bg=self.sidebar_bg, fg="#FFFFFF", font=self.font_style)
        tools_button["menu"] = tools_menu

        tools_menu.add_command(label="Anticheat", command=self.show_anticheat_tab)
        tools_menu.add_command(label="Bot", command=self.show_bot_tab)
        tools_menu.add_command(label="Webhooks", command=self.show_webhooks_tab)
        tools_menu.add_command(label="System", command=self.show_system_tab)
        tools_menu.add_separator()
        tools_menu.add_command(label="Update", command=self.show_update_tab)

        tools_button.pack(fill=tk.X, pady=5, padx=10)

    def show_terminal_tab(self):
        self.switch_tab(Terminal(self.content_frame, bg=self.primary_bg))

    def show_file_manager_tab(self):
        self.switch_tab(FileManager(self.content_frame))

    def show_player_management_tab(self):
        self.switch_tab(PlayerManagement(self.content_frame))

    def show_mod_manager_tab(self):
        self.switch_tab(Mods(self.content_frame, "YOUR_STEAM_API_KEY", self.username))

    def show_help_tab(self):
        self.switch_tab(HelpPage(self.content_frame))

    def show_staff_tab(self):
        self.switch_tab(PlayerManagement(self.content_frame))

    def show_anticheat_tab(self):
        self.switch_tab(PlayerManagement(self.content_frame))

    def show_bot_tab(self):
        self.switch_tab(PlayerManagement(self.content_frame))

    def show_webhooks_tab(self):
        self.switch_tab(DiscordTools(self.content_frame))

    def show_system_tab(self):
        self.switch_tab(System(self.content_frame))

    def show_update_tab(self):
        self.switch_tab(Update(self.content_frame))

    def show_licenses_tab(self):
        self.switch_tab(LicensesTab(self.content_frame))

    def switch_tab(self, new_tab):
        if self.current_tab:
            self.current_tab.destroy()
        self.current_tab = new_tab
        self.current_tab.pack(fill=tk.BOTH, expand=True)

    def toggle_login_logout(self):
        """Toggle between login and logout functionality."""
        if self.logged_in:
            self.logout()
        else:
            self.login_dialog()

    def login_dialog(self):
        """Open a pop-up window to get username and password."""
        login_window = tk.Toplevel(self)
        login_window.title("Login")
        login_window.geometry("400x300")
        login_window.configure(bg="#2E2E2E")
        
        # Header Label
        tk.Label(login_window, text="Login to Modix", bg="#2E2E2E", fg="#FFFFFF", font=("Segoe UI", 14, "bold")).pack(pady=10)

        # Username Label and Entry
        tk.Label(login_window, text="Username", fg="#FFFFFF", bg="#2E2E2E", font=("Segoe UI", 10)).pack(pady=5)
        username_entry = tk.Entry(login_window, font=("Segoe UI", 10), bg="#44475A", fg="#FFFFFF", relief="flat", bd=0, justify="center")
        username_entry.pack(pady=5, ipady=5, ipadx=10, fill=tk.X)

        # Password Label and Entry
        tk.Label(login_window, text="Password", fg="#FFFFFF", bg="#2E2E2E", font=("Segoe UI", 10)).pack(pady=5)
        password_entry = tk.Entry(login_window, font=("Segoe UI", 10), bg="#44475A", fg="#FFFFFF", show="*", relief="flat", bd=0, justify="center")
        password_entry.pack(pady=5, ipady=5, ipadx=10, fill=tk.X)

        # Signup/Sign In Toggle Label
        sign_up_label = tk.Label(login_window, text="Don't have an account? Sign up", fg="#6272A4", bg="#2E2E2E", font=("Segoe UI", 9, "italic"))
        sign_up_label.pack(pady=10)
        sign_up_label.bind("<Button-1>", lambda e: self.signup_dialog(login_window))  # Open signup when clicked

        # Login Button
        login_button = tk.Button(login_window, text="Login", command=lambda: self.attempt_login(username_entry.get(), password_entry.get(), login_window),
                                 bg="#FF5555", fg="#FFFFFF", font=("Segoe UI", 10), relief="flat", padx=10, pady=5)
        login_button.pack(pady=20)

    def attempt_login(self, username, password, login_window):
        """Attempt login."""
        try:
            response = requests.post(f"{SERVER_URL}/login", json={"username": username, "password": password})
            if response.status_code == 200:
                messagebox.showinfo("Success", "Logged in successfully!")
                self.logged_in = True
                self.username = username
                self.update_login_button()  # Update button text after login
                self.enable_sidebar_buttons()  # Enable buttons after login
                login_window.destroy()  # Close the login window
            else:
                messagebox.showerror("Error", response.json().get("error", "Failed to log in."))
        except Exception as e:
            messagebox.showerror("Error", f"Could not connect to server: {e}")

    def signup_dialog(self, login_window):
        """Open a pop-up window for user signup."""
        signup_window = tk.Toplevel(self)
        signup_window.title("Sign Up")
        signup_window.geometry("400x350")
        signup_window.configure(bg="#2E2E2E")

        # Header Label
        tk.Label(signup_window, text="Sign Up to Modix", bg="#2E2E2E", fg="#FFFFFF", font=("Segoe UI", 14, "bold")).pack(pady=10)

        # Username Label and Entry
        tk.Label(signup_window, text="Username", fg="#FFFFFF", bg="#2E2E2E", font=("Segoe UI", 10)).pack(pady=5)
        username_entry = tk.Entry(signup_window, font=("Segoe UI", 10), bg="#44475A", fg="#FFFFFF", relief="flat", bd=0, justify="center")
        username_entry.pack(pady=5, ipady=5, ipadx=10, fill=tk.X)

        # Email Label and Entry
        tk.Label(signup_window, text="Email", fg="#FFFFFF", bg="#2E2E2E", font=("Segoe UI", 10)).pack(pady=5)
        email_entry = tk.Entry(signup_window, font=("Segoe UI", 10), bg="#44475A", fg="#FFFFFF", relief="flat", bd=0, justify="center")
        email_entry.pack(pady=5, ipady=5, ipadx=10, fill=tk.X)

        # Password Label and Entry
        tk.Label(signup_window, text="Password", fg="#FFFFFF", bg="#2E2E2E", font=("Segoe UI", 10)).pack(pady=5)
        password_entry = tk.Entry(signup_window, font=("Segoe UI", 10), bg="#44475A", fg="#FFFFFF", show="*", relief="flat", bd=0, justify="center")
        password_entry.pack(pady=5, ipady=5, ipadx=10, fill=tk.X)

        # Confirm Password Label and Entry
        tk.Label(signup_window, text="Confirm Password", fg="#FFFFFF", bg="#2E2E2E", font=("Segoe UI", 10)).pack(pady=5)
        confirm_password_entry = tk.Entry(signup_window, font=("Segoe UI", 10), bg="#44475A", fg="#FFFFFF", show="*", relief="flat", bd=0, justify="center")
        confirm_password_entry.pack(pady=5, ipady=5, ipadx=10, fill=tk.X)

        # Sign Up Button
        signup_button = tk.Button(signup_window, text="Sign Up", command=lambda: self.attempt_signup(username_entry.get(), email_entry.get(), password_entry.get(), confirm_password_entry.get(), signup_window),
                                  bg="#FF5555", fg="#FFFFFF", font=("Segoe UI", 10), relief="flat", padx=10, pady=5)
        signup_button.pack(pady=20)

    def attempt_signup(self, username, email, password, confirm_password, signup_window):
        """Attempt signup."""
        if password != confirm_password:
            messagebox.showerror("Error", "Passwords do not match.")
            return

        try:
            response = requests.post(f"{SERVER_URL}/signup", json={"username": username, "password": password, "email": email})
            if response.status_code == 201:
                messagebox.showinfo("Success", "User created successfully!")
                signup_window.destroy()  # Close the signup window
                self.login_dialog()  # Open login dialog after successful signup
            else:
                messagebox.showerror("Error", response.json().get("error", "Signup failed."))
        except Exception as e:
            messagebox.showerror("Error", f"Could not connect to server: {e}")

    def logout(self):
        """Log the user out and update UI."""
        try:
            response = requests.post(f"{SERVER_URL}/logout")
            if response.status_code == 200:
                messagebox.showinfo("Success", "Logged out successfully!")
                self.logged_in = False
                self.username = ""
                self.update_login_button()  # Update button text after logout
                self.disable_sidebar_buttons()  # Disable buttons after logout
            else:
                messagebox.showerror("Error", f"Logout failed: {response.json().get('error')}")
        except Exception as e:
            messagebox.showerror("Error", f"Could not connect to server: {e}")

    def update_login_button(self):
        """Update the login/logout button based on login state."""
        if self.logged_in:
            self.login_logout_button.config(text="Logout")
        else:
            self.login_logout_button.config(text="Login")

    def disable_sidebar_buttons(self):
        """Disable all sidebar buttons except for the Login/Logout button."""
        for button in self.sidebar_frame.winfo_children():
            if button != self.login_logout_button:
                button.config(state=tk.DISABLED)

    def enable_sidebar_buttons(self):
        """Enable all sidebar buttons after successful login."""
        for button in self.sidebar_frame.winfo_children():
            if button != self.login_logout_button:
                button.config(state=tk.NORMAL)


if __name__ == "__main__":
    ModixApp().mainloop()
