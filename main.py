import customtkinter as ctk;
from  tkinter import messagebox, IntVar
from data_manager import DataManager, generatePassword, generateCuratedPassword, generateCode
from breach_test import check_password
from functools import partial
from sys import platform
import re
import math
import os




ctk.set_appearance_mode("System");
ctk.set_default_color_theme("blue");
custom_font = ("Helvetica", 16, "bold")

def show_password(entrybox: ctk.CTkEntry):
    if entrybox.cget("show") == "•":
        entrybox.configure(show="")
    else:
        entrybox.configure(show="•")

class MainWindow:
    def __init__(self, root, datamanager: DataManager, username): 
        self.root = root
        #self.root.iconbitmap('./assets/tex.ico')
        self.datamanager = datamanager
        self.refresh_data()

        self.main_window = ctk.CTkToplevel(self.root)
        self.main_window.geometry("850x700")
        self.main_window.title("VaulTex - Password Manager")
        self.main_window.wm_iconbitmap('./assets/tex.ico')
        self.main_window.resizable(False, False)

        #Setting Focus
        self.main_window.focus()
        self.main_window.lift()
        self.main_window.grab_set()

        # Window Closing Protocol
        self.main_window.protocol("WM_DELETE_WINDOW", self.on_closing)

        self.username_label = ctk.CTkLabel(self.main_window, width=200, text=username, font=custom_font)
        self.username_label.place(x=-50, y=10)

        self.refresh_button = ctk.CTkButton(self.main_window, width=100, height=20, text="Refresh", command=self.load_data, font=custom_font)
        self.refresh_button.place(x=10, y=40) 

        self.add_password_button = ctk.CTkButton(self.main_window, width=150, height=20, text="Add New Password", command=self.add_new_password, font=custom_font)
        self.add_password_button.place(x=150, y=40)

        self.breach_button = ctk.CTkButton(self.main_window, width=150, height=20, text="Check Breaches", command=self.on_breach_button_click, font=custom_font)
        self.breach_button.place(x=340, y=40)

        self.change_password_button = ctk.CTkButton(self.main_window, width=200, height=20, text="Change Master Password", command=self.change_password, font=custom_font)
        self.change_password_button.place(x=540, y=40)
        #Frames - and components related to the frames
        self.left_side_frame = Frame(self.main_window, x=10, y=80, width=300, height=540)
        self.right_side_frame = Frame(self.main_window, x=320, y=80, width=510, height=540, placed=False)
        """
        components related to the right side frames
        """
        self.service_label = ctk.CTkLabel(self.right_side_frame.frame, text="Service", font=custom_font)
        self.service_entry = ctk.CTkEntry(self.right_side_frame.frame, width=310, font=custom_font)

        self.domain_label = ctk.CTkLabel(self.right_side_frame.frame, text="Domain", font=custom_font)
        self.domain_entry = ctk.CTkEntry(self.right_side_frame.frame, width=310, font=custom_font)

        self.username_label = ctk.CTkLabel(self.right_side_frame.frame, text="Username", font=custom_font)
        self.username_entry = ctk.CTkEntry(self.right_side_frame.frame, width=310, font=custom_font)

        self.password_label = ctk.CTkLabel(self.right_side_frame.frame, text="Password", font=custom_font)
        self.password_show_button = ctk.CTkButton(self.right_side_frame.frame, width=30, height=20, text="show", command=self._show_pass, font=custom_font)
        self.password_entry = ctk.CTkEntry(self.right_side_frame.frame, width=310, show="•", font=custom_font)

        self.code_label = ctk.CTkLabel(self.right_side_frame.frame, text="Code", font=custom_font)
        self.code_entry = ctk.CTkEntry(self.right_side_frame.frame, width=310, show="•", font=custom_font)
        self.show_code_button = ctk.CTkButton(self.right_side_frame.frame, width=30, text="show", command=self._show_code, font=custom_font)

        self.edit_button = ctk.CTkButton(self.right_side_frame.frame, width=200, text="Edit", command=self.on_edit_button_click, font=custom_font)
        self.close_button = ctk.CTkButton(self.right_side_frame.frame, width=200, text="Close", command=self.on_close_button_click, font=custom_font)
        self.edit_button.place(x=150, y=430)
        self.close_button.place(x=150, y=480)

        self.service_label.place(x=10, y=20)
        self.service_entry.place(x=100, y=20)

        self.domain_label.place(x=10, y=60)
        self.domain_entry.place(x=100, y=60)

        self.username_label.place(x=10, y=100)
        self.username_entry.place(x=100, y=100)

        self.password_label.place(x=10, y=140)
        self.password_entry.place(x=100, y=140)
        self.password_show_button.place(x=430, y=140)

        self.code_label.place(x=10, y=180)
        self.code_entry.place(x=100, y=180)
        self.show_code_button.place(x=430, y=180)

        #Borrowed this one from GitHub 😂😂
        if platform.startswith("win"):
            self.main_window.after(200, lambda: self.main_window.iconbitmap("assets/tex.ico"))

        """FRAME NAVIGATION"""
        self.__dict__["index"] = 1
        self.next_button= ctk.CTkButton(self.main_window, height=30, text=">>", font=custom_font, state="disabled", command=self.next)
        self.prev_button= ctk.CTkButton(self.main_window, height=30,text="<<", font=custom_font, state="disabled", command=self.previous)
        self.next_button.place(x=170, y=640)
        self.prev_button.place(x=10, y=640)

        #CHECK FOR BREACHES
        self.test_for_breaches()

        self.load_data()

    def add_new_password(self):
        self.addPassword = AddPassword(self.main_window, self.datamanager, self.load_data)

    def on_breach_button_click(self):
        messagebox.showinfo("CHECKING", "Checking for any exposed passwords, please wait")
        self.breachCheck = BreachCheck(self.main_window, self.datamanager, self.load_data, self.main_window)
        self.main_window.withdraw()

    def _show_pass(self):
        show_password(self.password_entry)

    def _show_code(self):
        show_password(self.code_entry)

    def load_data(self):
        self.refresh_data()
        widgets = self.left_side_frame.frame.winfo_children()
        for widget in widgets:
            widget.destroy()

        self.place_data(0,10)
        self.test_for_breaches()
    
    def refresh_data(self):
        self.data = self.datamanager.load_data()
        self.data = self.datamanager.decrypt_data(self.data)

    def test_for_breaches(self):
        for i in range(1, len(self.data["accounts"])):
            if check_password(self.data["accounts"][i]["password"]):
                self.breach_button.configure(fg_color = "red")
                break
            else:
                self.breach_button.configure(fg_color = "green")

    def next(self):
        widgets = self.left_side_frame.frame.winfo_children()

        for widget in widgets:
            widget.destroy()
        
        index = self.__dict__["index"]
        self.place_data(start=index, end=index+9)
        self.prev_button.configure(state="normal")

    def previous(self):
        widgets = self.left_side_frame.frame.winfo_children()
        for widget in widgets:
            widget.destroy()

        self.__dict__["index"] -= 8
        if (self.__dict__["index"] < 0):
            self.__dict__["index"] = 0
        index = self.__dict__["index"]

        self.place_data(start=index, end=index+9)
        self.next_button.configure(state="normal")

    def place_data(self, start: int = 0, end: int = 9):
        length =len(self.data["accounts"])

        if (length > start+8):
            self.next_button.configure(state = "normal")
            self.__dict__["index"] = end
        else:
            self.next_button.configure(state= "disabled")
        
        j = 10
        for i in range(start, end):
            try:
                if self.data["accounts"][i]["service"] :
                    button = ctk.CTkButton(self.left_side_frame.frame, width=290, height=50, command=partial(self.display_password_details, i), text=self.data["accounts"][i]["service"], font=custom_font)
                    button.__dict__["i"] = i
                    button.place(x=5, y=j)
                    j +=60
            except IndexError:
                break
            except KeyError:
                pass

    def display_password_details(self, i):
        self.service_entry.delete(0, "end")
        self.domain_entry.delete(0, "end")
        self.username_entry.delete(0, "end")
        self.password_entry.delete(0, "end")
        self.code_entry.delete(0, "end")

        self.service_entry.insert(0, self.data["accounts"][i]["service"])
        self.domain_entry.insert(0, self.data["accounts"][i]["domain"])
        self.username_entry.insert(0, self.data["accounts"][i]["username"])
        self.password_entry.insert(0, self.data["accounts"][i]["password"])
        self.code_entry.insert(0, self.data["accounts"][i]["code"])

        self.edit_button.__dict__["current_index"] = i
        self.right_side_frame.show()

    def on_edit_button_click(self):
        username = self.username_entry.get()
        self.editPassword = EditPassword(self.main_window, self.data, self.edit_button.__dict__["current_index"], username, self.datamanager, self.load_data)
        self.right_side_frame.hide()

    def change_password(self):
       change_password = ChangePassword(self.root, self.data, self.datamanager, self.load_data)

    def on_close_button_click(self):
        self.right_side_frame.hide()
        self.load_data()

    def on_closing(self):
        self.root.quit()
        self.root.destroy()
    
