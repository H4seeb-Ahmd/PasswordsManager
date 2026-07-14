'''
PASSWORD MANAGER SOFTWARE

'''

import tkinter as tk
from tkinter import font, messagebox, ttk

import pandas as pd

import io

import pyperclip

from Crypto.Cipher import AES
from Crypto.Protocol.KDF import PBKDF2
from Crypto.Random import get_random_bytes

TextFont = None
EncryptedFilePath = "passwords_encrypted.bin"
PasswordsFileText = None
CurrentEncryptionKey = None

COL_DATA_TYPE = {'website':str, 'ID': str, 'password':str}

def join_frames(left_frame, right_frame):
    final_frame = tk.Frame

def get_id(self, website):
    website_data = self.df[self.df['website'] == website]

    if not website_data.empty:
        user_id = website_data.iloc[0]['ID']
        
        return user_id
    else:
        return None
        
def get_pass(self, website):
    website_data = self.df[self.df['website'] == website]
    
    if not website_data.empty:
        password = website_data.iloc[0]['password']
        
        return password

def get_websites(self):

    websites_df = self.df
    websites_list = websites_df['website'].to_list()
    
    return websites_list


def InitialiseApp():
    password = "admin"

    salt = get_random_bytes(16) 
    key = PBKDF2(password, salt, dkLen=16) 

    text = "website,ID,password"


    data = text.encode('utf-8')

    cipher = AES.new(key, AES.MODE_EAX)
    nonce = cipher.nonce
    ciphertext = cipher.encrypt(data)

    # Save salt + nonce + ciphertext to a binary file
    with open(EncryptedFilePath, 'wb') as f_enc:
        f_enc.write(salt)       
        f_enc.write(nonce)      
        f_enc.write(ciphertext) 


def update_file(encryption_key):
    global PasswordsFileText
    salt = get_random_bytes(16)  
    key = PBKDF2(encryption_key, salt, dkLen=16)

    cipher = AES.new(key, AES.MODE_EAX)
    nonce = cipher.nonce
    ciphertext = cipher.encrypt(PasswordsFileText.encode('utf-8'))
   

    PasswordsFileText = None

    # Save salt + nonce + ciphertext to a binary file
    with open(EncryptedFilePath, 'wb') as f_enc:
        f_enc.write(salt)       
        f_enc.write(nonce)      
        f_enc.write(ciphertext) 


def is_authentic(password):
    global PasswordsFileText
    try:
        with open(EncryptedFilePath, 'rb') as f_enc:
            salt_from_file = f_enc.read(16)
            nonce_from_file = f_enc.read(16)
            ciphertext_from_file = f_enc.read()

        key = PBKDF2(password, salt_from_file, dkLen=16)
        cipher_dec = AES.new(key, AES.MODE_EAX, nonce=nonce_from_file)
        plaintext_bytes = cipher_dec.decrypt(ciphertext_from_file)
        PasswordsFileText = plaintext_bytes.decode('utf-8')
        return True
    except:
        PasswordsFileText = None
        return False
    
