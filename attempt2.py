import tkinter as tk
from tkinter import messagebox, filedialog, simpledialog
from datetime import datetime

class Account:
    def __init__(self, username, age, password):
        self.username = username
        self.age = age
        self.password = password
        self.gender = "Fruit"  # Default
        self.date_format = "%Y-%m-%d"

class LoginApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Food Tracker")
        self.root.geometry("300x220")

        self.accounts = {}
        # Preload default user
        self.accounts["Apple"] = Account("Apple", "1 week", "Orange")

        self.frame = tk.Frame(root)
        self.frame.pack(pady=10)

        tk.Label(self.frame, text="Username:").pack()
        self.entry_username = tk.Entry(self.frame)
        self.entry_username.pack()

        tk.Label(self.frame, text="Password:").pack()
        self.entry_password = tk.Entry(self.frame, show="*")
        self.entry_password.pack()

        self.btn_login = tk.Button(self.frame, text="Login", command=self.check_login)
        self.btn_login.pack(pady=5)

        self.btn_create = tk.Button(self.frame, text="Create Account", command=self.create_account)
        self.btn_create.pack()

    def check_login(self):
        user = self.entry_username.get()
        pwd = self.entry_password.get()
        account = self.accounts.get(user)
        if account and account.password == pwd:
            messagebox.showinfo("Login Success", f"Welcome {user}!")
            self.root.destroy()
            MainApp(account)
        else:
            messagebox.showerror("Login Failed", "Invalid username or password")

    def create_account(self):
        create_win = tk.Toplevel(self.root)
        create_win.title("Create Account")
        create_win.geometry("300x230")

        tk.Label(create_win, text="Username:").pack(pady=2)
        entry_user = tk.Entry(create_win)
        entry_user.pack(pady=2)

        tk.Label(create_win, text="Age:").pack(pady=2)
        entry_age = tk.Entry(create_win)
        entry_age.pack(pady=2)

        tk.Label(create_win, text="Password:").pack(pady=2)
        entry_pwd = tk.Entry(create_win, show="*")
        entry_pwd.pack(pady=2)

        def save_new_account():
            username = entry_user.get().strip()
            age = entry_age.get().strip()
            password = entry_pwd.get()
            if not username or not password:
                messagebox.showerror("Error", "Username and Password required.")
                return
            if username in self.accounts:
                messagebox.showerror("Error", "Username already exists.")
                return
            self.accounts[username] = Account(username, age, password)
            messagebox.showinfo("Success", f"Account created for {username}. Please login.")
            create_win.destroy()

        tk.Button(create_win, text="Create", command=save_new_account).pack(pady=10)