class LogIn:
    def __init__(self,root):

        self.root = root
        self.root.iconbitmap('./assets/tex.ico')
        self.root.title("VaulTex - Log In")
        self.root.geometry("400x280")
        self.root.resizable(False, False)
        

        #Master Password Field
        self.username_label = ctk.CTkLabel(self.root, width=50, text="Username", font=custom_font)
        self.username_entry= ctk.CTkEntry(self.root, width=300, font=custom_font)
        self.master_password_label = ctk.CTkLabel(self.root, width=50, text="Password", font=custom_font)
        self.master_password_entry = ctk.CTkEntry(self.root, width=300, show="•", font=custom_font)
        self.show_password_button = ctk.CTkButton(self.root, width=30, height=10, text="show", command=self._show_pass, font=custom_font)
        self.login_button = ctk.CTkButton(self.root, width=200, text="Log In", command=self.on_login_button_click, font=custom_font)
        self.sign_up_button = ctk.CTkButton(self.root, width=200, text="Sign Up",command=self.on_create_account_button_click,  font=custom_font);

        #Object Placement
        self.username_label.place(x=50, y=50);
        self.username_entry.place(x=50, y=80);
        self.master_password_label.place(x=50, y=120);
        self.master_password_entry.place(x=50, y=150);
        self.login_button.place(x=100, y=190)
        self.sign_up_button.place(x=100, y=235)
        self.show_password_button.place(x=140, y=120)
    
    def _show_pass(self):
        show_password(self.master_password_entry)

    def on_login_button_click(self):
        username = self.username_entry.get()
        password = self.master_password_entry.get()

        if username == '':
           messagebox.showwarning("INVALID INPUT", "Please fill in the username field")
           self.username_entry.focus()
           return None
        elif password == '':
            messagebox.showwarning("INVALID INPUT", "Please fill in the password field")
            return None
            
        data_manager = DataManager(username=username, password=password)
        if data_manager.check_account() and data_manager.load_account():
            self.openMainWindow(datamanager=data_manager, username=username)
        else:
            messagebox.showwarning("Log In Failed", "Account Not Found, Please try again.")
    
    def on_create_account_button_click(self):
        self.sign_up_window = CreateAccount(self.root)

    def openMainWindow(self, datamanager: DataManager, username):
        self.main_window = MainWindow(self.root, datamanager, username )
        self.root.withdraw()

