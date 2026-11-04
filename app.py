import secrets
import string
from tkinter import filedialog, messagebox

import customtkinter as ctk

from password_manager import PasswordManager

CLIPBOARD_CLEAR_MS = 30_000
KEY_TYPES = [("Key files", "*.key"), ("All files", "*.*")]
PW_TYPES = [("Password files", "*.pw"), ("All files", "*.*")]


class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        ctk.set_appearance_mode("system")
        ctk.set_default_color_theme("blue")
        self.title("PasSafe")
        self.geometry("860x560")
        self.minsize(760, 480)

        self.pm = PasswordManager()
        self.selected = None
        self.search_var = ctk.StringVar()
        self.search_var.trace_add("write", lambda *_: self._refresh_list())

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self._build_sidebar()
        self._build_main()
        self._update_status_labels()
        self._refresh_list()

    # ---------- layout ----------
    def _build_sidebar(self):
        side = ctk.CTkFrame(self, width=210, corner_radius=0)
        side.grid(row=0, column=0, rowspan=2, sticky="nsew")
        side.grid_propagate(False)

        ctk.CTkLabel(side, text="PasSafe", font=ctk.CTkFont(size=24, weight="bold")).pack(
            padx=20, pady=(24, 16), anchor="w")

        ctk.CTkLabel(side, text="1. Key", font=ctk.CTkFont(weight="bold")).pack(padx=20, anchor="w")
        ctk.CTkButton(side, text="New key", command=self.new_key).pack(padx=20, pady=(6, 4), fill="x")
        ctk.CTkButton(side, text="Load key", command=self.load_key).pack(padx=20, pady=4, fill="x")
        self.key_label = ctk.CTkLabel(side, text="", anchor="w", justify="left", wraplength=170)
        self.key_label.pack(padx=20, pady=(2, 16), anchor="w")

        ctk.CTkLabel(side, text="2. Password file", font=ctk.CTkFont(weight="bold")).pack(padx=20, anchor="w")
        ctk.CTkButton(side, text="New password file", command=self.new_file).pack(padx=20, pady=(6, 4), fill="x")
        ctk.CTkButton(side, text="Load password file", command=self.load_file).pack(padx=20, pady=4, fill="x")
        self.file_label = ctk.CTkLabel(side, text="", anchor="w", justify="left", wraplength=170)
        self.file_label.pack(padx=20, pady=(2, 16), anchor="w")

        ctk.CTkLabel(side, text="Keep your key file somewhere\nseparate from your passwords.",
                     font=ctk.CTkFont(size=11), text_color="gray", justify="left").pack(
            padx=20, side="bottom", pady=16, anchor="w")

    def _build_main(self):
        main = ctk.CTkFrame(self, fg_color="transparent")
        main.grid(row=0, column=1, sticky="nsew", padx=16, pady=(16, 0))
        main.grid_columnconfigure(0, weight=1)
        main.grid_columnconfigure(1, weight=1)
        main.grid_rowconfigure(1, weight=1)

        ctk.CTkEntry(main, textvariable=self.search_var, placeholder_text="Search sites...").grid(
            row=0, column=0, sticky="ew", padx=(0, 8), pady=(0, 8))
        self.list_frame = ctk.CTkScrollableFrame(main, label_text="Saved sites")
        self.list_frame.grid(row=1, column=0, sticky="nsew", padx=(0, 8))
        self.list_frame.grid_columnconfigure(0, weight=1)

        form = ctk.CTkFrame(main)
        form.grid(row=0, column=1, rowspan=2, sticky="nsew", padx=(8, 0))
        form.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(form, text="Site", anchor="w").grid(row=0, column=0, padx=16, pady=(16, 0), sticky="w")
        self.site_entry = ctk.CTkEntry(form, placeholder_text="e.g. example.com")
        self.site_entry.grid(row=1, column=0, padx=16, pady=(4, 12), sticky="ew")

        ctk.CTkLabel(form, text="Password", anchor="w").grid(row=2, column=0, padx=16, sticky="w")
        self.pw_entry = ctk.CTkEntry(form, show="•")
        self.pw_entry.grid(row=3, column=0, padx=16, pady=(4, 8), sticky="ew")

        row = ctk.CTkFrame(form, fg_color="transparent")
        row.grid(row=4, column=0, padx=16, sticky="ew")
        self.show_var = ctk.BooleanVar(value=False)
        ctk.CTkCheckBox(row, text="Show", variable=self.show_var, width=60,
                        command=self._toggle_show).pack(side="left")
        ctk.CTkButton(row, text="Generate", width=80, command=self.generate).pack(side="right")
        ctk.CTkButton(row, text="Copy", width=70, command=self.copy_password).pack(side="right", padx=8)

        ctk.CTkButton(form, text="Save", command=self.save_password).grid(
            row=5, column=0, padx=16, pady=(20, 6), sticky="ew")
        ctk.CTkButton(form, text="Delete", fg_color="#b3261e", hover_color="#8c1d18",
                      command=self.delete_password).grid(row=6, column=0, padx=16, pady=6, sticky="ew")
        ctk.CTkButton(form, text="Clear form", fg_color="transparent", border_width=1,
                      text_color=("gray10", "gray90"), command=self.clear_form).grid(
            row=7, column=0, padx=16, pady=6, sticky="ew")

        self.status = ctk.CTkLabel(self, text="Create or load a key to get started.", anchor="w")
        self.status.grid(row=1, column=1, sticky="ew", padx=16, pady=8)

    # ---------- helpers ----------
    def _set_status(self, msg):
        self.status.configure(text=msg)

    def _report(self, result):
        """Show a manager result; pop up a dialog for errors."""
        if result.startswith("Error"):
            self._set_status(result)
            messagebox.showerror("PasSafe", result)
            return False
        self._set_status(result)
        return True

    def _update_status_labels(self):
        self.key_label.configure(text="Key loaded ✔" if self.pm.key else "No key loaded")
        name = self.pm.password_file.replace("\\", "/").split("/")[-1] if self.pm.password_file else None
        self.file_label.configure(text=name if name else "No file loaded")

    def _refresh_list(self):
        for child in self.list_frame.winfo_children():
            child.destroy()
        query = self.search_var.get().strip().lower()
        for site in self.pm.list_sites():
            if query and query not in site.lower():
                continue
            selected = site == self.selected
            ctk.CTkButton(
                self.list_frame, text=site, anchor="w",
                fg_color=("gray75", "gray30") if selected else "transparent",
                text_color=("gray10", "gray90"),
                hover_color=("gray70", "gray28"),
                command=lambda s=site: self.select(s),
            ).grid(sticky="ew", pady=1)

    def _toggle_show(self):
        self.pw_entry.configure(show="" if self.show_var.get() else "•")

    # ---------- key / file actions ----------
    def new_key(self):
        path = filedialog.asksaveasfilename(title="Save new key as", defaultextension=".key", filetypes=KEY_TYPES)
        if path and self._report(self.pm.create_key(path)):
            self._update_status_labels()

    def load_key(self):
        path = filedialog.askopenfilename(title="Open key file", filetypes=KEY_TYPES)
        if path and self._report(self.pm.load_key(path)):
            self._update_status_labels()

    def new_file(self):
        path = filedialog.asksaveasfilename(title="Create password file", defaultextension=".pw", filetypes=PW_TYPES)
        if path and self._report(self.pm.create_password_file(path)):
            self.selected = None
            self.clear_form()
            self._update_status_labels()
            self._refresh_list()

    def load_file(self):
        path = filedialog.askopenfilename(title="Open password file", filetypes=PW_TYPES)
        if path and self._report(self.pm.load_password_file(path)):
            self.selected = None
            self.clear_form()
            self._update_status_labels()
            self._refresh_list()

    # ---------- password actions ----------
    def select(self, site):
        self.selected = site
        self.site_entry.delete(0, "end")
        self.site_entry.insert(0, site)
        self.pw_entry.delete(0, "end")
        self.pw_entry.insert(0, self.pm.get_password(site) or "")
        self._refresh_list()

    def clear_form(self):
        self.selected = None
        self.site_entry.delete(0, "end")
        self.pw_entry.delete(0, "end")
        self._refresh_list()

    def save_password(self):
        site = self.site_entry.get().strip()
        pw = self.pw_entry.get()
        if not pw:
            self._report("Error: Password cannot be empty.")
            return
        if self._report(self.pm.add_password(site, pw)):
            self.selected = site
            self._refresh_list()

    def delete_password(self):
        site = self.site_entry.get().strip()
        if site not in self.pm.password_dict:
            self._report("Error: Select a saved site to delete.")
            return
        if messagebox.askyesno("PasSafe", f"Delete the password for '{site}'?"):
            if self._report(self.pm.delete_password(site)):
                self.clear_form()

    def copy_password(self):
        pw = self.pw_entry.get()
        if not pw:
            self._set_status("Nothing to copy.")
            return
        self.clipboard_clear()
        self.clipboard_append(pw)
        self._set_status("Copied. Clipboard clears in 30 seconds.")

        def clear_if_unchanged():
            try:
                if self.clipboard_get() == pw:
                    self.clipboard_clear()
            except Exception:
                pass
        self.after(CLIPBOARD_CLEAR_MS, clear_if_unchanged)

    def generate(self):
        alphabet = string.ascii_letters + string.digits + "!@#$%^&*-_"
        pw = "".join(secrets.choice(alphabet) for _ in range(20))
        self.pw_entry.delete(0, "end")
        self.pw_entry.insert(0, pw)
        self.show_var.set(True)
        self._toggle_show()


if __name__ == "__main__":
    App().mainloop()