class AddPasswordPage:
    def __init__(self, master, switch_to_main):
        self.switch_to_main = switch_to_main
        self.df = pd.read_csv(io.StringIO(PasswordsFileText), dtype=COL_DATA_TYPE)
        self.master = master
        self.app_panel = tk.Frame(self.master)
    
        # Title
        self.title_label = tk.Label(self.app_panel)
        self.title_label.configure(
            text="ADD CREDENTIAL",
            font=("Courier", 20, "bold"),
            pady=20
        )
        self.title_label.pack(pady=20)

        #Website
        self.website_label = tk.Label(
            self.app_panel,
            text="Website:",
            font=TextFont
        )
        self.website_label.pack(pady=5)
        self.website = tk.StringVar()
        self.website_tb = tk.Entry(
            self.app_panel,
            font = TextFont,
            textvariable = self.website,
            width = 20
            )
        self.website_tb.pack(pady = 5)

        #ID
        self.id_label = tk.Label(
            self.app_panel,
            text="ID:",
            font=TextFont
        )
        self.id_label.pack(pady=5)
        self.id = tk.StringVar()
        self.id_tb = tk.Entry(
            self.app_panel,
            font = TextFont,
            textvariable = self.id,
            width = 20
            )
        self.id_tb.pack(pady = 5)
        
        #PASS
        self.pass_label = tk.Label(
            self.app_panel,
            text="Password:",
            font=TextFont
        )
        self.pass_label.pack(pady=5)
        self.pass_var = tk.StringVar()
        self.pass_tb = tk.Entry(
            self.app_panel,
            font = TextFont,
            textvariable = self.pass_var,
            width = 20,
            show = "*"
            )
        self.pass_tb.pack(pady = 5)

        # Add, Edit, Delete buttons
        tk.Button(
            self.app_panel, 
            text="Add Password", 
            font=TextFont, 
            command = lambda: self.add_pass()
            ).pack(pady=5)
        tk.Button(
            self.app_panel, 
            text="Back", 
            font=TextFont, 
            command = lambda: self.switch_to_main(self.app_panel)
            ).pack(pady=5)

        self.app_panel.pack()

    def add_pass(self):
        website = self.website.get().strip()
        user_id = self.id.get().strip()
        password = self.pass_var.get()
        
        if not website or not user_id or not password:
            messagebox.showerror("Error", "All fields must be filled")
            return
        
        # Check if website already exists
        if website in get_websites(self):
            messagebox.showerror("Error", "Website already exists")
            return
        
        # Read current data
        global PasswordsFileText
        df = pd.read_csv(io.StringIO(PasswordsFileText), dtype=COL_DATA_TYPE)
        
        
        # Add the entry
        entry = [str(website), str(user_id), str(password)]
        
        df.loc[len(df)] = entry
        
        # Update the global variable
        PasswordsFileText = df.to_csv(index=False)

        
        
        
        # Re-encrypt the data
        update_file(CurrentEncryptionKey)
        messagebox.showinfo("Success", "Password added successfully")
        self.switch_to_main(self.app_panel)

    def get_websites(self):

        websites_df = self.df
        websites_list = websites_df['website'].to_list()

        return websites_list

class EditPasswordPage:
    def __init__(self, master, switch_to_main):
        self.switch_to_main = switch_to_main
        self.df = pd.read_csv(io.StringIO(PasswordsFileText), dtype=COL_DATA_TYPE)
        self.master = master
        self.app_panel = tk.Frame(self.master)

        self.websites = get_websites(self)

    
        # Title
        self.title_label = tk.Label(self.app_panel)
        self.title_label.configure(
            text="EDIT CREDENTIAL",
            font=("Courier", 20, "bold"),
            pady=20
        )
        self.title_label.pack(pady=20)

        # Website dropdown
        self.drop_label = tk.Label(
            self.app_panel,
            text="Website:",
            font=TextFont
        )
        self.drop_label.pack(pady=5)
        self.website_var = tk.StringVar()
        self.dropdown = ttk.Combobox(
            self.app_panel, 
            textvariable = self.website_var, 
            values = self.websites,
            font = TextFont,
            state = "readonly")
        self.website_var.trace_add("write", lambda *_ : self.update_creds())
        
        self.dropdown.config()
        
        self.dropdown.pack(pady=10)

        #ID
        self.id_label = tk.Label(
            self.app_panel,
            text="ID:",
            font=TextFont
        )
        self.id_label.pack(pady=5)
        self.id = tk.StringVar(
            value = get_id(self, self.website_var.get()))
        self.id_tb = tk.Entry(
            self.app_panel,
            font = TextFont,
            textvariable = self.id,
            width = 20
            )
        self.id_tb.pack(pady = 5)
        
        #PASS
        self.pass_label = tk.Label(
            self.app_panel,
            text="Password:",
            font=TextFont
        )
        self.pass_label.pack(pady=5)
        self.pass_var = tk.StringVar(
            value = get_pass(self, self.website_var.get()))
        self.pass_tb = tk.Entry(
            self.app_panel,
            font = TextFont,
            textvariable = self.pass_var,
            width = 20,
            show = "*"
            )
        self.pass_tb.pack(pady = 5)

        # Add, Edit, Delete buttons
        tk.Button(self.app_panel, text="Edit Password", font=TextFont, command = lambda: self.edit_pass()).pack(pady=5)
        tk.Button(self.app_panel, text="Back", font=TextFont, command = lambda: self.switch_to_main(self.app_panel)).pack(pady=5)

        self.app_panel.pack()

    def edit_pass(self):
        website = self.website_var.get()
        new_id = self.id.get()
        new_password = self.pass_var.get()
        
        if not new_id or not new_password:
            messagebox.showerror("Error", "All fields must be filled")
            return
        
        # Read current data
        global PasswordsFileText
        df = pd.read_csv(io.StringIO(PasswordsFileText), dtype=COL_DATA_TYPE)
        
        # Update the entry
        mask = df['website'] == website
        df.loc[mask, 'ID'] = str(new_id)
        df.loc[mask, 'password'] = str(new_password)
        
        # Update the global variable
        PasswordsFileText = df.to_csv(index=False)
        
        # Re-encrypt the data
        update_file(CurrentEncryptionKey)
        messagebox.showinfo("Success", "Password updated successfully")
        self.switch_to_main(self.app_panel)

    def update_creds(self):
        self.id.set(get_id(self, self.website_var.get()))
        self.pass_var.set(get_pass(self, self.website_var.get()))




