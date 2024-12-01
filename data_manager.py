import json
import os
from cryptography import fernet
import bcrypt
from PasswordGenerator import PasswordGenerator
from random import randint
from tkinter import messagebox


class DataManager:
    def __init__(self, username:str, password:str, email:str = None):
        self.username = username
        self.password = password
        self.email = email
        self.path = './data/'+self.username+'/'
        self.data_file_path = './data/'+self.username+'/'+self.username+'.json'

    def check_account(self):
        if not os.path.exists(self.path):
            return False
        if not os.path.exists(self.path+self.username+'.json'):
            return False
        else:
            return True

    def load_account(self):
        if self.check_account():
            fer_key = fernet.Fernet(open(self.path+'key.key', 'rb').read())
            with open(self.data_file_path, 'r') as file:
                account = json.load(file)
            master_credentials = account["accounts"][0]
            password = master_credentials["password"].encode()

            if(bcrypt.checkpw(self.password.encode(), password)):
                return True
            else:
                return False
        else:
            print("Account does not exist")
            return False

    def create_master_account(self):
        # Generate path 
        if not os.path.exists(self.path):
            os.mkdir(self.path)
        else:
            return 0
        
        #Generate and save key
        key = fernet.Fernet.generate_key();
        with open(self.path+'key.key', 'wb') as key_file:
            key_file.write(key)
        
        # Encrypt credentials 
        fer = fernet.Fernet(key)
        salt = bcrypt.gensalt()

        encrypted_password: bytes = bcrypt.hashpw(password=self.password.encode(), salt=salt)
        encrypted_username: bytes = fer.encrypt(self.username.encode());
        encrypted_email: bytes = fer.encrypt(self.email.encode())
        # Save credentials
        data = {
            "accounts": [
                {
                    "email": encrypted_email.decode(),
                    "username": encrypted_username.decode(),
                    "password": encrypted_password.decode(),
                }
            ]
        }

        with open(self.path+self.username+'.json', 'w') as file:
            json.dump(data, file, indent=4)

    def change_master_password(self, password:str, data):
        salt = bcrypt.gensalt()
        new_password = bcrypt.hashpw(password.encode(), salt)
        data["accounts"][0]["password"] = new_password.decode()
        
        self.save_new_data(data=data)

    def load_data(self):
        if not os.path.exists(self.data_file_path):
            messagebox.showerror("CRITICAL ERROR", "Failed to locate data.")
        else:
            with open(self.data_file_path, 'r') as file:
                data = json.load(file)
        return data
    
    def save_data(self, data):
        current_data = self.load_data()
        data = self.encrypt_data_basic(data)
        current_data["accounts"].append(data)

        with open(self.data_file_path, 'w') as file:
            json.dump(current_data, file, indent=4)
    
    def save_new_data(self, data):
        new_data = self.encrypt_data(data)
        with open(self.data_file_path, 'w') as file:
            json.dump(new_data, file, indent=4)
    
    def encrypt_data(self, data):
        # Directory is the username
        self.fer_key = fernet.Fernet(open('./data/'+self.username+'/key.key', 'rb').read())
        
        for item in data["accounts"]:
            if "email" in item:
                item["email/number"] = self.fer_key.encrypt(item["email"].encode()).decode()
                item["username"] = self.fer_key.encrypt(item["username"].encode()).decode()

            if "service" in item:
                item["service"] = self.fer_key.encrypt(item["service"].encode()).decode()
                item["domain"] = self.fer_key.encrypt(item["domain"].encode()).decode()
                item["username"] = self.fer_key.encrypt(item["username"].encode()).decode()
                item["password"] = self.fer_key.encrypt(item["password"].encode()).decode()
                item["code"] = self.fer_key.encrypt(item["code"].encode()).decode()
        return data;

    def encrypt_data_basic(self, data):
        data["service"] = self.fer_key.encrypt(data["service"].encode()).decode()
        data["domain"] = self.fer_key.encrypt(data["domain"].encode()).decode()
        data["username"] = self.fer_key.encrypt(data["username"].encode()).decode()
        data["password"] = self.fer_key.encrypt(data["password"].encode()).decode()
        data["code"] = self.fer_key.encrypt(data["code"].encode()).decode()
        return data;

    def decrypt_data(self, data):
        # Directory is the username
        self.fer_key = fernet.Fernet(open('./data/' + self.username + '/key.key', 'rb').read())
        for item in data["accounts"]:
            if "service" in item:
                item["service"] = self.fer_key.decrypt(item["service"].encode()).decode()
            if "domain" in item:
                item["domain"] = self.fer_key.decrypt(item["domain"].encode()).decode()
            if "username" in item:
                item["username"] = self.fer_key.decrypt(item["username"].encode()).decode()
            if "password" in item:
                try:
                    item["password"] = self.fer_key.decrypt(item["password"].encode()).decode()
                except:
                    pass
            if "code" in item:
                item["code"] = self.fer_key.decrypt(item["code"].encode()).decode()
        return data

def generatePassword():
    password_generator = PasswordGenerator()
    password_generator.minlen = 10
    password_generator.maxlen = 16
    password_generator.minnumbers = 2
    password_generator.minschars = 1
    password_generator.minuchars = 2
    password = password_generator.generate()
    return password

def generateCode():
    code = ""
    for i in range(0, 5):
        code += str(randint(0, 9))
    return code

def generateCuratedPassword(min_len:int, max_len:int, min_special_chars:int, min_uppercase, min_nums )->str:
    password_generator = PasswordGenerator()
    password_generator.minlen = min_len
    password_generator.maxlen = max_len
    password_generator.minnumbers = min_nums
    password_generator.minschars = min_special_chars
    password_generator.minuchars = min_uppercase
    password = password_generator.generate()
    return password

def generateCuratedCode(code_len, excl_nums:list = [])-> str:
    nums = []
    excl_nums.sort()
    for i in range(0,10):
        nums.append(i)
    
    if nums == excl_nums:
        return ""
    
    code = ""
    for i in range(0, code_len):
        num = randint(0,9)
        while num in excl_nums:
            num = randint(0,9)
        code += str(num)
    return code


def test():
    manager = DataManager("Nkulleko", "123UyahlanyA2");
    manager.create_master_account()

    data = {
        "service": "Google Email",
        "domain": "www.gooole.gmail.com",
        "username": "nkulleko",
        "password": "123UyahlanyA2",
        "code": "45638" ,
        "note": "This are the credentials for my google email account"
    }

    manager.save_data(data);
    print(manager.decrypt_data(manager.load_data()))