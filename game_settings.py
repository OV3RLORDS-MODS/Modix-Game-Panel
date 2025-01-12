import tkinter as tk
from tkinter import ttk
from tkinter import font as tkfont
from tkinter import messagebox

class GameSettings(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.configure(bg="#2E2E2E")

        # Define fonts and colors
        self.title_font = tkfont.Font(family="Segoe UI", size=20, weight="bold")
        self.label_font = tkfont.Font(family="Segoe UI", size=12)
        self.entry_font = tkfont.Font(family="Segoe UI", size=10)
        self.bg_color = "#1E1E1E"
        self.fg_color = "#F0F0F0"
        self.highlight_color = "#4CAF50"
        self.tooltip_bg = "#333333"
        self.tooltip_fg = "#FFFFFF"
        self.tooltip_font = tkfont.Font(family="Segoe UI", size=9)

        # Title
        title_label = tk.Label(self, text="Game Settings", font=self.title_font, bg=self.bg_color, fg=self.fg_color)
        title_label.pack(pady=20)

        # Create a notebook for tabs
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        # Create tabs
        self.general_tab = tk.Frame(self.notebook, bg=self.bg_color)
        self.advanced_tab = tk.Frame(self.notebook, bg=self.bg_color)

        self.notebook.add(self.general_tab, text="General Settings")
        self.notebook.add(self.advanced_tab, text="Advanced Settings")

        # Create canvas and scrollbar for scrolling
        self.canvas = tk.Canvas(self.general_tab, bg=self.bg_color)
        self.scrollbar = tk.Scrollbar(self.general_tab, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.scrollbar.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)

        # Create a frame inside the canvas to hold all widgets
        self.settings_frame = tk.Frame(self.canvas, bg=self.bg_color)
        self.canvas.create_window((0, 0), window=self.settings_frame, anchor="nw")

        # Update scroll region
        self.settings_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))

        # Populate tabs with widgets
        self.create_general_settings()
        self.create_advanced_settings()

        # Save Button
        save_button = tk.Button(self, text="Save Settings", command=self.save_settings, bg=self.highlight_color, fg=self.fg_color, font=self.entry_font, relief="flat", padx=10, pady=5)
        save_button.pack(pady=20)

    def create_general_settings(self):
        """ Create general game settings with tooltips """
        settings = [
            ("Server Name:", "server_name", "Name of the server."),
            ("Max Players:", "max_players", "Maximum number of players allowed."),
            ("Game Mode:", "game_mode", "Choose the game mode.", ["Survival", "Creative", "Adventure"]),
            ("Difficulty:", "difficulty", "Set the difficulty level.", ["Easy", "Normal", "Hard"]),
            ("PvP Enabled:", "pvp_enabled", "Enable or disable player vs player combat.", None, "boolean"),
            ("Server Port:", "server_port", "Port on which the server will run."),
            ("Max Day Length (minutes):", "max_day_length", "Length of a game day in minutes."),
            ("Zombie Count:", "zombie_count", "Number of zombies in the game."),
            ("Starting Inventory:", "starting_inventory", "Initial items given to players."),
            ("Server Password:", "server_password", "Password to access the server.", None, "password"),
            ("Allow Cheats:", "allow_cheats", "Enable or disable cheats.", None, "boolean"),
            ("Weather Settings:", "weather_settings", "Weather conditions available.", ["Clear", "Rain", "Snow"]),
            ("Public Server:", "public_server", "Show the server on the in-game browser.", None, "boolean"),
            ("Public Name:", "public_name", "Name of the server displayed in the browser."),
            ("Public Description:", "public_description", "Description displayed in the public server browser."),
            ("Player Respawn With Self:", "player_respawn_with_self", "Allow players to respawn at their death location.", None, "boolean"),
            ("Player Respawn With Other:", "player_respawn_with_other", "Allow players to respawn at a split-screen/Remote Play player's location.", None, "boolean"),
            ("Safehouse Allow Loot:", "safehouse_allow_loot", "Allow non-members to take items from safehouses.", None, "boolean"),
            ("Safehouse Allow Respawn:", "safehouse_allow_respawn", "Players will respawn in a safehouse they were a member of before they died.", None, "boolean"),
            ("Faction:", "faction", "Players can create factions."),
            ("Faction Day Survived To Create:", "faction_day_survived_to_create", "Number of days players need to survive before creating a faction."),
            ("Faction Players Required For Tag:", "faction_players_required_for_tag", "Number of players required as faction members before creating a group tag."),
        ]

        self.create_settings_in_frame(self.settings_frame, settings)

    def create_advanced_settings(self):
        """ Create advanced game settings with tooltips """
        settings = [
            ("Zombie Respawn Rate:", "zombie_respawn_rate", "Rate at which zombies respawn."),
            ("Zombie Spawn Count:", "zombie_spawn_count", "Number of zombies spawned at a time."),
            ("Loot Respawn Time:", "loot_respawn_time", "Time in minutes for loot to respawn."),
            ("Day/Night Cycle Length (minutes):", "cycle_length", "Length of the day/night cycle."),
            ("Vehicle Spawn Rate:", "vehicle_spawn_rate", "Rate at which vehicles spawn."),
            ("Global Events Frequency:", "events_frequency", "Frequency of global events."),
            ("Ping Limit:", "ping_limit", "Ping limit before a player is kicked from the server."),
            ("Backups Period:", "backups_period", "Number of minutes between backups."),
            ("Anti-Cheat Protection Type 1-24:", "anti_cheat_protection_type", "Various anti-cheat protection settings.")
        ]

        self.create_settings_in_frame(self.settings_frame, settings)

    def create_settings_in_frame(self, frame, settings):
        """ Create settings in a given frame """
        for idx, setting in enumerate(settings):
            label_text, setting_name, tooltip_text = setting[:3]
            values = setting[3] if len(setting) > 3 else None
            type = setting[4] if len(setting) > 4 else "text"
            self.create_setting(frame, label_text, setting_name, tooltip_text, row=idx, values=values, type=type)

    def create_setting(self, frame, label_text, setting_name, tooltip_text, row, values=None, type="text"):
        """ Helper function to create a setting entry with a label and tooltip """
        label = tk.Label(frame, text=label_text, bg=self.bg_color, fg=self.fg_color, font=self.label_font)
        label.grid(row=row, column=0, sticky=tk.W, padx=5, pady=5)

        if type == "boolean":
            var = tk.BooleanVar()
            entry = tk.Checkbutton(frame, variable=var, bg=self.bg_color, fg=self.fg_color, font=self.entry_font, selectcolor=self.highlight_color)
            entry.var = var  # Store the variable in the widget
        elif type == "password":
            entry = tk.Entry(frame, show="*", font=self.entry_font, bg="#333333", fg=self.fg_color, insertbackground='white')
        elif values:
            entry = ttk.Combobox(frame, values=values, font=self.entry_font, state="readonly", background="#333333", foreground=self.fg_color)
        else:
            entry = tk.Entry(frame, font=self.entry_font, bg="#333333", fg=self.fg_color, insertbackground='white')

        entry.grid(row=row, column=1, padx=5, pady=5, sticky=tk.EW)
        setattr(self, f"{setting_name}_entry", entry)

        # Add tooltip
        self.create_tooltip(entry, tooltip_text)

    def create_tooltip(self, widget, text):
        """ Create a tooltip for a given widget """
        tooltip = tk.Toplevel(self)
        tooltip.wm_overrideredirect(True)
        tooltip.config(bg=self.tooltip_bg)

        label = tk.Label(tooltip, text=text, background=self.tooltip_bg, foreground=self.tooltip_fg, relief="solid", borderwidth=1, font=self.tooltip_font, padx=5, pady=5)
        label.pack()

        def show_tooltip(event):
            # Position tooltip next to the widget
            x = widget.winfo_rootx() + widget.winfo_width() + 10
            y = widget.winfo_rooty()
            tooltip.wm_geometry(f"+{x}+{y}")
            tooltip.deiconify()

        def hide_tooltip(event):
            tooltip.withdraw()

        widget.bind("<Enter>", show_tooltip)
        widget.bind("<Leave>", hide_tooltip)
        tooltip.withdraw()

    def save_settings(self):
        settings = {
            "Server Name": self.server_name_entry.get(),
            "Max Players": self.max_players_entry.get(),
            "Game Mode": self.game_mode_entry.get(),
            "Difficulty": self.difficulty_entry.get(),
            "PvP Enabled": getattr(self.pvp_enabled_entry, 'var', tk.BooleanVar()).get(),
            "Server Port": self.server_port_entry.get(),
            "Max Day Length": self.max_day_length_entry.get(),
            "Zombie Count": self.zombie_count_entry.get(),
            "Starting Inventory": self.starting_inventory_entry.get(),
            "Server Password": self.server_password_entry.get(),
            "Allow Cheats": getattr(self.allow_cheats_entry, 'var', tk.BooleanVar()).get(),
            "Weather Settings": self.weather_settings_entry.get(),
            "Public Server": getattr(self.public_server_entry, 'var', tk.BooleanVar()).get(),
            "Public Name": self.public_name_entry.get(),
            "Public Description": self.public_description_entry.get(),
            "Player Respawn With Self": getattr(self.player_respawn_with_self_entry, 'var', tk.BooleanVar()).get(),
            "Player Respawn With Other": getattr(self.player_respawn_with_other_entry, 'var', tk.BooleanVar()).get(),
            "Safehouse Allow Loot": getattr(self.safehouse_allow_loot_entry, 'var', tk.BooleanVar()).get(),
            "Safehouse Allow Respawn": getattr(self.safehouse_allow_respawn_entry, 'var', tk.BooleanVar()).get(),
            "Faction": getattr(self.faction_entry, 'var', tk.BooleanVar()).get(),
            "Faction Day Survived To Create": self.faction_day_survived_to_create_entry.get(),
            "Faction Players Required For Tag": self.faction_players_required_for_tag_entry.get(),
            "Zombie Respawn Rate": self.zombie_respawn_rate_entry.get(),
            "Zombie Spawn Count": self.zombie_spawn_count_entry.get(),
            "Loot Respawn Time": self.loot_respawn_time_entry.get(),
            "Day/Night Cycle Length": self.cycle_length_entry.get(),
            "Vehicle Spawn Rate": self.vehicle_spawn_rate_entry.get(),
            "Global Events Frequency": self.events_frequency_entry.get(),
            "Ping Limit": self.ping_limit_entry.get(),
            "Backups Period": self.backups_period_entry.get(),
            "Anti-Cheat Protection Type": self.anti_cheat_protection_type_entry.get(),
        }

        # Add logic to save settings to a file or apply changes
        messagebox.showinfo("Settings Saved", "Game settings have been saved successfully!")
        print("Settings saved:")
        for key, value in settings.items():
            print(f"{key}: {value}")

# To use this class in your main application:
# import game_settings
# settings_frame = game_settings.GameSettings(parent_frame)
# settings_frame.pack(fill=tk.BOTH, expand=True)