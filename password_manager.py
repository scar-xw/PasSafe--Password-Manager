import os

from cryptography.fernet import Fernet, InvalidToken


class PasswordManager:
    """Handles key management and encrypted password storage (no UI code)."""

    def __init__(self):
        self.key = None
        self.password_file = None
        self.password_dict = {}

    # ---------- key handling ----------
    def create_key(self, path):
        key = Fernet.generate_key()
        try:
            with open(path, "wb") as f:
                f.write(key)
        except OSError as e:
            return f"Error: could not write key file ({e})."
        self.key = key
        return "Key created and loaded successfully!"

    def load_key(self, path):
        if not os.path.exists(path):
            return "Error: Key file not found."
        try:
            with open(path, "rb") as f:
                key = f.read().strip()
            Fernet(key)  # validate the key format
        except (ValueError, OSError):
            return "Error: That file is not a valid key file."
        self.key = key
        return "Key loaded successfully!"

    # ---------- password file handling ----------
    def create_password_file(self, path):
        if not self.key:
            return "Error: Create or load a key first."
        if os.path.exists(path):
            return "Error: File already exists (use option 4 to load it)."
        self.password_file = path
        self.password_dict = {}
        return self._save()

    def load_password_file(self, path):
        if not self.key:
            return "Error: Create or load a key first."
        if not os.path.exists(path):
            return "Error: Password file not found."
        fernet = Fernet(self.key)
        loaded = {}
        try:
            with open(path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if ":" not in line:
                        continue
                    # Fernet tokens never contain ":", so split from the right
                    site, encrypted = line.rsplit(":", 1)
                    loaded[site] = fernet.decrypt(encrypted.encode()).decode()
        except InvalidToken:
            return "Error: This key does not match the password file!"
        except OSError as e:
            return f"Error loading file: {e}"
        self.password_file = path
        self.password_dict = loaded
        return "Passwords loaded successfully!"

    def _save(self):
        """Rewrite the whole password file (avoids duplicate entries)."""
        fernet = Fernet(self.key)
        try:
            with open(self.password_file, "w", encoding="utf-8") as f:
                for site, pw in self.password_dict.items():
                    token = fernet.encrypt(pw.encode()).decode()
                    f.write(f"{site}:{token}\n")
        except OSError as e:
            return f"Error saving file: {e}"
        return "Password file saved successfully!"

    # ---------- passwords ----------
    def add_password(self, site, password):
        if not self.key:
            return "Error: Create or load a key first."
        if not self.password_file:
            return "Error: Create or load a password file first."
        if not site:
            return "Error: Site name cannot be empty."
        self.password_dict[site] = password
        result = self._save()
        if result.startswith("Error"):
            return result
        return f"Password for '{site}' saved!"

    def get_password(self, site):
        return self.password_dict.get(site)

    def delete_password(self, site):
        if site not in self.password_dict:
            return "Error: Site not found."
        del self.password_dict[site]
        result = self._save()
        if result.startswith("Error"):
            return result
        return f"Password for '{site}' deleted."

    def list_sites(self):
        return sorted(self.password_dict)
