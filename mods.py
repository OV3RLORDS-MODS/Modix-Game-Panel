import os
import zipfile
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from tkinter.simpledialog import askstring
import subprocess
import requests
import shutil
import json
import threading
from PIL import Image, ImageTk
import webbrowser
import sys

class Mods(tk.Frame):
    def __init__(self, parent, steam_api_key, current_user, *args, **kwargs):
        # Check if this script is being run directly
        if __name__ == "__main__":
            messagebox.showerror("Error", "You cannot run mods.py directly. Please run app.py.")
            sys.exit()  # Exit if the script is executed directly without going through app.py

        # Ensure the user is logged in
        if not current_user:
            messagebox.showerror("Access Denied", "You must be logged in to access Mods.")
            return

        super().__init__(parent, *args, **kwargs)
        self.configure(bg="#1E1E2E")

        self.current_user = current_user
        self.steam_api_key = steam_api_key
        self.mod_directory = None
        self.installed_mods = []
        self.categories = set()
        self.selected_category = "All"
        self.show_favorites_only = False
        self.search_query = ""
        self.last_mods_set = set()  # Track directory content changes
        self.create_widgets()
        self.check_steamcmd_installation()

    def create_widgets(self):
        style = ttk.Style(self)
        style.theme_use('default')
        style.configure("Custom.Horizontal.TProgressbar", thickness=20, background="#6272A4")

        header_frame = tk.Frame(self, bg="#282A36", pady=15)
        header_frame.pack(fill=tk.X)
        tk.Label(header_frame, text="Project Zomboid Mods Manager", 
                 font=("Segoe UI", 20, "bold"), fg="#FFFFFF", bg="#282A36").pack()

        action_frame = tk.Frame(self, bg="#1E1E2E")
        action_frame.pack(fill=tk.X, padx=10, pady=5)

        tk.Button(action_frame, text="Select Mod Dir", command=self.select_mod_directory, 
                  bg="#44475A", fg="#FFFFFF", font=("Segoe UI", 10), relief="flat").pack(side=tk.LEFT, padx=5)
        tk.Button(action_frame, text="Setup SteamCMD", command=self.setup_steamcmd, 
                  bg="#44475A", fg="#FFFFFF", font=("Segoe UI", 10), relief="flat").pack(side=tk.LEFT, padx=5)
        tk.Button(action_frame, text="Install Mod", command=self.install_mod, 
                  bg="#44475A", fg="#FFFFFF", font=("Segoe UI", 10), relief="flat").pack(side=tk.LEFT, padx=5)
        tk.Button(action_frame, text="Export Mods", command=self.export_mods, 
                  bg="#44475A", fg="#FFFFFF", font=("Segoe UI", 10), relief="flat").pack(side=tk.LEFT, padx=5)

        download_frame = tk.Frame(action_frame, bg="#1E1E2E")
        download_frame.pack(side=tk.LEFT, padx=5)
        self.mod_id_var = tk.StringVar()
        tk.Entry(download_frame, textvariable=self.mod_id_var, width=20, 
                 bg="#44475A", fg="#FFFFFF", font=("Segoe UI", 10)).pack(side=tk.LEFT, padx=5)
        tk.Button(download_frame, text="Download by ID", command=self.start_download_mod_by_id, 
                  bg="#6272A4", fg="#FFFFFF", font=("Segoe UI", 10), relief="flat").pack(side=tk.LEFT)

        filter_frame = tk.Frame(self, bg="#1E1E2E")
        filter_frame.pack(fill=tk.X, padx=10, pady=5)

        tk.Label(filter_frame, text="Filter by Category:", bg="#1E1E2E", fg="#FFFFFF").pack(side=tk.LEFT, padx=(0,5))
        self.category_var = tk.StringVar(value="All")
        self.category_menu = ttk.Combobox(filter_frame, textvariable=self.category_var, state="readonly")
        self.category_menu['values'] = ("All",)
        self.category_menu.pack(side=tk.LEFT, padx=5)
        self.category_menu.bind("<<ComboboxSelected>>", lambda e: self.apply_filters())

        self.favorite_filter_var = tk.BooleanVar(value=False)
        tk.Checkbutton(filter_frame, text="Show Favorites Only", variable=self.favorite_filter_var, 
                       command=self.apply_filters, bg="#1E1E2E", fg="#FFFFFF", selectcolor="#1E1E2E").pack(side=tk.LEFT, padx=20)

        tk.Label(filter_frame, text="Search:", bg="#1E1E2E", fg="#FFFFFF").pack(side=tk.LEFT, padx=(20,5))
        self.search_var = tk.StringVar()
        search_entry = tk.Entry(filter_frame, textvariable=self.search_var, width=30, 
                                bg="#44475A", fg="#FFFFFF", font=("Segoe UI", 10))
        search_entry.pack(side=tk.LEFT, padx=5)
        search_entry.bind("<KeyRelease>", lambda e: self.on_search())

        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(self, style="Custom.Horizontal.TProgressbar",
                                            variable=self.progress_var, maximum=100)
        self.progress_bar.pack(fill=tk.X, padx=10, pady=5)

        mod_list_container = tk.Frame(self, bg="#1E1E2E")
        mod_list_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        self.canvas = tk.Canvas(mod_list_container, bg="#1E1E2E", highlightthickness=0)
        self.scrollbar = tk.Scrollbar(mod_list_container, orient="vertical", command=self.canvas.yview)
        self.mod_list_frame = tk.Frame(self.canvas, bg="#1E1E2E")

        self.mod_list_frame.bind(
            "<Configure>", 
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        self.canvas.create_window((0, 0), window=self.mod_list_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    def check_steamcmd_installation(self):
        if not shutil.which("steamcmd"):
            messagebox.showinfo("Setup Required", 
                                "SteamCMD is not installed. Please click 'Setup SteamCMD' to install it.")
        else:
            print("SteamCMD is already installed.")

    def select_mod_directory(self):
        selected_dir = filedialog.askdirectory(title="Select Mod Directory")
        if selected_dir:
            self.mod_directory = selected_dir
            self.load_installed_mods()

    def load_installed_mods(self):
        if not self.mod_directory:
            return
        try:
            self.installed_mods = []
            for folder_name in os.listdir(self.mod_directory):
                folder_path = os.path.join(self.mod_directory, folder_name)
                if os.path.isdir(folder_path):
                    image_path = os.path.join(folder_path, "poster.png")
                    self.installed_mods.append({
                        "name": folder_name,
                        "description": "Folder-based mod detected.",
                        "status": "Installed",
                        "image": image_path if os.path.exists(image_path) else None,
                        "category": "Uncategorized",
                        "favorite": False
                    })
            print(f"Loaded {len(self.installed_mods)} mods from directory.")
            self.refresh_category_menu()
            self.update_mod_list()
            # Update directory state and start watching
            self.last_mods_set = set(os.listdir(self.mod_directory))
            self.after(5000, self.watch_mod_directory)
        except Exception as e:
            print(f"Error loading installed mods: {e}")

    def watch_mod_directory(self):
        """Periodically check the selected directory for changes and refresh mods if changes detected."""
        if not self.mod_directory:
            return
        try:
            current_set = set(os.listdir(self.mod_directory))
            if current_set != self.last_mods_set:
                print("Change detected in mod directory. Reloading mods...")
                self.load_installed_mods()
            self.last_mods_set = current_set
        except Exception as e:
            print(f"Error watching mod directory: {e}")
        self.after(5000, self.watch_mod_directory)

    def update_mod_list(self):
        for widget in self.mod_list_frame.winfo_children():
            widget.destroy()

        filtered_mods = self.installed_mods

        if self.selected_category and self.selected_category != "All":
            filtered_mods = [m for m in filtered_mods if m.get("category") == self.selected_category]
        if self.show_favorites_only:
            filtered_mods = [m for m in filtered_mods if m.get("favorite")]
        if self.search_query:
            query = self.search_query.lower()
            filtered_mods = [
                m for m in filtered_mods 
                if query in m.get("name", "").lower() or query in m.get("description", "").lower()
            ]

        # Limit the number of mods displayed to 200
        filtered_mods = filtered_mods[:200]

        row_frame = None
        for index, mod in enumerate(filtered_mods):
            if index % 3 == 0:
                row_frame = tk.Frame(self.mod_list_frame, bg="#1E1E2E")
                row_frame.pack(fill=tk.X, padx=5, pady=5)

            mod_frame = tk.Frame(row_frame, bg="#282A36", width=350, height=200, padx=10, pady=10, 
                                 relief="groove", bd=2)
            mod_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)

            image_path = mod.get("image")
            if image_path and os.path.exists(image_path):
                try:
                    img = Image.open(image_path)
                    img.thumbnail((100, 100))
                    img_tk = ImageTk.PhotoImage(img)
                    img_label = tk.Label(mod_frame, image=img_tk, bg="#282A36")
                    img_label.image = img_tk
                    img_label.pack(side=tk.LEFT, padx=10, pady=10)
                except Exception as e:
                    print(f"Error loading image: {e}")

            details_frame = tk.Frame(mod_frame, bg="#282A36")
            details_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10)

            tk.Label(details_frame, text=mod["name"], bg="#282A36", fg="#FFFFFF", 
                     font=("Segoe UI", 14, "bold"), anchor="w").pack(anchor="w")
            description = mod["description"][:150] + ("..." if len(mod["description"]) > 150 else "")
            tk.Label(details_frame, text=description, bg="#282A36", fg="#AAAAAA", 
                     font=("Segoe UI", 10), wraplength=250, justify="left").pack(anchor="w", pady=2)

            status_color = "#28A745" if mod["status"] == "Installed" else "#FFC107"
            tk.Label(details_frame, text=f"Status: {mod['status']}", bg="#282A36", fg=status_color, 
                     font=("Segoe UI", 10, "bold")).pack(anchor="w")

            fav_text = "★" if mod.get("favorite") else "☆"
            tk.Button(details_frame, text=fav_text, command=lambda m=mod: self.toggle_favorite(m), 
                      bg="#6272A4", fg="#FFFFFF", font=("Segoe UI", 10), relief="flat").pack(anchor="w", pady=5)

            tk.Button(details_frame, text="Details", command=lambda m=mod: self.show_mod_details(m), 
                      bg="#6272A4", fg="#FFFFFF", font=("Segoe UI", 10), relief="flat").pack(anchor="e", pady=5)

    def toggle_favorite(self, mod):
        mod["favorite"] = not mod.get("favorite", False)
        self.save_installed_mods()
        self.update_mod_list()

    def apply_filters(self):
        self.selected_category = self.category_var.get()
        self.show_favorites_only = self.favorite_filter_var.get()
        self.search_query = self.search_var.get().strip()
        self.update_mod_list()

    def on_search(self):
        self.search_query = self.search_var.get().strip()
        self.apply_filters()

    def fetch_mod_details(self, mod_id):
        url = "https://api.steampowered.com/ISteamRemoteStorage/GetPublishedFileDetails/v1/"
        params = {
            'key': self.steam_api_key,
            'itemcount': 1,
            'publishedfileids[0]': mod_id
        }
        try:
            response = requests.post(url, data=params)
            response.raise_for_status()
            data = response.json()
            if data and data.get("response", {}).get("publishedfiledetails"):
                return data["response"]["publishedfiledetails"][0]
        except Exception as e:
            print(f"Error fetching mod details: {e}")
        return None

    def show_mod_details(self, mod):
        mod_id = None
        if mod["name"].startswith("Mod ID:"):
            mod_id = mod["name"].split("Mod ID:")[-1].strip()
        
        details_data = None
        if mod_id:
            details_data = self.fetch_mod_details(mod_id)

        detail_win = tk.Toplevel(self)
        detail_win.title(f"Details for {mod['name']}")
        detail_win.configure(bg="#1E1E2E")
        detail_win.geometry("600x500")

        canvas = tk.Canvas(detail_win, bg="#1E1E2E", highlightthickness=0)
        scrollbar = tk.Scrollbar(detail_win, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg="#1E1E2E")
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        tk.Label(scrollable_frame, text=f"Name: {mod['name']}", bg="#282A36", fg="#FFFFFF",
                 font=("Segoe UI", 14, "bold")).pack(fill="x", pady=5, padx=5)

        tk.Label(scrollable_frame, text=f"Description: {mod['description']}", bg="#1E1E2E", fg="#AAAAAA",
                 wraplength=550, justify="left").pack(fill="x", pady=5, padx=5)
        tk.Label(scrollable_frame, text=f"Status: {mod['status']}", bg="#1E1E2E", fg="#FFFFFF").pack(fill="x", pady=5, padx=5)
        tk.Label(scrollable_frame, text=f"Category: {mod.get('category', 'Uncategorized')}", bg="#1E1E2E", fg="#FFFFFF").pack(fill="x", pady=5, padx=5)
        tk.Label(scrollable_frame, text=f"Favorite: {'Yes' if mod.get('favorite') else 'No'}", bg="#1E1E2E", fg="#FFFFFF").pack(fill="x", pady=5, padx=5)

        if details_data:
            title = details_data.get("title", "N/A")
            file_description = details_data.get("description", "No description available.")
            author = details_data.get("creator", "Unknown Author")
            workshop_link = f"https://steamcommunity.com/sharedfiles/filedetails/?id={mod_id}"
            votes_up = details_data.get("votes_up", 0)
            votes_down = details_data.get("votes_down", 0)
            score = details_data.get("score", "N/A")
            requirements = details_data.get("file_url", "N/A")

            tk.Label(scrollable_frame, text=f"Workshop Title: {title}", bg="#282A36", fg="#FFFFFF",
                     font=("Segoe UI", 12, "bold")).pack(fill="x", pady=5, padx=5)
            tk.Label(scrollable_frame, text=f"Workshop Description: {file_description}", bg="#1E1E2E", fg="#AAAAAA",
                     wraplength=550, justify="left").pack(fill="x", pady=5, padx=5)
            tk.Label(scrollable_frame, text=f"Author ID: {author}", bg="#1E1E2E", fg="#FFFFFF").pack(fill="x", pady=5, padx=5)

            tk.Button(scrollable_frame, text="View on Workshop", command=lambda: webbrowser.open(workshop_link),
                      bg="#6272A4", fg="#FFFFFF", font=("Segoe UI", 10), relief="flat").pack(pady=5, padx=5)

            tk.Label(scrollable_frame, text=f"Upvotes: {votes_up}, Downvotes: {votes_down}, Score: {score}", 
                     bg="#1E1E2E", fg="#FFFFFF").pack(fill="x", pady=5, padx=5)
            tk.Label(scrollable_frame, text=f"Requirements: {requirements}", bg="#1E1E2E", fg="#FFFFFF", 
                     wraplength=550, justify="left").pack(fill="x", pady=5, padx=5)
        else:
            tk.Label(scrollable_frame, text="Detailed workshop information not available for this mod.",
                     bg="#1E1E2E", fg="#FF5555").pack(fill="x", pady=5, padx=5)

    def install_mod(self):
        mod_file = filedialog.askopenfilename(filetypes=[("Mod Files", "*.zip")], title="Select Mod to Install")
        if mod_file and zipfile.is_zipfile(mod_file):
            category = askstring("Category", "Enter a category for this mod:", parent=self)
            if not category:
                category = "Uncategorized"

            try:
                with zipfile.ZipFile(mod_file, "r") as zip_ref:
                    zip_ref.extractall(self.mod_directory)
                new_mod = {
                    "name": os.path.basename(mod_file),
                    "description": "Manually installed mod.",
                    "status": "Installed",
                    "image": None,
                    "category": category,
                    "favorite": False
                }
                self.installed_mods.append(new_mod)
                self.categories.add(category)
                self.refresh_category_menu()
                self.save_installed_mods()
                self.update_mod_list()
                messagebox.showinfo("Success", "Mod installed successfully.")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to install mod: {e}")

    def export_mods(self):
        output_zip = filedialog.asksaveasfilename(defaultextension=".zip", filetypes=[("ZIP files", "*.zip")])
        if output_zip:
            try:
                with zipfile.ZipFile(output_zip, "w") as zip_ref:
                    for root, _, files in os.walk(self.mod_directory):
                        for file in files:
                            file_path = os.path.join(root, file)
                            zip_ref.write(file_path, os.path.relpath(file_path, self.mod_directory))
                messagebox.showinfo("Success", "Mods exported successfully.")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to export mods: {e}")

    def start_download_mod_by_id(self):
        mod_id = self.mod_id_var.get().strip()
        if not mod_id:
            messagebox.showerror("Error", "Please enter a valid Mod ID.")
            return
        threading.Thread(target=self.download_mod_by_id, args=(mod_id,), daemon=True).start()

    def download_mod_by_id(self, mod_id):
        try:
            cmd = ["steamcmd", "+login", "anonymous", "+workshop_download_item", "108600", mod_id, "+quit"]
            process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

            while True:
                output = process.stdout.readline()
                if output == "" and process.poll() is not None:
                    break
                if output:
                    if "Downloading" in output:
                        self.progress_var.set(min(self.progress_var.get() + 5, 100))
                        self.update_idletasks()
            process.wait()

            if process.returncode == 0:
                workshop_dir = os.path.expanduser("~/steamcmd/steamapps/workshop/content/108600")
                mod_path = os.path.join(workshop_dir, mod_id)
                if os.path.exists(mod_path):
                    # Copy downloaded mod folder to user's selected directory
                    if self.mod_directory:
                        destination = os.path.join(self.mod_directory, mod_id)
                        try:
                            if not os.path.exists(destination):
                                shutil.copytree(mod_path, destination)
                                print(f"Copied mod {mod_id} to {destination}")
                            else:
                                print(f"Destination {destination} already exists.")
                        except Exception as copy_error:
                            print(f"Error copying mod folder: {copy_error}")

                    image_path = os.path.join(mod_path, "poster.png")
                    new_mod = {
                        "name": f"Mod ID: {mod_id}",
                        "description": "Downloaded from Steam Workshop.",
                        "status": "Installed",
                        "image": image_path if os.path.exists(image_path) else None,
                        "category": "Uncategorized",
                        "favorite": False
                    }
                    self.installed_mods.append(new_mod)
                    self.refresh_category_menu()
                    self.save_installed_mods()
                    self.update_mod_list()
                    messagebox.showinfo("Success", f"Mod {mod_id} downloaded successfully.")
                else:
                    messagebox.showerror("Error", f"Mod {mod_id} not found in workshop directory.")
            else:
                messagebox.showerror("Error", "Failed to download mod. Command returned non-zero exit status.")
        except FileNotFoundError:
            messagebox.showerror("Error", "SteamCMD not found. Please install SteamCMD to download mods.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to download mod: {e}")
        finally:
            self.progress_var.set(0)

    def setup_steamcmd(self):
        steamcmd_url = "https://steamcdn-a.akamaihd.net/client/installer/steamcmd.zip"
        steamcmd_dir = os.path.expanduser("~/steamcmd")
        steamcmd_zip = os.path.join(steamcmd_dir, "steamcmd.zip")

        try:
            os.makedirs(steamcmd_dir, exist_ok=True)
            response = requests.get(steamcmd_url, stream=True)
            response.raise_for_status()

            with open(steamcmd_zip, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)

            with zipfile.ZipFile(steamcmd_zip, "r") as zip_ref:
                zip_ref.extractall(steamcmd_dir)

            os.environ["PATH"] += os.pathsep + steamcmd_dir
            messagebox.showinfo("Success", "SteamCMD setup completed.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to set up SteamCMD: {e}")

    def refresh_category_menu(self):
        all_categories = {"All"} | {mod.get("category", "Uncategorized") for mod in self.installed_mods}
        self.category_menu['values'] = tuple(sorted(all_categories))
        if self.selected_category in all_categories:
            self.category_var.set(self.selected_category)
        else:
            self.category_var.set("All")

    def save_installed_mods(self):
        try:
            if not self.mod_directory:
                return
            with open(os.path.join(self.mod_directory, "installed_mods.json"), "w") as f:
                json.dump(self.installed_mods, f)
        except Exception as e:
            print(f"Error saving installed mods: {e}")

    def load_installed_mods(self):
        if not self.mod_directory:
            return
        try:
            mods_file = os.path.join(self.mod_directory, "installed_mods.json")
            if os.path.exists(mods_file):
                with open(mods_file, "r") as f:
                    self.installed_mods = json.load(f)
            else:
                self.installed_mods = []
                for folder_name in os.listdir(self.mod_directory):
                    folder_path = os.path.join(self.mod_directory, folder_name)
                    if os.path.isdir(folder_path):
                        image_path = os.path.join(folder_path, "poster.png")
                        self.installed_mods.append({
                            "name": folder_name,
                            "description": "Folder-based mod detected.",
                            "status": "Installed",
                            "image": image_path if os.path.exists(image_path) else None,
                            "category": "Uncategorized",
                            "favorite": False
                        })
            self.refresh_category_menu()
            self.update_mod_list()
        except Exception as e:
            print(f"Error loading installed mods: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    root.title("Project Zomboid Mods Manager")
    root.geometry("1200x800")
    # For testing, using a dummy user. In production, Mods should be instantiated with actual logged-in user info.
    app = Mods(root, steam_api_key="YOUR_STEAM_API_KEY", current_user="dummy_user")
    app.pack(fill=tk.BOTH, expand=True)
    root.mainloop()
