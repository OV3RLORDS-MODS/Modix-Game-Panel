import tkinter as tk
from tkinter import messagebox, ttk, simpledialog, colorchooser
import requests
import json
import re
import datetime

class DiscordTools(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.config(bg="#2C2F33")
        self.webhooks = {}
        self.post_color = "#FFFFFF"
        self.create_widgets()
        self.load_webhooks()
        self.default_messages = {
            "start": "Server Online: Rise of the Undead – The Apocalypse Begins!",
            "stop": "🛑 Project Zomboid: Darkness Falls... The Apocalypse Pauses 🛑",
            "restart": "Server Restart: The Outbreak Reignites – Brace for Impact! "
        }
        self.default_descriptions = {
            "start": "The gates of hell have opened! The server is now live, and the streets are swarming with the undead. Gather your allies, fortify your base, and prepare for relentless survival in a world overrun by zombies. Will you conquer the chaos, or be consumed by it?",
            "stop": "The nightmare takes a brief pause as the server shuts down. The undead may rest, but don’t get too comfortable... survival never stops!",
            "restart": "The clock resets, but the danger escalates. As the server roars back to life, the infection intensifies, and the undead close in with newfound ferocity. This isn’t just survival anymore—it’s war. Rally your strength, survivors. The apocalypse waits for no one."
        }
        self.default_footer = "Powered by Node Manager"

    def create_widgets(self):
        # --- Top Buttons Frame ---
        top_frame = tk.Frame(self, bg="#23272A")
        top_frame.pack(fill=tk.X, padx=10, pady=10)

        self.add_button = self.create_button(top_frame, "Add Webhook", self.add_webhook, "#4CAF50")
        self.add_button.pack(side=tk.LEFT, padx=5)

        self.save_button = self.create_button(top_frame, "Save Webhooks", self.save_webhooks_to_file, "#7289DA")
        self.save_button.pack(side=tk.LEFT, padx=5)

        self.edit_button = self.create_button(top_frame, "Edit Webhook", self.edit_webhook, "#FFA500")
        self.edit_button.pack(side=tk.LEFT, padx=5)

        self.clear_history_button = self.create_button(top_frame, "Clear History", self.clear_history, "#FF0000")
        self.clear_history_button.pack(side=tk.LEFT, padx=5)

        self.export_history_button = self.create_button(top_frame, "Export History", self.export_history, "#009688")
        self.export_history_button.pack(side=tk.LEFT, padx=5)

        # --- Webhook Selection Frame ---
        webhook_frame = tk.Frame(self, bg="#2C2F33")
        webhook_frame.pack(fill=tk.X, padx=10, pady=10)

        self.webhook_label = tk.Label(webhook_frame, text="Select Webhook:", bg="#2C2F33", fg="#FFFFFF", font=("Segoe UI", 12))
        self.webhook_label.pack(side=tk.LEFT, padx=5)

        self.webhook_combo = ttk.Combobox(webhook_frame, font=("Segoe UI", 12))
        self.webhook_combo.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # --- New Webhook Frame ---
        new_webhook_frame = tk.Frame(self, bg="#2C2F33")
        new_webhook_frame.pack(fill=tk.X, padx=10, pady=10)

        self.new_webhook_label = tk.Label(new_webhook_frame, text="New Webhook URL:", bg="#2C2F33", fg="#FFFFFF", font=("Segoe UI", 12))
        self.new_webhook_label.pack(side=tk.LEFT, padx=5)

        self.new_webhook_entry = tk.Entry(new_webhook_frame, bg="#23272A", fg="#FFFFFF", font=("Segoe UI", 12))
        self.new_webhook_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # --- Bot Name Frame ---
        bot_name_frame = tk.Frame(self, bg="#2C2F33")
        bot_name_frame.pack(fill=tk.X, padx=10, pady=5)

        self.bot_name_label = tk.Label(bot_name_frame, text="Bot Username:", bg="#2C2F33", fg="#FFFFFF", font=("Segoe UI", 12))
        self.bot_name_label.pack(side=tk.LEFT, padx=5)

        self.bot_name_entry = tk.Entry(bot_name_frame, bg="#23272A", fg="#FFFFFF", font=("Segoe UI", 12))
        self.bot_name_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.bot_name_entry.insert(0, "Custom Bot")

        # --- Message Customization Frame ---
        message_frame = tk.Frame(self, bg="#2C2F33")
        message_frame.pack(fill=tk.BOTH, padx=10, pady=10, expand=True)

        self.message_title_label = tk.Label(message_frame, text="Title:", bg="#2C2F33", fg="#FFFFFF", font=("Segoe UI", 10))
        self.message_title_label.pack(anchor=tk.W, padx=5)
        self.message_title_entry = tk.Entry(message_frame, bg="#23272A", fg="#FFFFFF", font=("Segoe UI", 12))
        self.message_title_entry.pack(fill=tk.X, padx=5, pady=5)

        self.message_description_label = tk.Label(message_frame, text="Description:", bg="#2C2F33", fg="#FFFFFF", font=("Segoe UI", 10))
        self.message_description_label.pack(anchor=tk.W, padx=5)
        self.message_description_text = tk.Text(message_frame, bg="#23272A", fg="#FFFFFF", font=("Segoe UI", 12), wrap=tk.WORD, height=5)
        self.message_description_text.pack(fill=tk.X, padx=5, pady=5)

        self.message_image_label = tk.Label(message_frame, text="Image URL:", bg="#2C2F33", fg="#FFFFFF", font=("Segoe UI", 10))
        self.message_image_label.pack(anchor=tk.W, padx=5)
        self.message_image_entry = tk.Entry(message_frame, bg="#23272A", fg="#FFFFFF", font=("Segoe UI", 12))
        self.message_image_entry.pack(fill=tk.X, padx=5, pady=5)

        self.message_footer_label = tk.Label(message_frame, text="Footer:", bg="#2C2F33", fg="#FFFFFF", font=("Segoe UI", 10))
        self.message_footer_label.pack(anchor=tk.W, padx=5)
        self.message_footer_entry = tk.Entry(message_frame, bg="#23272A", fg="#FFFFFF", font=("Segoe UI", 12))
        self.message_footer_entry.pack(fill=tk.X, padx=5, pady=5)

        # --- Color Picker Frame ---
        color_frame = tk.Frame(self, bg="#2C2F33")
        color_frame.pack(fill=tk.X, padx=10, pady=10)

        self.color_label = tk.Label(color_frame, text="Post Color:", bg="#2C2F33", fg="#FFFFFF", font=("Segoe UI", 12))
        self.color_label.pack(side=tk.LEFT, padx=5)

        self.color_button = self.create_button(color_frame, "Choose Color", self.choose_color, "#7289DA")
        self.color_button.pack(side=tk.LEFT, padx=5)

        # --- Buttons for Sending Messages ---
        buttons_frame = tk.Frame(self, bg="#2C2F33")
        buttons_frame.pack(fill=tk.X, padx=10, pady=10)

        self.send_custom_message_button = self.create_button(buttons_frame, "Send Custom Message", self.send_custom_message, "#4CAF50")
        self.send_custom_message_button.pack(side=tk.LEFT, padx=5)

        self.start_button = self.create_button(buttons_frame, "Customize & Send Start Message", lambda: self.show_customization_dialog("start"), "#4CAF50")
        self.start_button.pack(side=tk.LEFT, padx=5)

        self.stop_button = self.create_button(buttons_frame, "Customize & Send Stop Message", lambda: self.show_customization_dialog("stop"), "#FF9800")
        self.stop_button.pack(side=tk.LEFT, padx=5)

        self.restart_button = self.create_button(buttons_frame, "Customize & Send Restart Message", lambda: self.show_customization_dialog("restart"), "#03A9F4")
        self.restart_button.pack(side=tk.LEFT, padx=5)

        # --- Webhook History Frame ---
        history_frame = tk.Frame(self, bg="#2C2F33")
        history_frame.pack(fill=tk.BOTH, padx=10, pady=10, expand=True)

        self.history_label = tk.Label(history_frame, text="Webhook History:", bg="#2C2F33", fg="#FFFFFF", font=("Segoe UI", 12))
        self.history_label.pack(anchor=tk.W, padx=5)

        self.history_listbox = tk.Listbox(history_frame, bg="#23272A", fg="#FFFFFF", font=("Segoe UI", 12))
        self.history_listbox.pack(fill=tk.BOTH, padx=5, pady=5, expand=True)

        self.search_entry = tk.Entry(history_frame, bg="#23272A", fg="#FFFFFF", font=("Segoe UI", 12))
        self.search_entry.pack(fill=tk.X, padx=5, pady=5)
        self.search_entry.bind('<KeyRelease>', self.search_history)

    def create_button(self, parent, text, command, color):
        return tk.Button(parent, text=text, command=command, bg=color, fg="#FFFFFF", font=("Segoe UI", 10))

    def choose_color(self):
        color_code = colorchooser.askcolor(title="Choose Color")[1]
        if color_code:
            self.post_color = color_code

    def add_webhook(self):
        webhook_url = self.new_webhook_entry.get().strip()
        if not webhook_url or not self.is_valid_webhook_url(webhook_url):
            messagebox.showwarning("Invalid Webhook URL", "Please enter a valid Discord webhook URL.")
            return

        name = self.ask_for_webhook_name()
        if not name:
            return

        if name in self.webhooks:
            messagebox.showwarning("Webhook Name Exists", "Webhook name already exists. Choose a different name.")
            return

        self.webhooks[name] = webhook_url
        self.update_webhook_combo()
        self.save_webhooks_to_file()
        messagebox.showinfo("Webhook Added", f"Webhook '{name}' added successfully.")

    def is_valid_webhook_url(self, url):
        pattern = r"https://discord.com/api/webhooks/\d+/[\w-]{64}"
        match = re.match(pattern, url)
        print(f"URL: {url}, Valid: {bool(match)}")  # Debug print
        return bool(match)

    def edit_webhook(self):
        selected_name = self.webhook_combo.get()
        if not selected_name or selected_name not in self.webhooks:
            messagebox.showwarning("No Webhook Selected", "Please select a valid webhook to edit.")
            return

        new_name = self.ask_for_webhook_name()
        if not new_name:
            return

        self.webhooks[new_name] = self.webhooks.pop(selected_name)
        self.update_webhook_combo()
        self.save_webhooks_to_file()

    def ask_for_webhook_name(self):
        new_window = tk.Toplevel(self)
        new_window.title("Webhook Name")

        tk.Label(new_window, text="Enter Webhook Name:", padx=10, pady=5).pack()

        name_entry = tk.Entry(new_window)
        name_entry.pack(padx=10, pady=5)

        result = [None]

        def on_ok():
            name = name_entry.get().strip()
            if name:
                result[0] = name
                new_window.destroy()
            else:
                messagebox.showwarning("Invalid Name", "Webhook name cannot be empty.")

        ok_button = tk.Button(new_window, text="OK", command=on_ok)
        ok_button.pack(pady=10)

        new_window.wait_window()
        return result[0]

    def save_webhooks_to_file(self):
        with open('webhooks.json', 'w') as file:
            json.dump(self.webhooks, file)
        print("Webhooks saved to file.")  # Debug print

    def load_webhooks(self):
        try:
            with open('webhooks.json', 'r') as file:
                self.webhooks = json.load(file)
            self.update_webhook_combo()
        except FileNotFoundError:
            messagebox.showinfo("No Webhooks", "No saved webhooks found.")
        print("Webhooks loaded from file.")  # Debug print

    def update_webhook_combo(self):
        self.webhook_combo['values'] = list(self.webhooks.keys())
        self.webhook_combo.set('')

    def send_webhook(self, title, description, image_url=None, footer=None, bot_name=None):
        webhook_name = self.webhook_combo.get()
        if not webhook_name or webhook_name not in self.webhooks:
            messagebox.showwarning("No Webhook Selected", "Please select a valid webhook.")
            return

        webhook_url = self.webhooks[webhook_name]
        data = {
            "username": bot_name or "Webhook Bot",
            "embeds": [
                {
                    "title": title,
                    "description": description,
                    "color": int(self.post_color[1:], 16),
                }
            ]
        }

        if image_url:
            data["embeds"][0]["image"] = {"url": image_url}
        if footer:
            data["embeds"][0]["footer"] = {"text": footer}

        try:
            response = requests.post(webhook_url, json=data)
            if response.status_code == 204:
                timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                self.history_listbox.insert(tk.END, f"[{timestamp}] Sent: {title} - {description}")
                messagebox.showinfo("Success", "Message sent successfully.")
            else:
                messagebox.showerror("Error", f"Failed to send message: {response.status_code}")
        except requests.exceptions.RequestException as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")

    def send_custom_message(self):
        title = self.message_title_entry.get()
        description = self.message_description_text.get("1.0", tk.END).strip()
        image_url = self.message_image_entry.get()
        footer = self.message_footer_entry.get()
        bot_name = self.bot_name_entry.get()

        if not title or not description:
            messagebox.showwarning("Missing Fields", "Please enter both title and description.")
            return

        self.send_webhook(title, description, image_url, footer, bot_name)

    def show_customization_dialog(self, message_type):
        default_title = self.default_messages[message_type]
        default_description = self.default_descriptions[message_type]
        default_footer = self.default_footer

        dialog = tk.Toplevel(self)
        dialog.title(f"Customize {message_type.capitalize()} Message")

        tk.Label(dialog, text="Title:").grid(row=0, column=0, padx=10, pady=5)
        title_entry = tk.Entry(dialog)
        title_entry.insert(0, default_title)
        title_entry.grid(row=0, column=1, padx=10, pady=5)

        tk.Label(dialog, text="Description:").grid(row=1, column=0, padx=10, pady=5)
        description_text = tk.Text(dialog, height=4, width=50)
        description_text.insert(tk.END, default_description)
        description_text.grid(row=1, column=1, padx=10, pady=5)

        tk.Label(dialog, text="Footer:").grid(row=2, column=0, padx=10, pady=5)
        footer_entry = tk.Entry(dialog)
        footer_entry.insert(0, default_footer)
        footer_entry.grid(row=2, column=1, padx=10, pady=5)

        def on_ok():
            title = title_entry.get().strip()
            description = description_text.get("1.0", tk.END).strip()
            footer = footer_entry.get().strip()
            if title and description:
                self.send_webhook(title, description, footer=footer)
                dialog.destroy()
            else:
                messagebox.showwarning("Missing Fields", "Please enter both title and description.")

        tk.Button(dialog, text="Send", command=on_ok).grid(row=3, column=1, padx=10, pady=10, sticky=tk.E)

        self.wait_window(dialog)

    def clear_history(self):
        self.history_listbox.delete(0, tk.END)

    def export_history(self):
        with open('history.txt', 'w') as file:
            for entry in self.history_listbox.get(0, tk.END):
                file.write(entry + '\n')
        messagebox.showinfo("History Exported", "History has been exported to 'history.txt'.")

    def search_history(self, event):
        search_term = self.search_entry.get().lower()
        for index in range(self.history_listbox.size()):
            entry = self.history_listbox.get(index).lower()
            if search_term in entry:
                self.history_listbox.select_set(index)
                self.history_listbox.see(index)
                return
        self.history_listbox.selection_clear(0, tk.END)

if __name__ == "__main__":
    root = tk.Tk()
    root.title("Discord Webhook Sender")
    root.geometry("600x800")
    DiscordTools(root).pack(fill="both", expand=True)
    root.mainloop()
