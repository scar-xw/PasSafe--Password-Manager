from cryptography.fernet import Fernet
import cryptography

class PasswordManager:
    # Key storage and creation
    def __init__ (self):
       self.key = None
       self.password = None
       self.password_dict = {} 
    
    def create_key(self, path):
        self.key = Fernet.generate_key()
        with open(path, 'wb') as f:
            f.write(self.key)

    def load_key(self, path):
        with open(path, 'rb') as f:
            self.key = f.read()

    # Password creation and storage

    
    def create_password_file(self, path, initial_values=None):
        self.password_file = path

        if initial_values is not None:
            for key, values in initial_values.items():# the .items() method can iterate between tuples
                    self.add_password(key, values)
            else:
                with open(path, 'w') as f:
                    pass
            
    def load_password_file(self, path):
        try:
            with open(path, 'r') as f:
                for line in f:
                    site, encrypted = line.split(":")
                    self.password_dict[site]  = Fernet(self.key).decrypt(encrypted.encode()).decode()
                    error = "Success! Password loaded/created with key"

        except cryptography.fernet.InvalidToken:
            self.password_dict = {} 
            error ="\nERROR: USER KEY DOES NOT MATCH PASSWORD FILE KEY, ENTER ANOTHER KEY OR FILE\n"
        return error

    def add_password(self, site, password):
        self.password_dict[site] = password

        if self.password_file is not None:
            # a+ reads and appends 
            with open(self.password_file, 'a+') as f:
                # encrypted = the new password for the site
                encrypted = Fernet(self.key).encrypt(password.encode())
                f.write(site + ":" + encrypted.decode() + "\n")
    
    def get_password(self, site):
        return self.password_dict[site]
    

        
    
       