class Frame:
    def __init__(self, root, x, y, width, height, placed: bool = True):
       #Children will be ctk components that will be placed on the frame
       self.frame = ctk.CTkFrame(root, width, height)
       self.x = x
       self.y = y
       
       if placed:
        self.show()

    def hide(self):
        self.frame.place_forget()
    
    def show(self):
        self.frame.place(x=self.x, y=self.y)

class AddPassword:
    def __init__(self,root, datamanager: DataManager, func = None):
        self.root = root
        self.root.iconbitmap('./assets/tex.ico')
        self.add_password = ctk.CTkToplevel(self.root)
        self.datamanager = datamanager
        self.func = func
        self.add_password.title("VaulTex - Add New Password")
        self.add_password.geometry("500x600")
        self.add_password.resizable(False, False)

        #Setting Focus
        self.add_password.focus()
        self.add_password.lift()
        self.add_password.grab_set()

        #Creating the components for adding a new password record
        self.service_label = ctk.CTkLabel(self.add_password, text="Service", font=custom_font)
        self.service_entry = ctk.CTkEntry(self.add_password, width=300, font=custom_font)

        self.domain_label = ctk.CTkLabel(self.add_password, text="Domain", font=custom_font)
        self.domain_entry = ctk.CTkEntry(self.add_password, width=300, font=custom_font)

        self.username_label = ctk.CTkLabel(self.add_password, text="Username", font=custom_font)
        self.username_entry = ctk.CTkEntry(self.add_password, width=300, font=custom_font)

        self.password_label = ctk.CTkLabel(self.add_password, text="Password", font=custom_font)
        self.password_entry = ctk.CTkEntry(self.add_password, width=300, font=custom_font)
        self.password_show_button = ctk.CTkButton(self.add_password, width=30, text="generate", command=self.on_generate_password_button_click, font=custom_font)

        self.code_label = ctk.CTkLabel(self.add_password, text="code", font=custom_font)
        self.code_entry = ctk.CTkEntry(self.add_password, width=300, font=custom_font)
        self.code_show_button = ctk.CTkButton(self.add_password, width=30, text="generate", command=self.on_generate_code_button_click, font=custom_font)

        self.add_button = ctk.CTkButton(self.add_password, text="Add", command=self.on_add_button_click, font=custom_font)
        self.cancel_button = ctk.CTkButton(self.add_password, text="Cancel", command=self.on_cancel_button_click, font=custom_font)

        #Placing The Components
        self.service_label.place(x=10, y=20)
        self.service_entry.place(x=100, y=20)

        self.domain_label.place(x=10, y=60)
        self.domain_entry.place(x=100, y=60)

        self.username_label.place(x=10, y=100)
        self.username_entry.place(x=100, y=100)

        self.password_label.place(x=10, y=140)
        self.password_entry.place(x=100, y=140)
        self.password_show_button.place(x=400, y=140)

        self.code_label.place(x=10, y=180)
        self.code_entry.place(x=100, y=180)
        self.code_show_button.place(x=400, y=180)

        self.add_button.place(x=90, y=560)
        self.cancel_button.place(x=280, y=560)

        if platform.startswith("win"):
            self.add_password.after(200, lambda: self.add_password.iconbitmap("assets/tex.ico"))

    def _show_pass(self):
        show_password(self.password_entry)
    
    def on_generate_password_button_click(self):
        #generate a password and insert it into the password entry
        password = generatePassword()
        self.password_entry.delete(0, "end")
        self.password_entry.insert(0, password)
    
    def on_generate_code_button_click(self):
        #generate a code and insert it into the code entry
        code = generateCode()
        self.code_entry.delete(0, "end")
        self.code_entry.insert(0, code)

    def _show_code(self):
        show_password(self.code_entry)
    
    def on_add_button_click(self):
        #add password to datamanager
        """
        First we start by validating user input
        """
        if self.code_entry.get() == '' and self.password_entry.get() == '':
            messagebox.showwarning("Password/Code Missing","Password or Code must be provided")
            return
        if self.username_entry.get() == '':
            messagebox.showwarning("Username Missing","Username cannot be blank")
            return
        if self.service_entry.get() == '':
            messagebox.showwarning("Service Missing","Service cannot be blank")
            return
        if self.domain_entry.get() == '':
            self.domain_entry.insert(0, "No Domain Available")
        
        
        """
        Then we add the new password to the data manager
        """
        data = {
            "service": self.service_entry.get(),
            "domain": self.domain_entry.get(),
            "username": self.username_entry.get(),
            "password": self.password_entry.get(),
            "code": self.code_entry.get()
        }

        self.datamanager.save_data(data)
        messagebox.showinfo("Password Added","New Password has been added to your vault")
        self.add_password.destroy()
        self.func()
        
 
    def on_cancel_button_click(self):
         self.add_password.destroy()   