class DeletePassPage:
    def __init__(self, master, switch_to_main):
        self.switch_to_main = switch_to_main
        self.df = pd.read_csv(io.StringIO(PasswordsFileText), dtype=COL_DATA_TYPE)
        self.master = master
        self.app_panel = tk.Frame(self.master)

        self.websites = get_websites(self)

    
        # Title
        self.title_label = tk.Label(self.app_panel)
        self.title_label.configure(
            text="DELETE CREDENTIAL",
            font=("Courier", 20, "bold"),
            pady=20
        )
        self.title_label.pack(pady=20)

        # Website dropdown
        self.drop_label = tk.Label(
            self.app_panel,
            text="Website:",
            font=TextFont
        )
        self.drop_label.pack(pady=5)
        self.website_var = tk.StringVar()
        self.dropdown = ttk.Combobox(
            self.app_panel, 
            textvariable = self.website_var, 
            values = self.websites,
            font = TextFont,
            state = "readonly")
        
        self.dropdown.config()
        
        self.dropdown.pack(pady=10)

        # Add, Edit, Delete buttons
        tk.Button(self.app_panel, text="Delete Password", font=TextFont, command = lambda: self.delete_pass()).pack(pady=5)
        tk.Button(self.app_panel, text="Back", font=TextFont, command = lambda: self.switch_to_main(self.app_panel)).pack(pady=5)

        self.app_panel.pack()

    def delete_pass(self):
        website = self.website_var.get()
    
        if not website:
            messagebox.showerror("Error", "Please select a website")
            return
        
        # Read current data
        global PasswordsFileText
        df = pd.read_csv(io.StringIO(PasswordsFileText), dtype=COL_DATA_TYPE)
        
        # Remove the entry
        df = df[df['website'] != website]
        
        # Update the global variable
        PasswordsFileText = df.to_csv(index=False)
        
        # Re-encrypt the data
        update_file(CurrentEncryptionKey)
        messagebox.showinfo("Success", "Password deleted successfully")
        self.switch_to_main(self.app_panel)


