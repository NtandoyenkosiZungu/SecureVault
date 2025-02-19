import hashlib
import requests
from tkinter import messagebox

def check_password(password):
    sha1_password = hashlib.sha1(password.encode('utf-8')).hexdigest().upper()
    prefix = sha1_password[:5]
    suffix = sha1_password[5:]
    try:
        response = requests.get(f'https://api.pwnedpasswords.com/range/{prefix}')
        response.raise_for_status()
        if response.status_code == 200:
            if suffix in response.text:
                return True
            return False
        else:
            messagebox.showerror("CONNECTION ERROR", "Failed to connect to provider.")
            return False
    except:
        return False