class CreateAccount:
    def __init__(self, root):
        self.root = root
        self.root.iconbitmap('./assets/tex.ico')
        self.create_account = ctk.CTkToplevel(self.root)
        self.create_account.title("VaulTex - Create New Account")
        self.create_account.geometry("400x600")
        self.create_account.resizable(False, False)

        #Setting Focus
        self.create_account.focus()
        self.create_account.lift()
        self.create_account.grab_set()

        #Components for creating a new account
        self.email_label = ctk.CTkComboBox(self.create_account, values=["Email", "Number"], font=custom_font)
        self.email_entry = ctk.CTkEntry(self.create_account, width=300, font=custom_font)
        
        self.username_label = ctk.CTkLabel(self.create_account, text="Username", font=custom_font)
        self.username_entry = ctk.CTkEntry(self.create_account, width=300, font=custom_font)

        self.password_label = ctk.CTkLabel(self.create_account, text="Password", font=custom_font)
        self.password_entry = ctk.CTkEntry(self.create_account, width=300,show="•", font=custom_font)
        self.show_password_button = ctk.CTkButton(self.create_account, width=30, height=20, text="show", command=self._show_pass, font=custom_font)

        self.confirm_password_label = ctk.CTkLabel(self.create_account, text="Confirm Password", font=custom_font)
        self.confirm_password_entry = ctk.CTkEntry(self.create_account, width=300, show="•", font=custom_font)
        self.confirm_show_password_button = ctk.CTkButton(self.create_account, width=30, height=20, text="show", command=self._show_confirm_pass, font=custom_font)

        self.create_account_button = ctk.CTkButton(self.create_account, width=70, height=40, text="Create Account", command=self.on_create_account_button_click, font=custom_font)
        self.cancel_button = ctk.CTkButton(self.create_account, width=60, height=40, text="Cancel", command=self.on_cancel_button_click, font=custom_font)

        self.email_label.place(x=10, y=20)
        self.email_entry.place(x=10, y=50)

        self.username_label.place(x=10, y=90)
        self.username_entry.place(x=10, y=120)

        self.password_label.place(x=10, y=150)
        self.password_entry.place(x=10, y=180)
        self.show_password_button.place(x=320, y=180)

        self.confirm_password_label.place(x=10, y=210)
        self.confirm_password_entry.place(x=10, y=240)
        self.confirm_show_password_button.place(x=320, y=240)

        self.create_account_button.place(x=110, y=300)
        self.cancel_button.place(x=145, y=370)

        if platform.startswith("win"):
            self.create_account.after(200, lambda: self.create_account.iconbitmap("assets/tex.ico"))
    def _show_pass(self):
        show_password(self.password_entry)
    
    def _show_confirm_pass(self):
        show_password(self.confirm_password_entry)
    
    def on_cancel_button_click(self):
        self.create_account.destroy()
    
    def is_valid_email(self, email):
        pattern = r'^[\w\.-]+@[a-zA-Z\d\.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    def on_create_account_button_click(self):
        #Creating The User Account
        """
        First We Start Off By Validating User Input
        """
        if self.email_entry.get() == '':
            messagebox.showwarning("Email/Number Missing","Email cannot be blank")
            return 0;
          
        if self.username_entry.get() == '':
            messagebox.showwarning("Username Missing","Username cannot be blank")
            return 0;
        elif len(self.username_entry.get()) < 5:
            messagebox.showwarning("Username Invalid","Username must be at least 5 characters long")
            return 0;
        
        if self.password_entry.get() == '' or self.confirm_password_entry.get() == '':
            messagebox.showwarning("Password Missing","Password must be provided")
            return 0;
        if self.password_entry.get()!= self.confirm_password_entry.get():
            messagebox.showwarning("Password Mismatch","Passwords do not match")
            return 0;
        
        """
        Then We Create The User Account
        """
        email:str = self.email_entry.get()
        if self.email_label.get() == "Email":
            if not self.is_valid_email(email):
                messagebox.showwarning("Invalid Email", "Your email is invalid, please enter a valid email address")
                return 0;
        
        if self.email_label.get() == "Number":
            if not (email.isdigit() and  len(email) == 10):
                messagebox.showwarning("Invalid Cell Number", "Your cell number is invalid, please enter a valid cell number")
                return 0;


        if (messagebox.askyesno("NOTICE", "Make sure to not FORGET your Master Password \n\n YOUR PASSWORD CANNOT BE RETRIEVED IF LOST \n\n Do you wish to CONTINUE?")):

            username:str = self.username_entry.get()
            password:str = self.password_entry.get()
            datamanager:DataManager = DataManager(username, password, email)
            datamanager.create_master_account()
            self.create_account.destroy()
            messagebox.showinfo("Account Created","Your account has been created successfully. \n You can now Log In to your account.")
        else:
            return 0;