class PasswordManager:
    def __init__(self, master):
        self.df = pd.read_csv(io.StringIO(PasswordsFileText), dtype=COL_DATA_TYPE)
        self.master = master
        self.app_panel = tk.Frame(self.master)

        self.websites = get_websites(self)

    
        # Title
        self.title_label = tk.Label(self.app_panel)
        self.title_label.configure(
            text="PASSWORD MANAGER",
            font=("Courier", 20, "bold"),
            pady=20
        )
        self.title_label.pack(pady=20)

        # Website dropdown
        self.drop_label = tk.Label(
            self.app_panel,
            text="Website:",
            font=TextFont
        )
        self.drop_label.pack(pady=5)
        self.website_var = tk.StringVar()
        self.dropdown = ttk.Combobox(
            self.app_panel, 
            textvariable = self.website_var, 
            values = self.websites,
            font = TextFont,
            state = "readonly")
        self.website_var.trace_add("write", lambda *_ : self.update_creds())
        
        self.dropdown.config()
        
        self.dropdown.pack(pady=10)

        #ID
        self.id_label = tk.Label(
            self.app_panel,
            text="ID:",
            font=TextFont
        )
        self.id_label.pack(pady=5)
        self.id = tk.StringVar(
            value = get_id(self, self.website_var.get()))
        self.id_tb = tk.Entry(
            self.app_panel,
            font = TextFont,
            state = "readonly",
            textvariable = self.id,
            width = 20
            )
        self.id_tb.pack(pady = 5)
        self.id_copy = tk.Button(self.app_panel, 
                                 text = 'Copy ID', 
                                 font = TextFont, 
                                 command = self.copy_id)
        self.id_copy.pack()
        
        #PASS

        self.pass_var = tk.StringVar(value = get_pass(self, self.website_var.get()))
        self.pass_copy = tk.Button(self.app_panel, 
                                 text = 'Copy Password', 
                                 font = TextFont, 
                                 command = lambda : self.copy_pass())
        self.pass_copy.pack(pady=50)

        # Add, Edit, Delete buttons
        tk.Button(
                    self.app_panel, 
                    text="Add Credential", 
                    font=TextFont, command = lambda: self.show_modify_panel(AddPasswordPage)
                ).pack(pady=5)
        tk.Button(
                    self.app_panel, 
                    text="Edit Credential", 
                    font=TextFont, command = lambda: self.show_modify_panel(EditPasswordPage)
                ).pack(pady=5)
        tk.Button(
                    self.app_panel, 
                    text="Delete Credential", 
                    font=TextFont, command = lambda: self.show_modify_panel(DeletePassPage)
                ).pack(pady=5)

        #change password button
        self.change_button = tk.Button(self.app_panel)
        self.change_button.configure(
            bg = "#7D7D7D", 
            text = "CHANGE LOGIN PASSWORD", 
            font = TextFont,
            command = lambda : self.show_to_change_pass(ChangePasswordPanel)
            )
        self.change_button.pack(pady = 30)



        self.app_panel.pack()

    def copy_id(self):
        pyperclip.copy(self.id.get())

    def copy_pass(self):
        pyperclip.copy(self.pass_var.get())

    def update_creds(self):
        self.id.set(get_id(self, self.website_var.get()))
        self.pass_var.set(get_pass(self, self.website_var.get()))

    
    def show_modify_panel(self, ModifyPanel):
        self.app_panel.pack_forget()
        ModifyPanel(self.master, self.switch_to_main)
    
    def switch_to_main(self, current_panel):
        # This will be called when returning from change password panel
        current_panel.pack_forget()

        global CurrentEncryptionKey
        is_authentic(CurrentEncryptionKey)

        self.df = pd.read_csv(io.StringIO(PasswordsFileText), dtype=COL_DATA_TYPE)
        self.websites = get_websites(self)
        self.dropdown.config(values = self.websites)
        self.website_var.set("")
        self.id.set("")
        self.pass_var.set("")
        self.app_panel.pack()

    def show_to_change_pass(self, ModifyPanel):
        self.app_panel.pack_forget()
        ModifyPanel(self.master, self.switch_from_change_pass)

    def switch_from_change_pass(self, current_panel):
        # This will be called when returning from change password panel
        current_panel.pack_forget()
        self.app_panel.pack()

class ChangePasswordPanel:
    def __init__(self, master, switch_to_main):
        self.master = master
        self.switch_to_main = switch_to_main
        
        self.panel = tk.Frame(self.master)
        self.panel.pack(pady=50)
        
        # Title
        self.title = tk.Label(self.panel)
        self.title.config(
            text = "CHANGE LOGIN PASSWORD",
            font = ("Courier", 20, "bold")
        )
        self.title.pack(pady=20)
        
        # Current Password
        self.old_label = tk.Label(
            self.panel,
            text="Current Password:",
            font=TextFont
        )
        self.old_label.pack(pady=5)
        self.old_pass = tk.StringVar()
        self.old_entry = tk.Entry(
            self.panel, 
            textvariable=self.old_pass, 
            show="*", 
            font=TextFont
        )
        self.old_entry.pack(pady=5)
        
        # New Password
        self.new_label = tk.Label(
            self.panel,
            text="New Password:",
            font=TextFont
        )
        self.new_label.pack(pady=5)
        self.new_pass = tk.StringVar()
        self.new_entry = tk.Entry(
            self.panel, 
            textvariable=self.new_pass, 
            show="*", 
            font=TextFont
        )
        self.new_entry.pack(pady=5)
        
        # Confirm New Password
        self.confirm_label = tk.Label(
            self.panel,
            text="Confirm Password:",
            font=TextFont
        )
        self.confirm_label.pack(pady=5)
        self.confirm_pass = tk.StringVar()
        self.confirm_entry = tk.Entry(
            self.panel, 
            textvariable=self.confirm_pass, 
            show="*", 
            font=TextFont
        )
        self.confirm_entry.pack(pady=5)
        
        # Buttons
        tk.Button(
                self.panel, 
                text="Change Password", 
                font=TextFont,
                command=self.change_password).pack(pady=15)
        tk.Button(
                self.panel, 
                text="Back", 
                font=TextFont,
                command=lambda : self.switch_to_main(self.panel)).pack(pady=10)
        
    def change_password(self):

        global PasswordsFileText

        current = self.old_pass.get()
        new = self.new_pass.get()
        confirm = self.confirm_pass.get()

        if not is_authentic(current):
            messagebox.showerror("Error", "Incorrect old password")
            return
        
        if new != confirm:
            messagebox.showerror("Error", "New passwords don't match")
            return
            
        if len(new) < 4:
            messagebox.showerror("Error", "Password must be at least 4 characters")
            return
        
        update_file(new)
        
        messagebox.showinfo("Success", "Password changed successfully")
        self.switch_to_main(self.panel)

