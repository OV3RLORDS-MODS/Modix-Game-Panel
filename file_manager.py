import os
import shutil
import zipfile
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog

class FileManager(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        # Check if this script is being run directly
        if __name__ == "__main__":
            messagebox.showerror("Error", "You cannot run mods.py directly. Please run app.py.")
            sys.exit()  # Exit if the script is executed directly without going through app.py

        self.configure(bg="#1E1E2E")  # Match terminal theme
        self.parent = parent
        self.current_path = os.getcwd()
        self.original_items = []  # Store original directory contents
        self.current_file = None  # Track the currently opened file

        # Default colors and fonts
        self.selection_color = "#6272A4"
        self.font_style = ("Segoe UI", 10)
        self.title_font = ("Segoe UI", 12, "bold")

        self.create_widgets()
        self.list_directory()

    def create_widgets(self):
        # Path display with breadcrumb navigation
        path_frame = tk.Frame(self, bg="#1E1E2E")
        path_frame.pack(fill=tk.X, padx=10, pady=5)

        self.path_label = tk.Label(
            path_frame, text=self.current_path, bg="#1E1E2E", fg="#FFFFFF", font=self.title_font
        )
        self.path_label.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # Directory selection and Back buttons
        button_frame = tk.Frame(path_frame, bg="#1E1E2E")
        button_frame.pack(side=tk.RIGHT)

        select_dir_button = tk.Button(
            button_frame,
            text="Select Directory",
            command=self.select_directory,
            bg="#44475A",
            fg="#FFFFFF",
            font=self.font_style,
            relief="flat",
        )
        select_dir_button.pack(side=tk.LEFT, padx=5)

        self.back_button = tk.Button(
            button_frame,
            text="Back",
            command=self.go_back,
            bg="#44475A",
            fg="#FFFFFF",
            font=self.font_style,
            relief="flat",
        )
        self.back_button.pack(side=tk.LEFT, padx=5)

        # Search bar
        search_frame = tk.Frame(self, bg="#1E1E2E")
        search_frame.pack(fill=tk.X, padx=10, pady=5)

        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", self.update_search_results)

        self.search_entry = tk.Entry(
            search_frame,
            textvariable=self.search_var,
            bg="#44475A",
            fg="#FFFFFF",
            font=self.font_style,
        )
        self.search_entry.pack(fill=tk.X, expand=True)

        # Directory content display
        self.listbox = tk.Listbox(
            self,
            width=80,
            height=20,
            bg="#1E1E2E",
            fg="#FFFFFF",
            font=self.font_style,
            selectbackground=self.selection_color,
            selectforeground="#FFFFFF",
        )
        self.listbox.pack(padx=10, pady=5, fill=tk.BOTH, expand=True)
        self.listbox.bind("<Double-1>", self.on_item_double_click)
        self.listbox.bind("<Button-3>", self.show_context_menu)

        # File operations buttons
        button_frame = tk.Frame(self, bg="#1E1E2E")
        button_frame.pack(pady=10)

        buttons = [
            ("View", self.view_file),
            ("Copy", self.copy_file),
            ("Move", self.move_file),
            ("Rename", self.rename_file),
            ("Delete", self.delete_file),
            ("New Folder", self.create_directory),
            ("Upload File", self.upload_file),
            ("Upload ZIP", self.upload_zip),
            ("Extract ZIP", self.extract_zip),
        ]

        for i, (text, command) in enumerate(buttons):
            button = tk.Button(
                button_frame,
                text=text,
                command=command,
                bg="#44475A",
                fg="#FFFFFF",
                font=self.font_style,
                relief="flat",
                width=12,
            )
            button.grid(row=i // 3, column=i % 3, padx=5, pady=5)

        # Context menu for right-click actions
        self.context_menu = tk.Menu(self, tearoff=0, bg="#44475A", fg="#FFFFFF", font=self.font_style)
        self.context_menu.add_command(label="View", command=self.view_file)
        self.context_menu.add_command(label="Copy", command=self.copy_file)
        self.context_menu.add_command(label="Move", command=self.move_file)
        self.context_menu.add_command(label="Rename", command=self.rename_file)
        self.context_menu.add_command(label="Delete", command=self.delete_file)

    def select_directory(self):
        """Allow user to select a directory."""
        selected_directory = filedialog.askdirectory(initialdir=self.current_path, title="Select Directory")
        if selected_directory:
            self.list_directory(selected_directory)

    def list_directory(self, path=None):
        """List directory contents."""
        if path:
            self.current_path = path
        self.path_label.config(text=self.current_path)
        self.listbox.delete(0, tk.END)
        try:
            self.original_items = sorted(os.listdir(self.current_path))
            for item in self.original_items:
                full_path = os.path.join(self.current_path, item)
                if os.path.isdir(full_path):
                    item = f"[DIR] {item}"
                self.listbox.insert(tk.END, item)
            self.update_search_results()  # Apply search filter
        except FileNotFoundError:
            messagebox.showerror("Error", "The directory does not exist.")
        except PermissionError:
            messagebox.showerror("Error", "You do not have permission to access this directory.")

    def update_search_results(self, *args):
        """Update the search results based on the search query."""
        query = self.search_var.get().lower()
        self.listbox.delete(0, tk.END)
        for item in self.original_items:
            if query in item.lower():
                full_path = os.path.join(self.current_path, item)
                if os.path.isdir(full_path):
                    item = f"[DIR] {item}"
                self.listbox.insert(tk.END, item)

    def on_item_double_click(self, event):
        """Handle double-click on item."""
        selected_item = self.listbox.get(tk.ACTIVE)
        item_name = selected_item.replace("[DIR] ", "")
        new_path = os.path.join(self.current_path, item_name)
        if os.path.isdir(new_path):
            self.list_directory(new_path)
        else:
            self.view_file()

    def go_back(self):
        """Navigate to the parent directory."""
        parent_dir = os.path.dirname(self.current_path)
        self.list_directory(parent_dir)

    def show_context_menu(self, event):
        """Show context menu on right-click."""
        self.context_menu.post(event.x_root, event.y_root)

    def view_file(self):
        """View the selected file."""
        selected_file = self.get_selected_file()
        if selected_file:
            file_path = os.path.join(self.current_path, selected_file)
            if os.path.isfile(file_path):
                content = ""
                try:
                    with open(file_path, "r") as file:
                        content = file.read()
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to read file: {e}")
                    return

                # Create text window
                text_window = tk.Toplevel(self)
                text_window.title(f"Viewing {selected_file}")
                text_window.geometry("800x600")

                text_widget = tk.Text(
                    text_window, wrap=tk.WORD, bg="#1E1E2E", fg="#FFFFFF", font=self.font_style
                )
                text_widget.insert(tk.END, content)
                text_widget.pack(fill=tk.BOTH, expand=True)

    def copy_file(self):
        """Copy the selected file."""
        # Implementation here

    def move_file(self):
        """Move the selected file."""
        # Implementation here

    def rename_file(self):
        """Rename the selected file."""
        # Implementation here

    def delete_file(self):
        """Delete the selected file."""
        # Implementation here

    def create_directory(self):
        """Create a new directory."""
        # Implementation here

    def upload_file(self):
        """Upload a file."""
        # Implementation here

    def upload_zip(self):
        """Upload and extract a ZIP file."""
        # Implementation here

    def extract_zip(self):
        """Extract the selected ZIP file."""
        # Implementation here

    def get_selected_file(self):
        """Get the currently selected file."""
        selection = self.listbox.curselection()
        if selection:
            selected_item = self.listbox.get(selection[0])
            return selected_item.replace("[DIR] ", "")
        return None


if __name__ == "__main__":
    root = tk.Tk()
    root.title("File Manager")
    root.geometry("800x600")
    app = FileManager(root)
    app.pack(fill=tk.BOTH, expand=True)
    root.mainloop()