class EditPassword:
    def __init__(self, root, data,current_index,username ,datamanager: DataManager, func: None):
        self.root = root
        self.root.iconbitmap('./assets/tex.ico')
        self.data = data
        self.datamanager = datamanager
        self.current_index = current_index
        self.func = func
        self.edit_password = ctk.CTkToplevel(self.root)
        self.edit_password.title("VaulTex - Edit Password")
        self.edit_password.geometry("400x400")
        self.edit_password.resizable(False, False)

        #Setting Focus
        self.edit_password.focus()
        self.edit_password.lift()
        self.edit_password.grab_set()

        #Components for editing a password
        self.username_label = ctk.CTkLabel(self.edit_password, text="Username", font=custom_font)
        self.username_entry = ctk.CTkEntry(self.edit_password, width=300, font=custom_font)
        self.username_entry.insert(0, username)

        self.password_label = ctk.CTkLabel(self.edit_password, text="Password", font=custom_font)
        self.password_entry = ctk.CTkEntry(self.edit_password, width=300, show="•", font=custom_font)
        self.show_password_button = ctk.CTkButton(self.edit_password, width=30, height=20, text="show", command=self._show_pass, font=custom_font)
        self.generate_password_button = ctk.CTkButton(self.edit_password, width=70, height=20, text="generate", command=self.on_generate_password_button_click, font=custom_font)

        self.code_label = ctk.CTkLabel(self.edit_password, text="Code", font=custom_font)
        self.code_entry = ctk.CTkEntry(self.edit_password, width=300, show="•", font=custom_font)
        self.code_show_button = ctk.CTkButton(self.edit_password, width=30, height=20, text="show", command=self._show_code, font=custom_font)
        self.generate_code_button = ctk.CTkButton(self.edit_password, width=70, height=20, text="generate", command=self.on_generate_code_button_click, font=custom_font)

        self.save_button = ctk.CTkButton(self.edit_password, width=200, height=30, text="Save", command=self.on_save_button_click, font=custom_font)
        self.delete_record_button = ctk.CTkButton(self.edit_password, width=200, height=30, text="Delete Record", command=self.on_delete_record_button_click, font=custom_font)
        self.delete_record_button.configure(fg_color = "red")
        self.cancel_button = ctk.CTkButton(self.edit_password, width=200, height=30, text="Cancel", command=self.on_cancel_button_click, font=custom_font)

        self.username_label.place(x=10, y=20)
        self.username_entry.place(x=10, y=50)

        self.password_label.place(x=10, y=90)
        self.password_entry.place(x=10, y=120)
        self.generate_password_button.place(x=100, y=90)
        self.show_password_button.place(x=320, y=120)

        self.code_label.place(x=10, y=160)
        self.code_entry.place(x=10, y=190)
        self.generate_code_button.place(x=100, y=160)
        self.code_show_button.place(x=320, y=190)

        self.save_button.place(x=100, y=250)
        self.cancel_button.place(x=100, y=300)
        self.delete_record_button.place(x=100, y=350)

        if platform.startswith("win"):
            self.edit_password.after(200, lambda: self.edit_password.iconbitmap("assets/tex.ico"))

    def _show_pass(self):
        show_password(self.password_entry)

    def _show_code(self):
        #generate a code and insert it into the code entry
        show_password(self.code_entry)

    def on_generate_password_button_click(self):
        #generate a password and insert it into the password entry
        self.password_entry.delete(0, ctk.END)
        passwordGeneratorWindow = PasswordGenerationWindow(self.edit_password, self.password_entry);
    
    def on_generate_code_button_click(self):
        #generate a code and insert it into the code entry
        code = generateCode()
        self.code_entry.delete(0, ctk.END)
        self.code_entry.insert(0, code)

    def on_save_button_click(self):
        #update the password in the database
        password = self.password_entry.get()
        username = self.username_entry.get()
        code =self.code_entry.get()

        self.data["accounts"][self.current_index]["username"] = username
        self.data["accounts"][self.current_index]["password"] = password
        self.data["accounts"][self.current_index]["code"] = code
        self.edit_password.destroy()
        self.datamanager.save_new_data(self.data)
        messagebox.showinfo("Password Updated","Your password has been updated successfully, please refresh to see changes.")
        self.func()

    def on_delete_record_button_click(self):
        #delete the record from the database
        if messagebox.askyesno("DELETE RECORD", "Are you sure you want to delete"):
            del self.data["accounts"][self.current_index]
            self.datamanager.save_new_data(self.data)
            self.edit_password.destroy()
            self.func()
            messagebox.showinfo("Record Deleted","Your record has been deleted successfully.")

    def on_cancel_button_click(self):
        self.edit_password.destroy()