class LoginPanel:
    def __init__(self, master):

        EntryWidth = 20
        self.master = master
        
        self.login_panel = tk.Frame(self.master)

        # Title
        self.title_label = tk.Label(self.login_panel)
        self.title_label.configure(
            text="PASSWORD MANAGER",
            font=("Courier", 20, "bold"),
            pady=20
        )
        self.title_label.pack()

        #password entry
        self.password_label = tk.Label(self.login_panel)
        self.password_label.configure(
            text = "PASSWORD: ",
            font = TextFont,
            justify = "left",
            width = EntryWidth
        )
        self.password_label.pack()


        self.password = tk.StringVar()
        self.password_entry = tk.Entry(self.login_panel)
        self.password_entry.configure(
            bg = "#9F9F9F", 
            width = EntryWidth, 
            font = TextFont,
            selectbackground = "#434343",
            show = "*",
            textvariable = self.password
            )
        self.password_entry.pack()


        #enter button
        self.enter_button = tk.Button(self.login_panel)
        self.enter_button.configure(
            bg = "#7D7D7D", 
            text = "ENTER", 
            font = TextFont,
            command = lambda : self.login_user(
                    password = self.password.get()
                )
            )
        self.enter_button.pack(pady = 10)

        #bind enter to <Return>
        self.password_entry.bind(
            sequence = "<Return>",
            func = lambda event: self.login_user(
                password = self.password.get()
            )
        )

        

        # Error message label
        self.error_label = tk.Label(self.login_panel)
        self.error_label.config(
            text = "",
            fg = "#FF0000",
            font = TextFont
        )
        self.error_label.pack()

        #to clear error message
        self.password.trace_add(
            mode = "write",
            callback = lambda *args : self.error_label.config(
                text = ""
            )
        )

        self.login_panel.pack()



    def login_user(self, password):

        global PasswordsFileText

        if is_authentic(password) :
            global CurrentEncryptionKey
            CurrentEncryptionKey = password
            self.show_password_manager()
        else:
            PasswordsFileText = None
            self.error_label.config(
                text = "Incorrect Password"
            )

    def show_password_manager(self):
        self.login_panel.pack_forget()
        PasswordManager(self.master)


class Application:
    
    def __init__(self):

        #create main window's title and dimensions
        self.root = tk.Tk()
        window_width = 500
        window_height = 700
        self.center_window(window_width, window_height)
        self.root.title("Password Manager Software")
        self.root.resizable(False, False)

        #create font
        global TextFont
        TextFont = font.Font(family = "Courier", size = 16)

        LoginPanel(self.root)
        #run the window
        self.root.mainloop()

    def center_window(self, width, height):
        # Get screen dimensions
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        
        # Calculate position
        x = (screen_width // 2) - (width // 2)
        y = (screen_height // 2) - (height // 2)
        
        # Set window position
        self.root.geometry(f'{width}x{height}+{x}+{y}')


try:
    f = open('passwords_encrypted.bin', 'r')
except FileNotFoundError:
    InitialiseApp()
Application()
