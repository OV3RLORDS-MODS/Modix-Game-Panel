import tkinter as tk
from tkinter import ttk, messagebox

class HelpPage(tk.Frame):
    """
    A single-page ticket manager with:
      - A dark-themed Treeview at the bottom listing tickets.
      - An 'Add Ticket' button to open a dark-themed popup for creating a new ticket.
      - Double-click on any ticket row to open a detailed view popup (similar to WHMCS).
    """

    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.configure(bg="#1E1E2E")

        # 1) Create & configure a ttk.Style for the Treeview, headings, etc.
        self.style = ttk.Style(self)
        self.style.theme_use("clam")

        # Treeview body style
        self.style.configure(
            "Dark.Treeview",
            background="#2E2E2E",
            foreground="#FFFFFF",
            rowheight=24,
            fieldbackground="#2E2E2E"
        )
        # Treeview heading style
        self.style.configure(
            "Dark.Treeview.Heading",
            background="#1E1E2E",
            foreground="#FFFFFF",
            font=("Segoe UI", 10, "bold")
        )
        # Selection color mapping
        self.style.map(
            "Dark.Treeview",
            background=[("selected", "#44475A")],
            foreground=[("selected", "#FFFFFF")]
        )

        # In-memory tickets
        self.tickets = []
        self.next_ticket_id = 1

        # ============= HEADER: Title =============
        header_frame = tk.Frame(self, bg="#1E1E2E")
        header_frame.pack(fill="x", padx=10, pady=(10, 5))

        title_label = tk.Label(
            header_frame,
            text="Help & Support",
            font=("Segoe UI", 14, "bold"),
            fg="#FFFFFF",
            bg="#1E1E2E"
        )
        title_label.pack(side=tk.LEFT, padx=(0, 10))

        # ============= ACTION FRAME: Buttons =============
        action_frame = tk.Frame(self, bg="#1E1E2E")
        action_frame.pack(fill="x", padx=10, pady=5)

        self.view_btn = tk.Button(
            action_frame,
            text="View Details",
            command=self.view_ticket_details,
            font=("Segoe UI", 10, "bold"),
            bg="#44475A",
            fg="#FFFFFF",
            relief="flat"
        )
        self.view_btn.pack(side=tk.LEFT, padx=5)

        self.close_btn = tk.Button(
            action_frame,
            text="Close Ticket",
            command=self.close_ticket,
            font=("Segoe UI", 10, "bold"),
            bg="#44475A",
            fg="#FFFFFF",
            relief="flat"
        )
        self.close_btn.pack(side=tk.LEFT, padx=5)

        add_ticket_btn = tk.Button(
            action_frame,
            text="Add Ticket",
            command=self.open_add_ticket_popup,
            font=("Segoe UI", 10, "bold"),
            bg="#44475A",
            fg="#FFFFFF",
            relief="flat"
        )
        add_ticket_btn.pack(side=tk.LEFT, padx=5)

        # ============= MAIN (TICKET LIST) =============
        self.tree_frame = tk.Frame(self, bg="#1E1E2E")
        self.tree_frame.pack(fill="both", expand=True, padx=10, pady=(5, 10))

        columns = ("id", "name", "subject", "status")
        self.ticket_tree = ttk.Treeview(
            self.tree_frame,
            columns=columns,
            show="headings",
            height=12,
            style="Dark.Treeview"
        )
        self.ticket_tree.heading("id", text="Ticket ID", anchor="center")
        self.ticket_tree.heading("name", text="Name", anchor="center")
        self.ticket_tree.heading("subject", text="Subject", anchor="center")
        self.ticket_tree.heading("status", text="Status", anchor="center")

        self.ticket_tree.column("id", width=70, anchor="center")
        self.ticket_tree.column("name", width=120, anchor="center")
        self.ticket_tree.column("subject", width=220, anchor="center")
        self.ticket_tree.column("status", width=80, anchor="center")
        self.ticket_tree.pack(side=tk.LEFT, fill="both", expand=True)

        scrollbar = ttk.Scrollbar(self.tree_frame, orient="vertical", command=self.ticket_tree.yview)
        self.ticket_tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.LEFT, fill="y")

        # 2) Bind double-click event to open a detail popup
        self.ticket_tree.bind("<Double-1>", self.on_ticket_double_click)

    # -------------------------------------------------------------------------
    # ADD TICKET POPUP
    # -------------------------------------------------------------------------
    def open_add_ticket_popup(self):
        popup = tk.Toplevel(self)
        popup.title("Add New Ticket")
        popup.configure(bg="#1E1E2E")
        popup.resizable(False, False)
        # Center the popup
        popup.geometry("+%d+%d" % (
            self.winfo_rootx() + 100,
            self.winfo_rooty() + 100
        ))

        # Name
        tk.Label(
            popup, text="Name:", font=("Segoe UI", 10, "bold"),
            fg="#FFFFFF", bg="#1E1E2E"
        ).grid(row=0, column=0, sticky="e", padx=10, pady=5)
        name_var = tk.StringVar()
        name_entry = tk.Entry(
            popup, textvariable=name_var,
            font=("Segoe UI", 10), width=30,
            bg="#2E2E2E", fg="#FFFFFF", insertbackground="#FFFFFF"
        )
        name_entry.grid(row=0, column=1, padx=5, pady=5)

        # Subject
        tk.Label(
            popup, text="Subject:", font=("Segoe UI", 10, "bold"),
            fg="#FFFFFF", bg="#1E1E2E"
        ).grid(row=1, column=0, sticky="e", padx=10, pady=5)
        subject_var = tk.StringVar()
        subject_entry = tk.Entry(
            popup, textvariable=subject_var,
            font=("Segoe UI", 10), width=30,
            bg="#2E2E2E", fg="#FFFFFF", insertbackground="#FFFFFF"
        )
        subject_entry.grid(row=1, column=1, padx=5, pady=5)

        # Description
        tk.Label(
            popup, text="Description:", font=("Segoe UI", 10, "bold"),
            fg="#FFFFFF", bg="#1E1E2E"
        ).grid(row=2, column=0, sticky="ne", padx=10, pady=5)
        desc_text = tk.Text(
            popup, width=40, height=4,
            font=("Segoe UI", 10),
            bg="#2E2E2E", fg="#FFFFFF", insertbackground="#FFFFFF"
        )
        desc_text.grid(row=2, column=1, padx=5, pady=5)

        def submit_popup():
            name = name_var.get().strip()
            subject = subject_var.get().strip()
            description = desc_text.get("1.0", "end-1c").strip()

            if not name or not subject or not description:
                messagebox.showwarning("Incomplete", "Please fill out all fields.")
                return

            new_ticket = {
                "id": self.next_ticket_id,
                "name": name,
                "subject": subject,
                "description": description,
                "status": "Open"
            }
            self.tickets.append(new_ticket)
            self.next_ticket_id += 1

            messagebox.showinfo(
                "Ticket Submitted",
                f"Thank you, {name}!\nSubject: {subject}\n\nWe will review your ticket soon."
            )

            popup.destroy()
            self.update_ticket_list()

        submit_btn = tk.Button(
            popup, text="Submit Ticket",
            command=submit_popup,
            font=("Segoe UI", 10, "bold"),
            bg="#44475A", fg="#FFFFFF", relief="flat"
        )
        submit_btn.grid(row=3, column=1, sticky="e", pady=(10, 10))

    # -------------------------------------------------------------------------
    # TICKET LIST: REFRESH, VIEW DETAILS, CLOSE
    # -------------------------------------------------------------------------
    def update_ticket_list(self):
        for row in self.ticket_tree.get_children():
            self.ticket_tree.delete(row)
        for t in self.tickets:
            self.ticket_tree.insert(
                "", tk.END,
                values=(t["id"], t["name"], t["subject"], t["status"])
            )

    def view_ticket_details(self):
        selected = self.ticket_tree.focus()
        if not selected:
            messagebox.showwarning("No selection", "Please select a ticket.")
            return
        self._open_ticket_detail_popup(selected)

    def close_ticket(self):
        selected = self.ticket_tree.focus()
        if not selected:
            messagebox.showwarning("No selection", "Please select a ticket.")
            return

        values = self.ticket_tree.item(selected, "values")
        ticket_id = values[0]

        ticket = next((x for x in self.tickets if str(x["id"]) == str(ticket_id)), None)
        if not ticket:
            messagebox.showerror("Not Found", f"No ticket found with ID {ticket_id}")
            return

        if ticket["status"] == "Closed":
            messagebox.showinfo("Already Closed", "This ticket is already closed.")
            return

        ticket["status"] = "Closed"
        messagebox.showinfo("Ticket Closed", f"Ticket #{ticket_id} has been closed.")
        self.update_ticket_list()

    # -------------------------------------------------------------------------
    # DOUBLE-CLICK HANDLER
    # -------------------------------------------------------------------------
    def on_ticket_double_click(self, event):
        item_id = self.ticket_tree.focus()
        if not item_id:
            return
        self._open_ticket_detail_popup(item_id)

    def _open_ticket_detail_popup(self, item_id):
        values = self.ticket_tree.item(item_id, "values")
        ticket_id = values[0]
        ticket = next((x for x in self.tickets if str(x["id"]) == str(ticket_id)), None)
        if not ticket:
            messagebox.showerror("Not Found", f"No ticket found with ID {ticket_id}")
            return

        detail_win = tk.Toplevel(self)
        detail_win.title(f"Ticket #{ticket_id} Detail")
        detail_win.configure(bg="#1E1E2E")
        detail_win.geometry("+%d+%d" % (
            self.winfo_rootx() + 120,
            self.winfo_rooty() + 120
        ))
        detail_win.resizable(False, False)

        tk.Label(
            detail_win,
            text=f"Ticket #{ticket['id']}",
            font=("Segoe UI", 14, "bold"),
            fg="#FFFFFF", bg="#1E1E2E"
        ).grid(row=0, column=0, columnspan=2, padx=10, pady=(10, 5))

        tk.Label(
            detail_win, text="Name:", font=("Segoe UI", 10, "bold"),
            fg="#FFFFFF", bg="#1E1E2E"
        ).grid(row=1, column=0, sticky="e", padx=10, pady=5)
        tk.Label(
            detail_win, text=ticket["name"],
            font=("Segoe UI", 10),
            fg="#FFFFFF", bg="#1E1E2E"
        ).grid(row=1, column=1, sticky="w", padx=5, pady=5)

        tk.Label(
            detail_win, text="Subject:", font=("Segoe UI", 10, "bold"),
            fg="#FFFFFF", bg="#1E1E2E"
        ).grid(row=2, column=0, sticky="e", padx=10, pady=5)
        tk.Label(
            detail_win, text=ticket["subject"],
            font=("Segoe UI", 10),
            fg="#FFFFFF", bg="#1E1E2E"
        ).grid(row=2, column=1, sticky="w", padx=5, pady=5)

        tk.Label(
            detail_win, text="Status:", font=("Segoe UI", 10, "bold"),
            fg="#FFFFFF", bg="#1E1E2E"
        ).grid(row=3, column=0, sticky="e", padx=10, pady=5)
        tk.Label(
            detail_win, text=ticket["status"],
            font=("Segoe UI", 10),
            fg="#FFFFFF", bg="#1E1E2E"
        ).grid(row=3, column=1, sticky="w", padx=5, pady=5)

        tk.Label(
            detail_win, text="Description:", font=("Segoe UI", 10, "bold"),
            fg="#FFFFFF", bg="#1E1E2E"
        ).grid(row=4, column=0, sticky="ne", padx=10, pady=5)

        desc_box = tk.Text(
            detail_win, width=50, height=6,
            font=("Segoe UI", 10),
            bg="#2E2E2E", fg="#FFFFFF",
            insertbackground="#FFFFFF"
        )
        desc_box.grid(row=4, column=1, padx=5, pady=5)
        desc_box.insert("1.0", ticket["description"])
        desc_box.config(state=tk.DISABLED)

        close_btn = tk.Button(
            detail_win,
            text="Close Ticket",
            font=("Segoe UI", 10, "bold"),
            bg="#44475A",
            fg="#FFFFFF",
            relief="flat",
            command=lambda: self._close_ticket_from_popup(ticket, detail_win)
        )
        close_btn.grid(row=5, column=1, sticky="e", padx=5, pady=(10, 10))

    def _close_ticket_from_popup(self, ticket, detail_win):
        if ticket["status"] == "Closed":
            messagebox.showinfo("Already Closed", "This ticket is already closed.")
            return
        ticket["status"] = "Closed"
        messagebox.showinfo("Ticket Closed", f"Ticket #{ticket['id']} has been closed.")
        detail_win.destroy()
        self.update_ticket_list()