class BreachCheck:
    def __init__(self, root, datamanager: DataManager, func = None, window=None):
        self.root = root
        self.func = func
        self.parent = window

        self.datamanager = datamanager
        self.data = self.datamanager.load_data()
        self.data = self.datamanager.decrypt_data(self.data)

        self.breach_check = ctk.CTkToplevel(self.root)
        self.breach_check.title("VaulTex - Breach Check")
        self.breach_check.geometry("800x650")

        self.breach_check.focus()
        self.breach_check.lift()
        self.breach_check.grab_set()


        self.cancel_button = ctk.CTkButton(self.breach_check, text="Back", command=self.show_parent, fg_color="red", font=custom_font) 
        self.cancel_button.place(x=640, y=10 )

        self.label = ctk.CTkLabel(self.breach_check, text="EXPOSED PASSWORDS",text_color="red", font=("Helvetica", 18, "bold"))
        self.label.place(x=10, y=10)

        self.left_frame = Frame(self.breach_check, 20,50,300,570)
        self.right_frame = Frame(self.breach_check, 350, 205, 420,305)

        self.right_frame.hide()

        self.old_password_label = ctk.CTkLabel(self.right_frame.frame, text="Compromised Password", font=custom_font)
        self.old_password_label.place(x=30, y=30)
        
        self.old_password = ctk.CTkEntry(self.right_frame.frame, width=300, font=custom_font ,fg_color="red")
        self.old_password.place(x=30, y=60)

        self.password_label = ctk.CTkLabel(self.right_frame.frame, text="New Password", font=custom_font)
        self.password_label.place(x=30, y=100)

        self.generate_password_button = ctk.CTkButton(self.right_frame.frame, width=60, height=20, text="generate", command=self._generate_password, font=custom_font)
        self.generate_password_button.place(x=150, y=100)

        self.show_password_button = ctk.CTkButton(self.right_frame.frame, width=50, height=20, text="show", command=self._show_pass, font=custom_font)
        self.show_password_button.place(x=340, y=130)

        self.new_password = ctk.CTkEntry(self.right_frame.frame, width=300, show="•", font=custom_font)
        self.new_password.place(x=30, y=130)

        self.check_button = ctk.CTkButton(self.right_frame.frame, text="Check Password", command=self.check_password, font=custom_font)
        self.check_button.place(x=130, y=200)
        self.confirm_button = ctk.CTkButton(self.right_frame.frame, text="Confirm", font=custom_font, state="disabled",command=self.modify_password , fg_color="green")
        self.confirm_button.place(x=130, y=250)

        if platform.startswith("win"):
            self.breach_check.after(200, lambda: self.breach_check.iconbitmap("assets/tex.ico"))
        self.refresh()


    def refresh(self):
        widgets = self.left_frame.frame.winfo_children()
        for widget in widgets:
            widget.destroy()

        j = 10
        for i in range(0, len(self.data["accounts"])):
            password = self.data["accounts"][i]["password"]
            service = self.data["accounts"][i]["service"] if "service" in self.data["accounts"][i] else "Master"

            if check_password(password=password):
                button = ctk.CTkButton(self.left_frame.frame, width=290, height=50, text=service, command=partial(self.display_password, i), font=custom_font ,fg_color="red")
                button.__dict__["i"] = i
                button.place(x = 5, y = j)
                j+=60

    def _generate_password(self):
        password = generatePassword()
        self.new_password.delete(0,"end")
        self.new_password.insert(0,password)

    def display_password(self, i):
        self.right_frame.show()
        self.old_password.delete(0, "end")
        self.old_password.insert(0, self.data["accounts"][i]["password"])

        self.new_password.delete(0, "end")
        self.__dict__["current_index"] = i

    def _show_pass(self):
        show_password(self.new_password)
    
    def check_password(self):
        password = self.new_password.get()
        if(password!=' '):
            if not (check_password(password)):
                self.confirm_button.configure(state="normal")
            else:
                messagebox.showinfo("PASSWORD SAFE", "This password has not been exposed, Please Try Anothe One")
        else:
            messagebox.showinfo("INVALID INPUT", "Please fill compromised password field")
        
    def modify_password(self):
        i =  self.__dict__["current_index"]

        password = self.new_password.get()
        if len(self.new_password.get()) > 8:
            if not (check_password(password)):
                self.new_password.configure(fg_color  = "green")
                self.data["accounts"][i]["password"] = password

                print(self.data["accounts"][i]["password"])

                self.datamanager.save_new_data(self.data)
                messagebox.showinfo("PASSWORD UPDATED", "Your password has been updated. Stay safe out there.")
                self.refresh()
                self.func()
                self.right_frame.hide()
            else:
                messagebox.showwarning("EXPOSED PASSWORDS","This password has already been exposed, Try another one.")

    def show_parent(self):
        if self.parent != None:
            self.parent.deiconify()
        self.breach_check.destroy()    
     
