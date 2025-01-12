import os
import zipfile
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter.simpledialog import askstring
import requests
from mod_manager_mod_editor import open_edit_dialog
from modmanager_import_options import ImportSettings
from modmanager_search import ModManagerSearch

class Mods(tk.Frame):
    def __init__(self, parent, steam_api_key, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.configure(bg="#1E1E1E")
        self.steam_api_key = steam_api_key
        self.mod_directory = self.get_mod_directory()
        self.current_directory = self.mod_directory
        self.history = [self.mod_directory]  # Initialize history with the base mod directory

        # Initialize ImportSettings and ModManagerSearch
        self.import_settings = ImportSettings(self.mod_directory)
        self.mod_search = ModManagerSearch(self.mod_directory)

        # Set up favorites
        self.favorites = set()

        self.create_widgets()
        self.update_mod_list()

    def create_widgets(self):
        self.create_path_frame()
        self.create_button_frame()
        self.create_sorting_frame()
        self.create_search_frame()
        self.create_mod_listbox()
        self.create_context_menu()
        self.create_import_menu()

    def create_path_frame(self):
        path_frame = tk.Frame(self, bg="#1E1E1E")
        path_frame.pack(fill=tk.X, padx=10, pady=5)

        self.path_label = tk.Label(path_frame, text=self.mod_directory, bg="#1E1E1E", fg="#00FF00", font=("Consolas", 12))
        self.path_label.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # Back button
        self.back_button = tk.Button(path_frame, text="Back", command=self.go_back, bg="#2E2E2E", fg="#00FF00", font=("Consolas", 12), relief="flat", cursor="hand2")
        self.back_button.pack(side=tk.LEFT, padx=5)

    def create_button_frame(self):
        button_frame = tk.Frame(self, bg="#1E1E1E")
        button_frame.pack(pady=10)

        # Buttons for various actions
        buttons = [
            ("Select Mod Directory", self.select_mod_directory),
            ("Install Mod", self.install_mod),
            ("Refresh List", self.update_mod_list),
            ("Change API", self.change_api_key),
            ("Webhook", self.send_webhook),
            ("Import", self.show_import_menu),
            ("Export", self.export_mods)  # Added export button
        ]

        for idx, (text, command) in enumerate(buttons):
            tk.Button(button_frame, text=text, command=command, bg="#2E2E2E", fg="#00FF00", font=("Consolas", 12), relief="flat", cursor="hand2").grid(row=0, column=idx, padx=5)

    def create_sorting_frame(self):
        sorting_frame = tk.Frame(self, bg="#1E1E1E")
        sorting_frame.pack(fill=tk.X, padx=10, pady=5)

        self.sort_var = tk.StringVar(value="Name")
        sort_options = [("Name", "Name"), ("Date", "Date")]

        for text, value in sort_options:
            tk.Radiobutton(sorting_frame, text=f"Sort by {text}", variable=self.sort_var, value=value, command=self.update_mod_list, bg="#2E2E2E", fg="#00FF00", font=("Consolas", 12), relief="flat", cursor="hand2").pack(side=tk.LEFT, padx=5)

    def create_search_frame(self):
        search_frame = tk.Frame(self, bg="#1E1E1E")
        search_frame.pack(fill=tk.X, padx=10, pady=5)

        self.search_entry = tk.Entry(search_frame, bg="#2E2E2E", fg="#00FF00", font=("Consolas", 12))
        self.search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.search_entry.bind('<KeyRelease>', self.search_mods)

        tk.Button(search_frame, text="Search", command=self.search_mods, bg="#2E2E2E", fg="#00FF00", font=("Consolas", 12), relief="flat", cursor="hand2").pack(side=tk.RIGHT, padx=5)

    def create_mod_listbox(self):
        self.mod_listbox = tk.Listbox(self, width=100, height=25, bg="#1E1E1E", fg="#00FF00", font=("Consolas", 12), selectbackground="#004000", selectforeground="#FFFFFF")
        self.mod_listbox.pack(padx=10, pady=5, fill=tk.BOTH, expand=True)
        self.mod_listbox.bind('<Double-1>', self.on_mod_double_click)
        self.mod_listbox.bind('<Button-3>', self.show_context_menu)

    def create_context_menu(self):
        self.context_menu = tk.Menu(self, tearoff=0, bg="#2E2E2E", fg="#00FF00", font=("Consolas", 12))
        self.context_menu.add_command(label="Edit Mod", command=self.edit_mod)
        self.context_menu.add_command(label="Move Mod", command=self.move_mod)
        self.context_menu.add_command(label="Rename Mod", command=self.rename_mod)
        self.context_menu.add_command(label="Change Color", command=self.show_color_menu)
        self.context_menu.add_command(label="Toggle Favorite", command=self.toggle_favorite)  # Added toggle favorite

    def create_import_menu(self):
        self.import_menu = tk.Menu(self, tearoff=0, bg="#2E2E2E", fg="#00FF00", font=("Consolas", 12))
        self.import_menu.add_command(label="Import from Google Drive", command=self.import_settings.import_from_google_drive)
        self.import_menu.add_command(label="Import from Dropbox", command=self.import_settings.import_from_dropbox)
        self.import_menu.add_command(label="Import from GitHub", command=self.import_settings.import_from_github)

    def show_import_menu(self):
        """Show the import menu."""
        self.import_menu.post(self.winfo_rootx(), self.winfo_rooty() + 30)  # Adjust position as needed

    def go_back(self):
        """Navigate back to the previous directory."""
        if len(self.history) > 1:
            self.history.pop()  # Remove current directory
            self.current_directory = self.history[-1]  # Go back to the previous directory
            self.path_label.config(text=self.current_directory)
            self.update_mod_list()

    def select_mod_directory(self):
        """Allow user to select the mod directory."""
        selected_directory = filedialog.askdirectory(initialdir=self.mod_directory, title="Select Mod Directory")
        if selected_directory:
            self.mod_directory = selected_directory
            self.current_directory = self.mod_directory
            self.history = [self.mod_directory]  # Reset history
            self.path_label.config(text=self.mod_directory)
            self.import_settings.mod_directory = self.mod_directory
            self.mod_search.mod_directory = self.mod_directory
            self.update_mod_list()

    def install_mod(self):
        """Install a mod from a ZIP file."""
        file_path = filedialog.askopenfilename(filetypes=[("Mod Files", "*.zip;*.rar")])
        if file_path:
            if not zipfile.is_zipfile(file_path):
                messagebox.showerror("Error", "Selected file is not a valid ZIP file.")
                return
            try:
                with zipfile.ZipFile(file_path, 'r') as zip_ref:
                    zip_ref.extractall(self.mod_directory)
                self.update_mod_list()
                messagebox.showinfo("Success", "Mod installed successfully.")
            except Exception as e:
                messagebox.showerror("Error", f"An error occurred: {e}")

    def update_mod_list(self):
        """Update the list of installed mods or files in the current directory."""
        self.mod_listbox.delete(0, tk.END)
        if os.path.exists(self.current_directory):
            entries = os.listdir(self.current_directory)
            mod_entries = []
            for entry in entries:
                entry_path = os.path.join(self.current_directory, entry)
                if os.path.isdir(entry_path):
                    mod_entries.append((entry, 'DIR', os.path.getmtime(entry_path)))
                elif entry.lower().endswith(".zip"):
                    mod_entries.append((entry, 'ZIP', os.path.getmtime(entry_path)))
                else:
                    mod_entries.append((entry, 'FILE', os.path.getmtime(entry_path)))
            
            # Sort entries based on the selected sort method
            sort_by = self.sort_var.get()
            if sort_by == "Date":
                mod_entries.sort(key=lambda x: x[2], reverse=True)
            else:
                mod_entries.sort(key=lambda x: x[0].lower())

            for entry in mod_entries:
                display_text = f"{entry[0]} [{entry[1]}]"
                # Determine tag based on favorite status
                tag = "favorite" if entry[0] in self.favorites else "default"
                self.mod_listbox.insert(tk.END, display_text)
                self.mod_listbox.itemconfig(tk.END, {'bg': '#FFD700' if tag == 'favorite' else '#1E1E1E', 'fg': '#00FF00'})  # Change background and foreground based on tag

    def on_mod_double_click(self, event):
        """Handle double-click on a mod item."""
        selected_item = self.mod_listbox.get(tk.ACTIVE)
        if selected_item:
            item_name = selected_item.split()[0].strip("[]")  # Extract the name from the display text
            item_path = os.path.join(self.current_directory, item_name)
            if os.path.isdir(item_path):
                self.history.append(self.current_directory)  # Save current directory to history
                self.current_directory = item_path
                self.path_label.config(text=self.current_directory)
                self.update_mod_list()
            elif os.path.isfile(item_path):
                open_edit_dialog(self, item_path)

    def search_mods(self, event=None):
        """Search for mods based on user input."""
        search_text = self.search_entry.get().lower()
        if search_text:
            search_results = self.mod_search.search(search_text)
            self.mod_listbox.delete(0, tk.END)
            for result in search_results:
                self.mod_listbox.insert(tk.END, result)
        else:
            self.update_mod_list()

    def show_context_menu(self, event):
        """Show context menu on right-click."""
        self.context_menu.post(event.x_root, event.y_root)

    def edit_mod(self):
        """Edit the selected mod."""
        selected_mod = self.mod_listbox.get(tk.ACTIVE)
        if selected_mod:
            item_name = selected_mod.split()[0].strip("[]")  # Extract the name from the display text
            item_path = os.path.join(self.current_directory, item_name)

            if os.path.isfile(item_path):
                # Use the function from the external module
                open_edit_dialog(self, item_path)
            else:
                messagebox.showwarning("Not File", "The selected item is not a file and cannot be edited.")

    def move_mod(self):
        """Move the selected mod to a new directory."""
        selected_mod = self.mod_listbox.get(tk.ACTIVE)
        if selected_mod:
            item_name = selected_mod.split()[0].strip("[]")  # Extract the name from the display text
            item_path = os.path.join(self.current_directory, item_name)

            new_directory = filedialog.askdirectory(initialdir=self.current_directory, title="Select Destination Directory")
            if new_directory:
                try:
                    os.rename(item_path, os.path.join(new_directory, item_name))
                    self.update_mod_list()
                    messagebox.showinfo("Success", "Mod moved successfully.")
                except Exception as e:
                    messagebox.showerror("Error", f"An error occurred: {e}")

    def rename_mod(self):
        """Rename the selected mod."""
        selected_mod = self.mod_listbox.get(tk.ACTIVE)
        if selected_mod:
            item_name = selected_mod.split()[0].strip("[]")  # Extract the name from the display text
            item_path = os.path.join(self.current_directory, item_name)

            new_name = askstring("Rename Mod", "Enter new name:")
            if new_name:
                new_path = os.path.join(self.current_directory, new_name)
                try:
                    os.rename(item_path, new_path)
                    self.update_mod_list()
                    messagebox.showinfo("Success", "Mod renamed successfully.")
                except Exception as e:
                    messagebox.showerror("Error", f"An error occurred: {e}")

    def show_color_menu(self):
        """Show the color menu."""
        selected_mod = self.mod_listbox.get(tk.ACTIVE)
        if selected_mod:
            messagebox.showinfo("Change Color", f"Changing color for {selected_mod}")

    def get_mod_directory(self):
        """Get the default mod directory. Modify this method as needed."""
        return os.path.expanduser("~/Documents/Mods")

    def change_api_key(self):
        """Change the Steam API key."""
        new_key = askstring("Change API Key", "Enter new Steam API Key:")
        if new_key:
            self.steam_api_key = new_key
            messagebox.showinfo("Success", "Steam API Key updated successfully.")

    def send_webhook(self):
        """Send mod list to a Discord webhook."""
        webhook_url = askstring("Webhook URL", "Enter Discord Webhook URL:")
        if webhook_url:
            channel_id = askstring("Channel ID", "Enter Discord Channel ID:")
            if channel_id:
                mod_names = [self.mod_listbox.get(idx).split()[0].strip("[]") for idx in range(self.mod_listbox.size())]
                embed_description = "\n".join(mod_names)
                embed_content = {
                    "content": "List of Mods:",
                    "embeds": [
                        {
                            "title": "Mod List",
                            "description": embed_description,
                            "color": 5814783
                        }
                    ]
                }
                try:
                    response = requests.post(webhook_url, json=embed_content)
                    if response.status_code == 204:
                        messagebox.showinfo("Success", "Mod list sent to Discord channel.")
                    else:
                        messagebox.showerror("Error", f"Failed to send message: {response.status_code}")
                except Exception as e:
                    messagebox.showerror("Error", f"An error occurred: {e}")

    def toggle_favorite(self):
        """Toggle the favorite status of the selected mod."""
        selected_mod = self.mod_listbox.get(tk.ACTIVE)
        if selected_mod:
            item_name = selected_mod.split()[0].strip("[]")
            if item_name in self.favorites:
                self.favorites.remove(item_name)
            else:
                self.favorites.add(item_name)
            self.update_mod_list()

    def export_mods(self):
        """Export all mods as a ZIP file and upload to Google Drive or GitHub."""
        output_zip = filedialog.asksaveasfilename(defaultextension=".zip", filetypes=[("ZIP files", "*.zip")])
        if output_zip:
            try:
                with zipfile.ZipFile(output_zip, 'w') as zip_ref:
                    for root, _, files in os.walk(self.mod_directory):
                        for file in files:
                            file_path = os.path.join(root, file)
                            zip_ref.write(file_path, os.path.relpath(file_path, self.mod_directory))
                messagebox.showinfo("Success", "Mods exported successfully.")
                # Optionally, implement upload logic here
                # self.upload_to_google_drive(output_zip)
                # self.upload_to_github(output_zip)
            except Exception as e:
                messagebox.showerror("Error", f"An error occurred: {e}")

    def upload_to_google_drive(self, file_path):
        """Upload file to Google Drive (implement this function)."""
        pass  # Replace with actual Google Drive upload code

    def upload_to_github(self, file_path):
        """Upload file to GitHub (implement this function)."""
        pass  # Replace with actual GitHub upload code

# Example usage:
if __name__ == "__main__":
    root = tk.Tk()
    app = Mods(root, steam_api_key="YOUR_STEAM_API_KEY")
    app.pack(fill=tk.BOTH, expand=True)
    root.mainloop()