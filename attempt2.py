import tkinter as tk
from tkinter import messagebox, filedialog
from PIL import Image, ImageTk
from datetime import datetime, timedelta
import csv
import os

CSV_FILE = "foodapp_infosheet.csv"

class Account:
    def __init__(self, username, age, password):
        self.username = username
        self.age = age
        self.password = password
        self.gender = "Fruit"
        self.date_format = "%Y-%m-%d"

class LoginApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Food Tracker")
        self.root.geometry("300x220")

        self.accounts = {}
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
            MainApp(account, self.accounts)
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
    def __init__(self, account, accounts):
        self.account = account
        self.accounts = accounts

        self.pantry = []

        self.window = tk.Tk()
        self.window.title("Food Tracker Main Menu")
        self.window.geometry("650x500")

        btn_scan = tk.Button(self.window, text="Scan Item", width=20, command=self.scan_item)
        btn_pantry = tk.Button(self.window, text="Pantry", width=20, command=self.show_pantry)
        btn_recipe = tk.Button(self.window, text="Generate Recipe", width=20, command=self.generate_recipe)
        btn_cameras = tk.Button(self.window, text="Cameras", width=20, command=self.cameras)
        btn_friends = tk.Button(self.window, text="Friends", width=20, command=self.friends)
        btn_account = tk.Button(self.window, text="Account", width=20, command=self.show_account)
        btn_signout = tk.Button(self.window, text="Sign Out", width=20, command=self.sign_out)

        btn_scan.pack(pady=5)
        btn_pantry.pack(pady=5)
        btn_recipe.pack(pady=5)
        btn_cameras.pack(pady=5)
        btn_friends.pack(pady=5)
        btn_account.pack(pady=5)
        btn_signout.pack(pady=5)

        self.pantry_win = None

        self.load_pantry_from_csv()  # Load saved pantry

        self.window.mainloop()

    def scan_item(self):
        file_path = filedialog.askopenfilename(
            title="Select food photo",
            filetypes=[("Image files", "*.jpg *.jpeg *.png")]
        )
        if file_path:
            img = Image.open(file_path)
            img.thumbnail((50, 50))
            photo = ImageTk.PhotoImage(img)
            selected_var = tk.BooleanVar(value=False)
            self.pantry.append({
                "name": file_path.split("/")[-1],
                "expiry": None,
                "photo": photo,
                "selected_var": selected_var
            })
            self.save_pantry_to_csv()
            messagebox.showinfo("Item Scanned", f"Added {self.pantry[-1]['name']} to pantry with image.")
            self.check_expiry_reminders()

    def show_pantry(self):
        if self.pantry_win and tk.Toplevel.winfo_exists(self.pantry_win):
            self.refresh_pantry_contents()
            self.pantry_win.lift()
            return

        self.pantry_win = tk.Toplevel(self.window)
        self.pantry_win.title("Pantry Items")
        self.pantry_win.geometry("650x500")

        self.main_frame = tk.Frame(self.pantry_win)
        self.main_frame.pack(fill="both", expand=True)

        self.canvas = tk.Canvas(self.main_frame)
        self.scrollbar = tk.Scrollbar(self.main_frame, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        btn_frame = tk.Frame(self.pantry_win)
        btn_frame.pack(side="bottom", pady=10, fill="x")

        btn_edit = tk.Button(btn_frame, text="Edit Selected", command=self.edit_selected)
        btn_edit.pack(side="left", padx=10)

        btn_add = tk.Button(btn_frame, text="Add Item", command=self.add_item)
        btn_add.pack(side="left", padx=10)

        btn_delete = tk.Button(btn_frame, text="Delete Selected", command=self.delete_selected)
        btn_delete.pack(side="left", padx=10)

        self.refresh_pantry_contents()
        self.check_expiry_reminders()
        self.show_expired_warning()

    def refresh_pantry_contents(self):
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

        if len(self.pantry) == 0:
            empty_lbl = tk.Label(self.scrollable_frame, text="Pantry is empty. Add items below.", pady=10)
            empty_lbl.pack()
            return

        for item in self.pantry:
            frame = tk.Frame(self.scrollable_frame, pady=5)
            frame.pack(fill="x", padx=5)

            checkbox = tk.Checkbutton(frame, variable=item["selected_var"])
            checkbox.pack(side="left", padx=5)

            if item["photo"]:
                lbl_img = tk.Label(frame, image=item["photo"])
                lbl_img.pack(side="left", padx=5)

            # Color items: red if expired, green if expiring soon
            color = "black"
            today = datetime.now().date()
            if item["expiry"]:
                if item["expiry"] < today:
                    color = "red"
                elif item["expiry"] <= today + timedelta(days=7):
                    color = "green"

            expiry_str = item["expiry"].strftime(self.account.date_format) if item["expiry"] else "No expiry"
            lbl_text = tk.Label(frame, text=f"{item['name']} , Expiry: {expiry_str}", anchor="w", fg=color)
            lbl_text.pack(side="left")

    def get_selected_indices(self):
        return [i for i, item in enumerate(self.pantry) if item["selected_var"].get()]

    def edit_selected(self):
        indices = self.get_selected_indices()
        if not indices:
            messagebox.showerror("Selection Error", "Please select at least one item to edit.")
            return
        if len(indices) > 1:
            messagebox.showerror("Multiple Selection", "Please select only one item to edit at a time.")
            return
        index = indices[0]
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
            self.pantry[index]["selected_var"].set(False)
            self.save_pantry_to_csv()
            self.refresh_pantry_contents()
            edit_win.destroy()
            self.check_expiry_reminders()
            self.show_expired_warning()

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
            selected_var = tk.BooleanVar(value=False)
            self.pantry.append({"name": name, "expiry": expiry, "photo": None, "selected_var": selected_var})
            self.save_pantry_to_csv()
            self.refresh_pantry_contents()
            add_win.destroy()
            self.check_expiry_reminders()
            self.show_expired_warning()

        tk.Button(add_win, text="Add", command=save_new).pack(pady=10)

    def delete_selected(self):
        indices = sorted(self.get_selected_indices(), reverse=True)
        if not indices:
            messagebox.showerror("Selection Error", "Please select at least one item to delete.")
            return
        confirm = messagebox.askyesno("Confirm Delete", f"Delete {len(indices)} selected item(s)?")
        if not confirm:
            return
        for index in indices:
            del self.pantry[index]
        self.save_pantry_to_csv()
        self.refresh_pantry_contents()
        self.check_expiry_reminders()
        self.show_expired_warning()

    def check_expiry_reminders(self):
        soon = datetime.now().date() + timedelta(days=7)
        expiring_items = []
        for item in self.pantry:
            if item["expiry"]:
                if item["expiry"] < datetime.now().date():
                    self.show_expired_warning()
                    return
                elif item["expiry"] <= soon:
                    expiring_items.append(f"{item['name']} (expires {item['expiry'].strftime(self.account.date_format)})")
        if expiring_items:
            messagebox.showwarning(
                "Expiry Reminder",
                "These items are expiring soon:\n\n" + "\n".join(expiring_items)
            )

    def show_expired_warning(self):
        expired_items = [item for item in self.pantry if item["expiry"] and item["expiry"] < datetime.now().date()]
        if expired_items:
            messagebox.showerror(
                "Expired Items!",
                "The following food items are expired:\n\n" + "\n".join([item["name"] for item in expired_items])
            )

    def save_pantry_to_csv(self):
        with open(CSV_FILE, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(["name", "expiry"])
            for item in self.pantry:
                exp_str = item["expiry"].strftime(self.account.date_format) if item["expiry"] else ""
                writer.writerow([item["name"], exp_str])

    def load_pantry_from_csv(self):
        if not os.path.exists(CSV_FILE):
            return
        with open(CSV_FILE, mode='r', newline='', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                name = row["name"]
                expiry_str = row["expiry"]
                expiry = None
                if expiry_str:
                    try:
                        expiry = datetime.strptime(expiry_str, self.account.date_format).date()
                    except:
                        expiry = None
                selected_var = tk.BooleanVar(value=False)
                # No image loaded from CSV, photo=None
                self.pantry.append({"name": name, "expiry": expiry, "photo": None, "selected_var": selected_var})

    # Placeholder methods for other buttons
    def generate_recipe(self):
        if not self.pantry:
            messagebox.showinfo("Generate Recipe", "Pantry is empty, add some items first.")
            return
        ingredients = ", ".join([i["name"] for i in self.pantry])
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
                self.account_win.destroy()

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
                entry_current = tk.Entry(cp_win, show="*")
                entry_current.pack(pady=2)

                tk.Label(cp_win, text="New Password:").pack(pady=2)
                entry_new = tk.Entry(cp_win, show="*")
                entry_new.pack(pady=2)

                tk.Label(cp_win, text="Confirm New Password:").pack(pady=2)
                entry_confirm = tk.Entry(cp_win, show="*")
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

        info_str = (
            f"Name: {self.account.username}\n"
            f"Age: {self.account.age}\n"
            f"Gender: {self.account.gender}\n"
            f"Date Format: {self.account.date_format}"
        )
        tk.Label(self.account_win, text=info_str).pack(pady=10)

        tk.Button(self.account_win, text="Edit Personal Info", command=edit_personal_info).pack(pady=5)
        tk.Button(self.account_win, text="Settings", command=settings).pack(pady=5)

    def sign_out(self):
        self.window.destroy()
        root = tk.Tk()
        LoginApp(root)
        root.mainloop()


if __name__ == "__main__":
    root = tk.Tk()
    login_app = LoginApp(root)
    root.mainloop()