class PasswordGenerationWindow:
    def __init__(self, root, password_entry: ctk.CTkEntry):
        self.root = root;
        self.root.iconbitmap('./assets/tex.ico')
        self.window = ctk.CTkToplevel(self.root)
        self.window.title("Generate Password")
        self.window.geometry("300x540")
        self.window.resizable(False, False)
        self.customfont=("Helvetica", 13, "bold")

        self.window.focus()
        self.window.grab_set()

        self.pass_label = ctk.CTkLabel(self.window, text="Password", font=custom_font)
        self.pass_label.place(x=10, y=20)

        self.pass_entry = ctk.CTkEntry(self.window,width=280, font=custom_font)
        self.pass_entry.place(x=10,y=50)

        self.controls_label = ctk.CTkLabel(self.window, text="Controls", font=("Helvetica", 20, "bold"))
        self.controls_label.place(x=100, y=90)


        #OUTPUT VARIABLES 
        self.generated_password = ""
        self.password_entry = password_entry

        self.controls_frame = ctk.CTkFrame(self.window, width=280, height=280)
        self.controls_frame.place(x=10, y=130)
        #CONTROLS

        self.pass_length_slider = ctk.CTkSlider(self.controls_frame, width=250, from_=6, to=25, command=self.change_label,variable=IntVar(value=6))
        self.pass_length_slider.place(x=10, y=50)

        self.length_label = ctk.CTkLabel(self.controls_frame, text=f"Length:{int(self.pass_length_slider.get())}", font=self.customfont)
        self.length_label.place(x=10, y=20)

        self.characters_slider = ctk.CTkSlider(self.controls_frame, width=250, from_=0, to=int(self.pass_length_slider.get()), command=self.change_charlen, variable=IntVar(value=2))
        self.characters_slider.place(x=10, y=105)

        self.charlen_label = ctk.CTkLabel(self.controls_frame, text=f"Chars: {self.characters_slider.get()}", font= self.customfont )
        self.charlen_label.place(x=10, y=70)

        self.upcase_slider = ctk.CTkSlider(self.controls_frame, width=250, from_=0, to=(self.pass_length_slider.get() - self.characters_slider.get()), command=self.change_upcase, variable=IntVar(value=2))
        self.upcase_slider.place(x=10, y=155)

        self.upcase_label = ctk.CTkLabel(self.controls_frame, text=f"Uppercase:{int(self.upcase_slider.get())}", font=self.customfont)
        self.upcase_label.place(x=10, y=125)

        val = int(self.pass_length_slider.get()) - int(self.characters_slider.get()) - int(self.upcase_slider.get());

        self.num_slider = ctk.CTkSlider(self.controls_frame, width=250, from_=0, to=val, command=self.change_nums, variable=IntVar(value=2))
        self.num_slider.place(x=10, y=205)

        self.num_label = ctk.CTkLabel(self.controls_frame, text=f"Numbers:{math.ceil(self.upcase_slider.get())}", font=self.customfont)
        self.num_label.place(x=10, y=175)

        self.generate_button = ctk.CTkButton(self.window, text="Generate", font=custom_font, command=self.ongenerate_button_click)
        self.generate_button.place(x=80, y=420)

        self.save_button = ctk.CTkButton(self.window, text="Save", font=custom_font, command=self.on_save_button_click);
        self.save_button.place(x=80, y=460)
        
        self.cancel_button = ctk.CTkButton(self.window, text="Cancel", font=custom_font, fg_color="red", command=self.oncancel_button_click)
        self.cancel_button.place(x=80, y=500)

        if platform.startswith("win"):
            self.window.after(200, lambda: self.window.iconbitmap("assets/tex.ico"))

    def change_charlen(self, value):
        self.charlen_label.configure(text=f"Chars:{math.ceil(value)}")
        self.upcase_slider.configure(to=int(self.pass_length_slider.get()) - value, variable = IntVar(value=self.upcase_slider.get()))
        self.upcase_label.configure(text=f"Uppercase:{math.ceil(self.upcase_slider.get())}")

        _val = math.ceil(self.pass_length_slider.get()) - int(value) - int(self.upcase_slider.get())

        self.num_label.configure(text=f"Number:{math.ceil(self.num_slider.get())}")
        self.num_slider.configure(to =_val, variable = IntVar(value = self.num_slider.get()))
        #self.upcase_slider.configure(to=int(value - self.characters_slider.get()), variable=IntVar(value = self.upcase_slider.get()))
     
    def change_label(self, value):
        self.length_label.configure(text=f"Length:{math.ceil(value)}")
        self.characters_slider.configure(to=math.ceil(value), variable=IntVar(value=int(self.characters_slider.get())))
        """self.upcase_label.configure(text=f"Uppercase:{int(self.upcase_slider.get())}")"""
        self.upcase_slider.configure(to=int(value - self.characters_slider.get()), variable=IntVar(value = self.upcase_slider.get()))
        _val = math.ceil(value) - int(self.characters_slider.get()) - int(self.upcase_slider.get())
        self.num_slider.configure(to =_val, variable = IntVar(value = self.num_slider.get()))
            
    def change_upcase(self, value):
        self.upcase_label.configure(text=f"Uppercase:{math.ceil(value)}")

        self.characters_slider.configure(to=math.ceil(self.pass_length_slider.get() - value), variable=IntVar(value=int(self.characters_slider.get())))
        self.charlen_label.configure(text=f"Chars:{math.ceil(self.characters_slider.get())}")
        
        _val = math.ceil(self.pass_length_slider.get()) - int(self.characters_slider.get()) - int(value)
        self.num_slider.configure(to =_val, variable = IntVar(value = self.num_slider.get()))
        self.num_label.configure(text=f"Numbers:{math.ceil(self.num_slider.get())}")
   
    def change_nums(self, value):
        self.num_label.configure(text=f"Numbers:{math.ceil(value)}")

    def ongenerate_button_click(self):
        self.pass_entry.delete(0, "end")
        max_len = math.ceil(self.pass_length_slider.get())
        min_sp_chars = math.ceil(self.characters_slider.get())
        min_upper = math.ceil(self.upcase_slider.get())
        min_nums = math.ceil(self.num_slider.get())

        self.generated_password = generateCuratedPassword(
                min_len=max_len, max_len=max_len, 
                min_special_chars=min_sp_chars, 
                min_uppercase=min_upper, 
                min_nums=min_nums
            )
        
        self.pass_entry.insert(0, self.generated_password)
        
    def on_save_button_click(self):
        if len(self.generated_password) > 5:
            self.password_entry.insert(0, self.generated_password)
            self.window.destroy()
        else:
            messagebox.showerror("EMPTY PASSWORD", "Cannot save empty password.")
    
    def oncancel_button_click(self):
        self.window.destroy()

    def getPassword(self):
        return self.generated_password