class MainApp:
    def __init__(self, account):
        self.account = account
        self.pantry = []

        self.window = tk.Tk()
        self.window.title("Food Tracker Main Menu")
        self.window.geometry("400x320")

        btn_scan = tk.Button(self.window, text="Scan Item", width=20, command=self.scan_item)
        btn_pantry = tk.Button(self.window, text="Pantry", width=20, command=self.show_pantry)
        btn_recipe = tk.Button(self.window, text="Generate Recipe", width=20, command=self.generate_recipe)
        btn_cameras = tk.Button(self.window, text="Cameras", width=20, command=self.cameras)
        btn_friends = tk.Button(self.window, text="Friends", width=20, command=self.friends)
        btn_account = tk.Button(self.window, text="Account", width=20, command=self.show_account)

        btn_scan.pack(pady=5)
        btn_pantry.pack(pady=5)
        btn_recipe.pack(pady=5)
        btn_cameras.pack(pady=5)
        btn_friends.pack(pady=5)
        btn_account.pack(pady=5)

        self.window.mainloop()

    def scan_item(self):
        # Placeholder for AI image recognition
        file_path = filedialog.askopenfilename(
            title="Select food photo",
            filetypes=[("Image files", "*.jpg *.jpeg *.png")]
        )
        if file_path:
            name = file_path.split("/")[-1]
            self.pantry.append({"name": name, "expiry": None})
            messagebox.showinfo("Item Scanned", f"Added {name} to pantry (AI recognition to add later)")

    def show_pantry(self):
        self.pantry_win = tk.Toplevel(self.window)
        self.pantry_win.title("Pantry Items")
        self.pantry_win.geometry("450x350")

        if not self.pantry:
            tk.Label(self.pantry_win, text="Pantry is empty").pack(pady=20)

        self.listbox = tk.Listbox(self.pantry_win, width=50, height=12)
        self.listbox.pack(pady=10)

        self.update_pantry_listbox()

        # Buttons always present
        btn_frame = tk.Frame(self.pantry_win)
        btn_frame.pack(pady=5)

        btn_edit = tk.Button(btn_frame, text="Edit Pantry", command=self.edit_item)
        btn_edit.grid(row=0, column=0, padx=5)

        btn_add = tk.Button(btn_frame, text="Add Item", command=self.add_item)
        btn_add.grid(row=0, column=1, padx=5)

        btn_delete = tk.Button(btn_frame, text="Delete Item", command=self.delete_item)
        btn_delete.grid(row=0, column=2, padx=5)

    def update_pantry_listbox(self):
        self.listbox.delete(0, tk.END)
        for item in self.pantry:
            expiry_str = item["expiry"].strftime(self.account.date_format) if item["expiry"] else "No expiry"
            self.listbox.insert(tk.END, f"{item['name']} , Expiry: {expiry_str}")

    def edit_item(self):
        selections = self.listbox.curselection()
        if not selections:
            messagebox.showerror("Selection Error", "Please select an item to edit")
            return
        index = selections[0]
        item = self.pantry[index]

        edit_win = tk.Toplevel(self.pantry_win)
        edit_win.title("Edit Pantry Item")
        edit_win.geometry("300x180")

        tk.Label(edit_win, text="Name:").pack(pady=5)
        entry_name = tk.Entry(edit_win)
        entry_name.pack()
        entry_name.insert(0, item["name"])

        tk.Label(edit_win, text=f"Expiry Date ({self.account.date_format}):").pack(pady=5)
        entry_expiry = tk.Entry(edit_win)
        entry_expiry.pack()
        if item["expiry"]:
            entry_expiry.insert(0, item["expiry"].strftime(self.account.date_format))

        def save_changes():
            new_name = entry_name.get().strip()
            expiry_str = entry_expiry.get().strip()
            if not new_name:
                messagebox.showerror("Input Error", "Name cannot be empty")
                return
            try:
                new_expiry = datetime.strptime(expiry_str, self.account.date_format).date() if expiry_str else None
            except:
                messagebox.showerror("Input Error", f"Expiry date must be in {self.account.date_format} format or empty")
                return

            self.pantry[index]["name"] = new_name
            self.pantry[index]["expiry"] = new_expiry
            self.update_pantry_listbox()
            edit_win.destroy()

        tk.Button(edit_win, text="Save", command=save_changes).pack(pady=10)

    def add_item(self):
        add_win = tk.Toplevel(self.pantry_win)
        add_win.title("Add Pantry Item")
        add_win.geometry("300x180")

        tk.Label(add_win, text="Name:").pack(pady=5)
        entry_name = tk.Entry(add_win)
        entry_name.pack()

        tk.Label(add_win, text=f"Expiry Date ({self.account.date_format}):").pack(pady=5)
        entry_expiry = tk.Entry(add_win)
        entry_expiry.pack()

        def save_new():
            name = entry_name.get().strip()
            expiry_str = entry_expiry.get().strip()
            if not name:
                messagebox.showerror("Input Error", "Name cannot be empty")
                return
            try:
                expiry = datetime.strptime(expiry_str, self.account.date_format).date() if expiry_str else None
            except:
                messagebox.showerror("Input Error", f"Expiry date must be in {self.account.date_format} format or empty")
                return
            self.pantry.append({"name": name, "expiry": expiry})
            self.update_pantry_listbox()
            add_win.destroy()

        tk.Button(add_win, text="Add", command=save_new).pack(pady=10)

    def delete_item(self):
        selections = self.listbox.curselection()
        if not selections:
            messagebox.showerror("Selection Error", "Please select an item to delete")
            return
        index = selections[0]
        item_name = self.pantry[index]["name"]
        if messagebox.askyesno("Confirm Delete", f"Delete {item_name}?"):
            del self.pantry[index]
            self.update_pantry_listbox()

    def generate_recipe(self):
        if not self.pantry:
            messagebox.showinfo("Generate Recipe", "Pantry is empty, add some items first.")
            return
        ingredients = ', '.join([i["name"] for i in self.pantry])
        messagebox.showinfo("Recipe Generation", f"Generating recipe using: {ingredients}")

    def cameras(self):
        messagebox.showinfo("Coming Soon", "Cameras feature will be added later.")

    def friends(self):
        messagebox.showinfo("Coming Soon", "Friends feature will be added later.")

    def show_account(self):
        self.account_win = tk.Toplevel(self.window)
        self.account_win.title("User Account")
        self.account_win.geometry("350x300")

        def edit_personal_info():
            edit_win = tk.Toplevel(self.account_win)
            edit_win.title("Edit Personal Info")
            edit_win.geometry("300x220")

            tk.Label(edit_win, text="Name:").pack(pady=2)
            entry_name = tk.Entry(edit_win)
            entry_name.pack(pady=2)
            entry_name.insert(0, self.account.username)

            tk.Label(edit_win, text="Age:").pack(pady=2)
            entry_age = tk.Entry(edit_win)
            entry_age.pack(pady=2)
            entry_age.insert(0, self.account.age)

            tk.Label(edit_win, text="Gender:").pack(pady=2)
            entry_gender = tk.Entry(edit_win)
            entry_gender.pack(pady=2)
            entry_gender.insert(0, self.account.gender)

            def save_info():
                self.account.username = entry_name.get().strip()
                self.account.age = entry_age.get().strip()
                self.account.gender = entry_gender.get().strip()
                messagebox.showinfo("Saved", "Personal info updated.")
                edit_win.destroy()
                self.account_win.destroy()  # Close account window to reflect changes on relaunch

            tk.Button(edit_win, text="Save", command=save_info).pack(pady=10)

        def settings():
            settings_win = tk.Toplevel(self.account_win)
            settings_win.title("Settings")
            settings_win.geometry("300x220")

            tk.Label(settings_win, text="Date Format (Python strftime format):").pack(pady=5)
            entry_date_fmt = tk.Entry(settings_win)
            entry_date_fmt.pack()
            entry_date_fmt.insert(0, self.account.date_format)

            def save_settings():
                fmt = entry_date_fmt.get().strip()
                try:
                    datetime.now().strftime(fmt)
                    self.account.date_format = fmt
                    messagebox.showinfo("Success", "Date format updated.")
                    settings_win.destroy()
                except:
                    messagebox.showerror("Error", "Invalid date format string.")

            tk.Button(settings_win, text="Save", command=save_settings).pack(pady=10)

            def change_password():
                cp_win = tk.Toplevel(settings_win)
                cp_win.title("Change Password")
                cp_win.geometry("300x180")

                tk.Label(cp_win, text="Current Password:").pack(pady=2)
                entry_current = tk.Entry(cp_win, show='*')
                entry_current.pack(pady=2)

                tk.Label(cp_win, text="New Password:").pack(pady=2)
                entry_new = tk.Entry(cp_win, show='*')
                entry_new.pack(pady=2)

                tk.Label(cp_win, text="Confirm New Password:").pack(pady=2)
                entry_confirm = tk.Entry(cp_win, show='*')
                entry_confirm.pack(pady=2)

                def save_password():
                    current = entry_current.get()
                    new = entry_new.get()
                    confirm = entry_confirm.get()
                    if current != self.account.password:
                        messagebox.showerror("Error", "Current password incorrect.")
                        return
                    if new != confirm:
                        messagebox.showerror("Error", "New passwords do not match.")
                        return
                    if not new:
                        messagebox.showerror("Error", "New password cannot be empty.")
                        return
                    self.account.password = new
                    messagebox.showinfo("Success", "Password changed successfully.")
                    cp_win.destroy()

                tk.Button(cp_win, text="Save Password", command=save_password).pack(pady=10)

            tk.Button(settings_win, text="Change Password", command=change_password).pack(pady=10)

        # Show user info
        info_str = f"Name: {self.account.username}\nAge: {self.account.age}\nGender: {self.account.gender}\nDate Format: {self.account.date_format}"
        tk.Label(self.account_win, text=info_str).pack(pady=10)

        tk.Button(self.account_win, text="Edit Personal Info", command=edit_personal_info).pack(pady=5)
        tk.Button(self.account_win, text="Settings", command=settings).pack(pady=5)

if __name__ == "__main__":
    root = tk.Tk()
    login_app = LoginApp(root)
    root.mainloop()