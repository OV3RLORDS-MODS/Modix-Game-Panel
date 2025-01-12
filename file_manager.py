import os
import shutil
import zipfile
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog

class FileManager(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.configure(bg="#1E1E1E")
        self.parent = parent
        self.current_path = os.getcwd()
        self.original_items = []  # Store original directory contents
        self.current_file = None  # Track the currently opened file

        # Default colors
        self.selection_color = "#004000"

        self.create_widgets()
        self.list_directory()

    def create_widgets(self):
        # Path display with breadcrumb navigation
        path_frame = tk.Frame(self, bg="#1E1E1E")
        path_frame.pack(fill=tk.X, padx=10, pady=5)

        self.path_label = tk.Label(path_frame, text=self.current_path, bg="#1E1E1E", fg="#00FF00", font=("Consolas", 12))
        self.path_label.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # Directory selection and Back buttons
        button_frame = tk.Frame(path_frame, bg="#1E1E1E")
        button_frame.pack(side=tk.RIGHT)

        select_dir_button = tk.Button(button_frame, text="Select Directory", command=self.select_directory,
                                      bg="#2E2E2E", fg="#00FF00", font=("Consolas", 12), relief="flat")
        select_dir_button.pack(side=tk.LEFT, padx=5)

        self.back_button = tk.Button(button_frame, text="Back", command=self.go_back,
                                     bg="#2E2E2E", fg="#00FF00", font=("Consolas", 12), relief="flat")
        self.back_button.pack(side=tk.LEFT, padx=5)

        # Upload and Extract buttons
        upload_file_button = tk.Button(self, text="Upload File", command=self.upload_file,
                                       bg="#2E2E2E", fg="#00FF00", font=("Consolas", 12), relief="flat")
        upload_file_button.pack(padx=10, pady=5, anchor="w")

        upload_zip_button = tk.Button(self, text="Upload ZIP", command=self.upload_zip,
                                      bg="#2E2E2E", fg="#00FF00", font=("Consolas", 12), relief="flat")
        upload_zip_button.pack(padx=10, pady=5, anchor="w")

        extract_button = tk.Button(self, text="Extract ZIP", command=self.extract_zip,
                                   bg="#2E2E2E", fg="#00FF00", font=("Consolas", 12), relief="flat")
        extract_button.pack(padx=10, pady=5, anchor="w")

        # Search bar
        search_frame = tk.Frame(self, bg="#1E1E1E")
        search_frame.pack(fill=tk.X, padx=10, pady=5)

        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", self.update_search_results)

        self.search_entry = tk.Entry(search_frame, textvariable=self.search_var, bg="#2E2E2E", fg="#00FF00", font=("Consolas", 12))
        self.search_entry.pack(fill=tk.X, expand=True)

        # Directory content display
        self.listbox = tk.Listbox(self, width=80, height=20, bg="#1E1E1E", fg="#00FF00", font=("Consolas", 12),
                                 selectbackground=self.selection_color, selectforeground="#FFFFFF")
        self.listbox.pack(padx=10, pady=5, fill=tk.BOTH, expand=True)
        self.listbox.bind('<Double-1>', self.on_item_double_click)
        self.listbox.bind('<Button-3>', self.show_context_menu)

        # File operations buttons
        button_frame = tk.Frame(self, bg="#1E1E1E")
        button_frame.pack(pady=10)

        self.view_button = tk.Button(button_frame, text="View", command=self.view_file,
                                     bg="#2E2E2E", fg="#00FF00", font=("Consolas", 12), relief="flat", width=12)
        self.view_button.grid(row=0, column=0, padx=5, pady=5)

        self.copy_button = tk.Button(button_frame, text="Copy", command=self.copy_file,
                                     bg="#2E2E2E", fg="#00FF00", font=("Consolas", 12), relief="flat", width=12)
        self.copy_button.grid(row=0, column=1, padx=5, pady=5)

        self.move_button = tk.Button(button_frame, text="Move", command=self.move_file,
                                     bg="#2E2E2E", fg="#00FF00", font=("Consolas", 12), relief="flat", width=12)
        self.move_button.grid(row=0, column=2, padx=5, pady=5)

        self.rename_button = tk.Button(button_frame, text="Rename", command=self.rename_file,
                                       bg="#2E2E2E", fg="#00FF00", font=("Consolas", 12), relief="flat", width=12)
        self.rename_button.grid(row=1, column=0, padx=5, pady=5)

        self.delete_button = tk.Button(button_frame, text="Delete", command=self.delete_file,
                                       bg="#2E2E2E", fg="#00FF00", font=("Consolas", 12), relief="flat", width=12)
        self.delete_button.grid(row=1, column=1, padx=5, pady=5)

        self.create_dir_button = tk.Button(button_frame, text="New Folder", command=self.create_directory,
                                           bg="#2E2E2E", fg="#00FF00", font=("Consolas", 12), relief="flat", width=12)
        self.create_dir_button.grid(row=1, column=2, padx=5, pady=5)

        # Context menu for right-click actions
        self.context_menu = tk.Menu(self, tearoff=0, bg="#2E2E2E", fg="#00FF00", font=("Consolas", 12))
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
            self.original_items = sorted(os.listdir(self.current_path))  # Store original items
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
        if query == "":  # Restore original list if search is empty
            for item in self.original_items:
                full_path = os.path.join(self.current_path, item)
                if os.path.isdir(full_path):
                    item = f"[DIR] {item}"
                self.listbox.insert(tk.END, item)
        else:
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
        """View or edit the selected file."""
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

                text_window = tk.Toplevel(self)
                text_window.title(f"Viewing {selected_file}")
                text_window.geometry("800x600")

                self.text_widget = tk.Text(text_window, wrap=tk.WORD, bg="#1E1E1E", fg="#00FF00", font=("Consolas", 12))
                self.text_widget.insert(tk.END, content)
                self.text_widget.pack(fill=tk.BOTH, expand=True)

                button_frame = tk.Frame(text_window, bg="#1E1E1E")
                button_frame.pack(fill=tk.X, padx=10, pady=5)

                save_button = tk.Button(button_frame, text="Save", command=self.save_file,
                                        bg="#2E2E2E", fg="#00FF00", font=("Consolas", 12), relief="flat")
                save_button.pack(side=tk.LEFT, padx=5)

                save_as_button = tk.Button(button_frame, text="Save As", command=self.save_file_as,
                                           bg="#2E2E2E", fg="#00FF00", font=("Consolas", 12), relief="flat")
                save_as_button.pack(side=tk.LEFT, padx=5)

                self.current_file = file_path  # Track the currently opened file

    def save_file(self):
        """Save changes to the currently opened file."""
        if self.current_file:
            try:
                with open(self.current_file, "w") as file:
                    content = self.text_widget.get("1.0", tk.END)
                    file.write(content)
                messagebox.showinfo("Success", "File saved successfully.")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save file: {e}")
        else:
            self.save_file_as()  # If no file is currently open, prompt for "Save As"

    def save_file_as(self):
        """Save changes to a new file."""
        if self.current_file:
            content = self.text_widget.get("1.0", tk.END)
        else:
            content = ""

        new_file_path = filedialog.asksaveasfilename(defaultextension=".txt", title="Save File As")
        if new_file_path:
            try:
                with open(new_file_path, "w") as file:
                    file.write(content)
                messagebox.showinfo("Success", "File saved successfully.")
                self.current_file = new_file_path  # Update the currently opened file
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save file: {e}")

    def copy_file(self):
        """Copy the selected file to a new location."""
        selected_file = self.get_selected_file()
        if selected_file:
            source = os.path.join(self.current_path, selected_file)
            destination = filedialog.asksaveasfilename(initialfile=selected_file, title="Select Destination")
            if destination:
                try:
                    shutil.copy(source, destination)
                    messagebox.showinfo("Success", "File copied successfully.")
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to copy file: {e}")

    def move_file(self):
        """Move the selected file to a new location."""
        selected_file = self.get_selected_file()
        if selected_file:
            source = os.path.join(self.current_path, selected_file)
            destination = filedialog.asksaveasfilename(initialfile=selected_file, title="Select Destination")
            if destination:
                try:
                    shutil.move(source, destination)
                    messagebox.showinfo("Success", "File moved successfully.")
                    self.list_directory()  # Refresh directory contents
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to move file: {e}")

    def rename_file(self):
        """Rename the selected file."""
        selected_file = self.get_selected_file()
        if selected_file:
            new_name = simpledialog.askstring("Rename", "Enter new file name:", initialvalue=selected_file)
            if new_name:
                try:
                    os.rename(os.path.join(self.current_path, selected_file),
                              os.path.join(self.current_path, new_name))
                    self.list_directory()  # Refresh directory contents
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to rename file: {e}")

    def delete_file(self):
        """Delete the selected file."""
        selected_file = self.get_selected_file()
        if selected_file:
            confirm = messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete '{selected_file}'?")
            if confirm:
                try:
                    os.remove(os.path.join(self.current_path, selected_file))
                    self.list_directory()  # Refresh directory contents
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to delete file: {e}")

    def create_directory(self):
        """Create a new directory."""
        new_dir_name = simpledialog.askstring("New Folder", "Enter new folder name:")
        if new_dir_name:
            try:
                os.makedirs(os.path.join(self.current_path, new_dir_name))
                self.list_directory()  # Refresh directory contents
            except Exception as e:
                messagebox.showerror("Error", f"Failed to create directory: {e}")

    def upload_file(self):
        """Upload a file from local file system."""
        file_path = filedialog.askopenfilename(title="Select file to upload")
        if file_path:
            try:
                shutil.copy(file_path, self.current_path)
                self.list_directory()  # Refresh directory contents
            except Exception as e:
                messagebox.showerror("Error", f"Failed to upload file: {e}")

    def upload_zip(self):
        """Upload and extract a ZIP file."""
        zip_path = filedialog.askopenfilename(filetypes=[("ZIP files", "*.zip")], title="Select ZIP file")
        if zip_path:
            try:
                with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                    zip_ref.extractall(self.current_path)
                self.list_directory()  # Refresh directory contents
            except Exception as e:
                messagebox.showerror("Error", f"Failed to upload ZIP file: {e}")

    def extract_zip(self):
        """Extract the selected ZIP file."""
        selected_file = self.get_selected_file()
        if selected_file and selected_file.lower().endswith('.zip'):
            zip_path = os.path.join(self.current_path, selected_file)
            try:
                with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                    extract_dir = filedialog.askdirectory(title="Select Extraction Directory")
                    if extract_dir:
                        zip_ref.extractall(extract_dir)
                        messagebox.showinfo("Success", "ZIP file extracted successfully.")
                        self.list_directory()  # Refresh directory contents
            except Exception as e:
                messagebox.showerror("Error", f"Failed to extract ZIP file: {e}")

    def get_selected_file(self):
        """Get the currently selected file in the listbox."""
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