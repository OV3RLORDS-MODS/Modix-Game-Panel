import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
import tkinter.font as tkfont
import re

class TextEditor(tk.Toplevel):
    def __init__(self, parent, file_path):
        super().__init__(parent)
        self.title(f"Editing {file_path}")
        self.geometry("800x600")
        self.configure(bg="#1E1E1E")
        self.file_path = file_path

        # Create a frame for the text area and search widgets
        self.text_frame = tk.Frame(self)
        self.text_frame.pack(expand=True, fill="both")

        # Add a text widget with line numbers
        self.text_area = tk.Text(self.text_frame, wrap="word", bg="#2E2E2E", fg="#00FF00", font=("Consolas", 12), undo=True)
        self.text_area.pack(side=tk.LEFT, expand=True, fill="both")

        self.scrollbar = tk.Scrollbar(self.text_frame, command=self.text_area.yview)
        self.scrollbar.pack(side=tk.RIGHT, fill="y")
        self.text_area.config(yscrollcommand=self.scrollbar.set)

        self.line_number_canvas = tk.Canvas(self.text_frame, width=40, bg="#1E1E1E", highlightthickness=0)
        self.line_number_canvas.pack(side=tk.LEFT, fill="y")

        self.text_area.bind("<KeyRelease>", self.update_line_numbers)
        self.text_area.bind("<MouseWheel>", self.update_line_numbers)
        self.update_line_numbers()

        # Add search and replace frame
        self.search_frame = tk.Frame(self, bg="#1E1E1E")
        self.search_frame.pack(fill=tk.X, padx=10, pady=5)

        self.search_entry = tk.Entry(self.search_frame, bg="#2E2E2E", fg="#00FF00", font=("Consolas", 12))
        self.search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        self.search_entry.bind('<Return>', self.search_text)

        search_button = tk.Button(self.search_frame, text="Search", command=self.search_text, bg="#2E2E2E", fg="#00FF00", font=("Consolas", 12), relief="flat")
        search_button.pack(side=tk.RIGHT, padx=5)

        replace_button = tk.Button(self.search_frame, text="Replace", command=self.replace_text, bg="#2E2E2E", fg="#00FF00", font=("Consolas", 12), relief="flat")
        replace_button.pack(side=tk.RIGHT, padx=5)

        self.info_frame = tk.Frame(self)
        self.info_frame.pack(fill=tk.X, padx=10, pady=5)

        self.word_count_label = tk.Label(self.info_frame, text="Words: 0", bg="#1E1E1E", fg="#00FF00", font=("Consolas", 12))
        self.word_count_label.pack(side=tk.LEFT)

        self.theme_button = tk.Button(self.info_frame, text="Toggle Theme", command=self.toggle_theme, bg="#2E2E2E", fg="#00FF00", font=("Consolas", 12), relief="flat")
        self.theme_button.pack(side=tk.RIGHT, padx=5)

        self.font_size = 12
        self.font_size_button = tk.Button(self.info_frame, text="Font Size", command=self.change_font_size, bg="#2E2E2E", fg="#00FF00", font=("Consolas", 12), relief="flat")
        self.font_size_button.pack(side=tk.RIGHT, padx=5)

        self.load_file()

        save_button = tk.Button(self, text="Save", command=self.save_file, bg="#2E2E2E", fg="#00FF00", font=("Consolas", 12), relief="flat")
        save_button.pack(pady=10)

        # Bind keyboard shortcuts
        self.bind_all("<Control-o>", self.open_file)
        self.bind_all("<Control-s>", self.save_file)
        self.bind_all("<Control-n>", self.new_file)

    def load_file(self):
        """Load the contents of the file into the text area."""
        try:
            with open(self.file_path, 'r') as file:
                content = file.read()
                self.text_area.insert("1.0", content)
                self.update_word_count()
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred while loading the file: {e}")

    def save_file(self, event=None):
        """Save the contents of the text area back to the file."""
        try:
            with open(self.file_path, 'w') as file:
                content = self.text_area.get("1.0", "end-1c")
                file.write(content)
            messagebox.showinfo("Success", "File saved successfully.")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred while saving the file: {e}")

    def search_text(self, event=None):
        """Search for text in the text area and highlight it."""
        search_term = self.search_entry.get()
        self.text_area.tag_remove("highlight", "1.0", "end")

        if search_term:
            start_pos = "1.0"
            while True:
                start_pos = self.text_area.search(search_term, start_pos, nocase=True, stopindex="end")
                if not start_pos:
                    break
                end_pos = f"{start_pos}+{len(search_term)}c"
                self.text_area.tag_add("highlight", start_pos, end_pos)
                self.text_area.tag_config("highlight", background="#3333FF", foreground="#FFFFFF")
                start_pos = end_pos

    def replace_text(self):
        """Replace text in the text area."""
        search_term = self.search_entry.get()
        if not search_term:
            messagebox.showwarning("Input Error", "Search term cannot be empty.")
            return
        
        replace_term = simpledialog.askstring("Replace", "Replace with:")
        if replace_term is None:
            return

        content = self.text_area.get("1.0", "end-1c")
        new_content = content.replace(search_term, replace_term)
        self.text_area.delete("1.0", "end")
        self.text_area.insert("1.0", new_content)
        self.update_line_numbers()
        self.update_word_count()

    def update_line_numbers(self, event=None):
        """Update line numbers in the line number canvas."""
        self.line_number_canvas.delete("all")
        line_count = int(self.text_area.index("end-1c").split(".")[0])
        for i in range(1, line_count + 1):
            self.line_number_canvas.create_text(2, (i * 20), anchor="nw", text=str(i), fill="#00FF00", font=("Consolas", 12))

    def update_word_count(self):
        """Update the word count label."""
        content = self.text_area.get("1.0", "end-1c")
        word_count = len(re.findall(r'\b\w+\b', content))
        self.word_count_label.config(text=f"Words: {word_count}")

    def toggle_theme(self):
        """Toggle between dark and light themes."""
        current_bg = self.text_area.cget("bg")
        if current_bg == "#2E2E2E":  # Dark theme
            self.text_area.config(bg="#FFFFFF", fg="#000000")
            self.line_number_canvas.config(bg="#FFFFFF")
            self.search_entry.config(bg="#FFFFFF", fg="#000000")
            self.search_frame.config(bg="#FFFFFF")
            self.info_frame.config(bg="#FFFFFF")
            self.configure(bg="#FFFFFF")
            self.word_count_label.config(bg="#FFFFFF", fg="#000000")
            self.theme_button.config(bg="#FFFFFF", fg="#000000")
            self.font_size_button.config(bg="#FFFFFF", fg="#000000")
        else:  # Light theme
            self.text_area.config(bg="#2E2E2E", fg="#00FF00")
            self.line_number_canvas.config(bg="#1E1E1E")
            self.search_entry.config(bg="#2E2E2E", fg="#00FF00")
            self.search_frame.config(bg="#1E1E1E")
            self.info_frame.config(bg="#1E1E1E")
            self.configure(bg="#1E1E1E")
            self.word_count_label.config(bg="#1E1E1E", fg="#00FF00")
            self.theme_button.config(bg="#2E2E2E", fg="#00FF00")
            self.font_size_button.config(bg="#2E2E2E", fg="#00FF00")

    def change_font_size(self):
        """Change the font size of the text area."""
        new_size = simpledialog.askinteger("Font Size", "Enter new font size:", initialvalue=self.font_size)
        if new_size:
            self.font_size = new_size
            self.text_area.config(font=("Consolas", self.font_size))
            self.update_line_numbers()

    def open_file(self, event=None):
        """Open a new file."""
        file_path = filedialog.askopenfilename(filetypes=[("Text Files", "*.txt")])
        if file_path:
            self.file_path = file_path
            self.title(f"Editing {file_path}")
            self.text_area.delete("1.0", "end")
            self.load_file()

    def new_file(self, event=None):
        """Create a new file."""
        self.text_area.delete("1.0", "end")
        self.file_path = None
        self.title("Untitled")
        self.update_word_count()

if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()  # Hide the main root window
    file_path = filedialog.askopenfilename(filetypes=[("Text Files", "*.txt")])
    if file_path:
        editor = TextEditor(root, file_path)
        editor.mainloop()