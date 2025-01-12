import tkinter as tk
from tkinter import simpledialog, messagebox, filedialog, Menu
import requests
from PIL import Image, ImageTk
from io import BytesIO
import webbrowser
import sqlite3
import aiohttp
import asyncio
import os

class ModManager(tk.Frame):
    def __init__(self, parent, steam_api_key, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.steam_api_key = steam_api_key
        self.mod_id_map = {}
        self.mod_tags = {}
        self.mod_status = {}
        self.mod_steam_urls = {}
        self.database = "mods.db"
        self.mod_dir = ""
        self.create_widgets()
        self.load_from_database()

    def create_widgets(self):
        self.configure(bg="#2e2e2e")

        # Header
        header_frame = tk.Frame(self, bg="#ff5722", pady=15)
        header_frame.pack(fill=tk.X)
        tk.Label(header_frame, text="Mod Manager", font=("Arial", 24, "bold"), fg="#ffffff", bg="#ff5722").pack()

        # Content frame
        content_frame = tk.Frame(self, bg="#2e2e2e")
        content_frame.pack(fill=tk.BOTH, expand=True)

        # Search frame
        search_frame = tk.Frame(content_frame, bg="#2e2e2e", pady=10)
        search_frame.pack(fill=tk.X, padx=15)
        tk.Label(search_frame, text="Search Mods:", font=("Arial", 14), bg="#2e2e2e", fg="#ffffff").pack(side=tk.LEFT, padx=5)
        self.mod_search_var = tk.StringVar()
        self.mod_search_entry = tk.Entry(search_frame, textvariable=self.mod_search_var, font=("Arial", 12), bg="#424242", fg="#ffffff", bd=1, relief=tk.SOLID)
        self.mod_search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        self.mod_search_entry.bind("<KeyRelease>", self.filter_mod_list)

        # Filter frame
        filter_frame = tk.Frame(content_frame, bg="#2e2e2e", pady=10)
        filter_frame.pack(fill=tk.X, padx=15)
        tk.Label(filter_frame, text="Filter by Category:", font=("Arial", 14), bg="#2e2e2e", fg="#ffffff").pack(side=tk.LEFT, padx=5)
        self.category_var = tk.StringVar(value="All")
        categories = ["All", "Active", "Bugged", "Pending", "Build40", "Build41", "Balance", "Building", "Clothing", "Food", "Interface", "Literature", "Misc", "Models", "Textures", "Transport", "Weapons", "Other"]
        for category in categories:
            tk.Radiobutton(filter_frame, text=category, variable=self.category_var, value=category, font=("Arial", 10), bg="#2e2e2e", fg="#ffffff", selectcolor="#424242", indicatoron=0, relief=tk.FLAT, width=10, height=1, command=self.filter_mod_list).pack(side=tk.LEFT, padx=5)

        # Sort frame
        sort_frame = tk.Frame(content_frame, bg="#2e2e2e", pady=10)
        sort_frame.pack(fill=tk.X, padx=15)
        tk.Label(sort_frame, text="Sort by:", font=("Arial", 14), bg="#2e2e2e", fg="#ffffff").pack(side=tk.LEFT, padx=5)
        self.sort_var = tk.StringVar(value="Title")
        sort_options = ["Title", "Status"]
        for option in sort_options:
            tk.Radiobutton(sort_frame, text=option, variable=self.sort_var, value=option, font=("Arial", 10), bg="#2e2e2e", fg="#ffffff", selectcolor="#424242", indicatoron=0, relief=tk.FLAT, width=8, height=1, command=self.filter_mod_list).pack(side=tk.LEFT, padx=5)

        # List frame
        list_frame = tk.Frame(content_frame, bg="#2e2e2e")
        list_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=15, pady=10)

        self.mod_listbox = tk.Listbox(list_frame, bg="#424242", fg="#ffffff", font=("Arial", 12), selectbackground="#ff5722", selectforeground="#ffffff")
        self.mod_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scrollbar = tk.Scrollbar(list_frame, command=self.mod_listbox.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.mod_listbox.config(yscrollcommand=scrollbar.set)

        self.mod_listbox.bind("<<ListboxSelect>>", self.on_mod_select)
        self.mod_listbox.bind("<Button-3>", self.show_context_menu)

        # Details frame
        details_frame = tk.Frame(content_frame, bg="#2e2e2e", padx=15, pady=15)
        details_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        tk.Label(details_frame, text="Mod Details", font=("Arial", 16, "bold"), bg="#2e2e2e", fg="#ffffff").pack(pady=5)

        self.mod_image_label = tk.Label(details_frame, bg="#2e2e2e")
        self.mod_image_label.pack(pady=5)

        self.mod_details_text = tk.Text(details_frame, wrap=tk.WORD, state=tk.DISABLED, bg="#424242", fg="#ffffff", font=("Arial", 12))
        self.mod_details_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.steam_page_button = tk.Button(details_frame, text="View on Steam", command=self.open_steam_page, state=tk.DISABLED, bg="#007bff", fg="#ffffff", font=("Arial", 12), relief=tk.FLAT)
        self.steam_page_button.pack(pady=5)

        # Import button and Select Mod Dir button
        button_frame = tk.Frame(details_frame, bg="#2e2e2e")
        button_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=10)

        self.select_mod_dir_button = tk.Button(button_frame, text="Select Mod Dir", command=self.select_mod_dir, bg="#ffc107", fg="#ffffff", font=("Arial", 12))
        self.select_mod_dir_button.pack(side=tk.LEFT, padx=5)

        self.import_button = tk.Button(button_frame, text="Import Mod", command=self.import_mod, bg="#28a745", fg="#ffffff", font=("Arial", 12))
        self.import_button.pack(side=tk.LEFT, padx=5)

    def filter_mod_list(self, event=None):
        search_term = self.mod_search_var.get().lower()
        selected_category = self.category_var.get()
        sort_by = self.sort_var.get()

        sorted_mods = sorted(
            self.mod_id_map.items(),
            key=lambda item: (self.mod_status.get(item[0], "Off") != "Pending", 
                              self.mod_status.get(item[0], "Off") if sort_by == "Status" else item[0].lower())
        )

        self.mod_listbox.delete(0, tk.END)
        for mod_title, mod_id in sorted_mods:
            if search_term in mod_title.lower():
                tags = self.mod_tags.get(mod_title, [])
                if selected_category == "All" or selected_category in tags:
                    status_prefix = self.mod_status.get(mod_title, "Off")
                    self.mod_listbox.insert(tk.END, f"[{status_prefix}] {mod_title}")

    async def fetch_mod_details(self, mod_id):
        url = "https://api.steampowered.com/ISteamRemoteStorage/GetPublishedFileDetails/v1/"
        params = {
            "key": self.steam_api_key,
            "itemcount": 1,
            "publishedfileids[0]": mod_id
        }
        async with aiohttp.ClientSession() as session:
            async with session.post(url, data=params) as response:
                return await response.json()

    def on_mod_select(self, event):
        selected_index = self.mod_listbox.curselection()
        if not selected_index:
            return
        
        selected_mod = self.mod_listbox.get(selected_index)
        mod_title = selected_mod[selected_mod.find("] ") + 2:]
        mod_id = self.mod_id_map.get(mod_title)

        if not mod_id:
            self.mod_details_text.config(state=tk.NORMAL)
            self.mod_details_text.delete(1.0, tk.END)
            self.mod_details_text.insert(tk.END, "Mod details not found.")
            self.mod_details_text.config(state=tk.DISABLED)
            return

        asyncio.run(self.load_mod_details(mod_id))

    async def load_mod_details(self, mod_id):
        details = await self.fetch_mod_details(mod_id)
        if "response" not in details or not details["response"]["publishedfiledetails"]:
            messagebox.showerror("Error", "Mod not found.")
            return
        
        mod_info = details["response"]["publishedfiledetails"][0]

        image_url = mod_info.get("preview_url")
        if image_url:
            image_data = requests.get(image_url).content
            image = Image.open(BytesIO(image_data))
            image.thumbnail((200, 200))
            photo = ImageTk.PhotoImage(image)
            self.mod_image_label.config(image=photo)
            self.mod_image_label.image = photo
        else:
            self.mod_image_label.config(image="")

        self.mod_details_text.config(state=tk.NORMAL)
        self.mod_details_text.delete(1.0, tk.END)
        self.mod_details_text.insert(tk.END, f"Title: {mod_info.get('title', 'N/A')}\n")
        self.mod_details_text.insert(tk.END, f"Description: {mod_info.get('description', 'N/A')}\n")
        self.mod_details_text.insert(tk.END, f"Author: {mod_info.get('creator', 'N/A')}\n")
        self.mod_details_text.insert(tk.END, f"Date Published: {mod_info.get('time_created', 'N/A')}\n")
        self.mod_details_text.config(state=tk.DISABLED)

        self.steam_page_button.config(state=tk.NORMAL)
        self.steam_page_button.bind("<Button-1>", lambda e: webbrowser.open(mod_info.get("url", "")))

    def show_context_menu(self, event):
        selected_index = self.mod_listbox.curselection()
        if not selected_index:
            return
        
        context_menu = Menu(self, tearoff=0, bg="#2e2e2e", fg="#ffffff")
        context_menu.add_command(label="Assign Tag", command=self.assign_tag, background="#2e2e2e", foreground="#ffffff", font=("Arial", 12))
        context_menu.add_command(label="Change Status", command=self.change_status, background="#2e2e2e", foreground="#ffffff", font=("Arial", 12))
        context_menu.post(event.x_root, event.y_root)

    def assign_tag(self):
        tag = simpledialog.askstring("Assign Tag", "Enter the tag to assign:")
        if tag:
            selected_index = self.mod_listbox.curselection()
            if not selected_index:
                return
            selected_mod = self.mod_listbox.get(selected_index)
            mod_title = selected_mod[selected_mod.find("] ") + 2:]
            if mod_title in self.mod_tags:
                self.mod_tags[mod_title].append(tag)
                self.filter_mod_list()

    def change_status(self):
        status = simpledialog.askstring("Change Status", "Enter the new status (Active, Bugged, Pending, etc.):")
        if status:
            selected_index = self.mod_listbox.curselection()
            if not selected_index:
                return
            selected_mod = self.mod_listbox.get(selected_index)
            mod_title = selected_mod[selected_mod.find("] ") + 2:]
            self.mod_status[mod_title] = status
            self.filter_mod_list()

    def open_steam_page(self):
        selected_index = self.mod_listbox.curselection()
        if not selected_index:
            return
        selected_mod = self.mod_listbox.get(selected_index)
        mod_title = selected_mod[selected_mod.find("] ") + 2:]
        mod_id = self.mod_id_map.get(mod_title)
        if mod_id:
            url = self.mod_steam_urls.get(mod_id)
            if url:
                webbrowser.open(url)

    def import_mod(self):
        url = simpledialog.askstring("Import Mod", "Enter the Steam Workshop URL of the mod:")
        if url:
            mod_id = url.split("/")[-1]  # Extract the mod ID from the URL
            asyncio.run(self.load_mod_details(mod_id))
            self.mod_id_map[mod_id] = mod_id
            self.mod_tags[mod_id] = []  # Initialize tags as an empty list
            self.mod_status[mod_id] = "Pending"  # Set default status
            self.mod_steam_urls[mod_id] = url
            self.filter_mod_list()

    def select_mod_dir(self):
        self.mod_dir = filedialog.askdirectory(title="Select Mod Directory")
        if self.mod_dir:
            self.load_mods_from_dir(self.mod_dir)
            messagebox.showinfo("Directory Selected", f"Mod directory set to: {self.mod_dir}")

    def load_mods_from_dir(self, directory):
        self.mod_listbox.delete(0, tk.END)
        self.mod_id_map.clear()  # Clear existing mod entries
        self.mod_tags.clear()
        self.mod_status.clear()
        self.mod_steam_urls.clear()
        
        for root, dirs, files in os.walk(directory):
            for filename in files:
                if filename.endswith(".mod"):  # Adjust file extension as needed
                    mod_title = os.path.splitext(filename)[0]  # Using filename without extension as title
                    self.mod_id_map[mod_title] = filename
                    self.mod_tags[mod_title] = []  # Initialize tags as an empty list
                    self.mod_status[mod_title] = "Pending"  # Set default status
                    self.mod_steam_urls[filename] = ""  # Set URL as empty

        self.filter_mod_list()

    def save_to_database(self):
        conn = sqlite3.connect(self.database)
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS mods
                     (id TEXT PRIMARY KEY, title TEXT, tags TEXT, status TEXT, url TEXT)''')

        for mod_title, mod_id in self.mod_id_map.items():
            tags = ",".join(self.mod_tags.get(mod_title, []))
            status = self.mod_status.get(mod_title, "Pending")
            url = self.mod_steam_urls.get(mod_id, "")
            c.execute('REPLACE INTO mods (id, title, tags, status, url) VALUES (?, ?, ?, ?, ?)',
                      (mod_id, mod_title, tags, status, url))
        
        conn.commit()
        conn.close()

    def load_from_database(self):
        conn = sqlite3.connect(self.database)
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS mods
                     (id TEXT PRIMARY KEY, title TEXT, tags TEXT, status TEXT, url TEXT)''')

        c.execute('SELECT * FROM mods')
        rows = c.fetchall()

        for row in rows:
            mod_id, mod_title, tags, status, url = row
            self.mod_id_map[mod_title] = mod_id
            self.mod_tags[mod_title] = tags.split(",") if tags else []
            self.mod_status[mod_title] = status
            self.mod_steam_urls[mod_id] = url
        
        conn.close()
        self.filter_mod_list()

if __name__ == "__main__":
    root = tk.Tk()
    root.title("Mod Manager")
    root.geometry("1000x700")
    steam_api_key = "YOUR_STEAM_API_KEY_HERE"
    app = ModManager(root, steam_api_key)
    app.pack(fill=tk.BOTH, expand=True)
    root.mainloop()