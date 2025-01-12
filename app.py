import tkinter as tk
from tkinter import Menu, messagebox

# Import your modules
from help import HelpPage
from terminal import Terminal
from file_manager import FileManager
from mod_manager import ModManager
from player_management import PlayerManagement
from discord_tools import DiscordTools  # Webhooks now shows this
from info import Info
from system import System
from mods import Mods


class ModixApp(tk.Tk):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.title("Modix - Game Server Manager V1.0.2")
        self.geometry("1000x600")
        self.configure(bg="#1E1E2E")  # Dark background

        # Styling
        self.primary_bg = "#1E1E2E"
        self.sidebar_bg = "#282A36"  # Darker sidebar background
        self.button_color = "#44475A"  # Button color
        self.hover_color = "#6272A4"   # Hover effect
        self.font_style = ("Segoe UI", 10)
        self.button_font = ("Segoe UI", 10, "bold")

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
        ]

        for text, command in buttons:
            self.create_sidebar_button(text, command)

        # Tools Submenu
        self.add_tools_button()

        # Help Button
        self.create_sidebar_button("❓ Help", self.show_help_tab)

    def create_sidebar_button(self, text, command):
        """Create a standard sidebar button with consistent styling."""
        button = tk.Button(
            self.sidebar_frame,
            text=text,
            command=command,
            bg=self.button_color,
            fg="#FFFFFF",
            font=self.button_font,
            anchor="w",
            relief="flat",
            borderwidth=0,
            padx=10,
            pady=5,
            width=20,  # Force consistent width for all buttons
        )
        button.pack(fill=tk.X, pady=5, padx=10)
        button.bind("<Enter>", lambda e, b=button: b.config(bg=self.hover_color))
        button.bind("<Leave>", lambda e, b=button: b.config(bg=self.button_color))

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
            borderwidth=0,
            padx=10,
            pady=5,
            activebackground=self.hover_color,
        )

        # Create the menu for Tools
        tools_menu = Menu(tools_button, tearoff=0, bg=self.sidebar_bg, fg="#FFFFFF", font=self.font_style)
        tools_button["menu"] = tools_menu

        # Tools submenu items
        tools_menu.add_command(label="Anticheat", command=self.show_anticheat_tab)
        tools_menu.add_command(label="Bot", command=self.show_bot_tab)
        tools_menu.add_command(label="Webhooks", command=self.show_webhooks_tab)
        tools_menu.add_separator()
        tools_menu.add_command(label="Update", command=self.show_update_tab)

        tools_button.pack(fill=tk.X, pady=5, padx=10)

    # ----------------- Tools submenu handlers -----------------
    def show_anticheat_tab(self):
        """Anticheat behaves like Players."""
        self.switch_tab(PlayerManagement(self.content_frame))

    def show_bot_tab(self):
        """Bot behaves like Players."""
        self.switch_tab(PlayerManagement(self.content_frame))

    def show_webhooks_tab(self):
        """Webhooks now shows Discord Tools."""
        self.switch_tab(DiscordTools(self.content_frame))

    def show_update_tab(self):
        messagebox.showinfo("Update", "Checking for updates... (Placeholder)")

    # ----------------- Show Help Tab -----------------
    def show_help_tab(self):
        """Switch to the new HelpPage from help.py."""
        self.switch_tab(HelpPage(self.content_frame))

    # ----------------- Switch Tab Logic -----------------
    def switch_tab(self, new_tab):
        # If there's a currently displayed tab, destroy it
        if self.current_tab:
            self.current_tab.destroy()

        self.current_tab = new_tab
        # Pack this new tab
        self.current_tab.pack(fill=tk.BOTH, expand=True)

    # ----------------- Main Tab Handlers -----------------
    def show_terminal_tab(self):
        self.switch_tab(Terminal(self.content_frame, bg=self.primary_bg))

    def show_file_manager_tab(self):
        self.switch_tab(FileManager(self.content_frame))

    def show_mod_manager_tab(self):
        self.switch_tab(Mods(self.content_frame, "YOUR_STEAM_API_KEY"))

    def show_player_management_tab(self):
        self.switch_tab(PlayerManagement(self.content_frame))

    def show_staff_tab(self):
        """Show the same tab as Players."""
        self.switch_tab(PlayerManagement(self.content_frame))


if __name__ == "__main__":
    app = ModixApp()
    app.mainloop()