class ChangePassword:
    def __init__(self, root, data,datamanager: DataManager, func):
        self.root =root
        self.datamanager = datamanager
        self.data = data
        self.func = func

        self.window = ctk.CTkToplevel(self.root)
        self.window.title("VaulTex- Change Password")
        self.window.geometry("320x300")

        self.window.grab_set()
        self.window.focus()
        self.window.lift()

        self.window.after(200, lambda: self.window.iconbitmap("assets/tex.ico"))

        self.password_label = ctk.CTkLabel(self.window, text="New Password", font=custom_font)
        self.password_entry = ctk.CTkEntry(self.window, width=300, show="•" ,font=custom_font)
        self.password_label.place(x=10, y=30)
        self.password_entry.place(x=10, y=60)

        self.conf_passlabel = ctk.CTkLabel(self.window, text="Confirm Password", font=custom_font)
        self.conf_passentry = ctk.CTkEntry(self.window, width=300, show="•", font=custom_font)
        self.conf_passlabel.place(x=10, y=90)
        self.conf_passentry.place(x=10, y=120)

        self.save_button = ctk.CTkButton(self.window, text="Save",command=self.on_save_button_click, font=custom_font)
        self.save_button.place(x=80, y=190)

        self.cancel_button = ctk.CTkButton(self.window, text="Cancel", command=self.on_cancel_button_click, fg_color="red", font=custom_font)
        self.cancel_button.place(x=80, y=240)

    def on_save_button_click(self):
        new_password = self.password_entry.get()
        conf_password = self.password_entry.get()

        if new_password == '':
            messagebox.showwarning("INVALID INPUT", "Please fill in the new password field.")
        elif len(new_password) < 8:
            messagebox.showwarning("INVALID INPUT", "Password must be longer than 8 characters.")
        elif new_password != conf_password:
            messagebox.showwarning("PASSWORD DOES NOT MATCH", "Please make sure that your password matches")
        else:
            messagebox.showinfo("CHANGE PASSWORD", "Please make sure to not forget your new password. \nThe Master Password cannot be retrieved if lost.")
            self.datamanager.change_master_password(new_password, self.data)
            self.func()
            messagebox.showinfo("CHANGE PASSWORD", "Your Master Password has been changed.")
            self.window.destroy()

    def on_cancel_button_click(self):
        self.window.destroy()

if __name__ == "__main__":
    root = ctk.CTk()
    app = LogIn(root=root)
    root.mainloop()


