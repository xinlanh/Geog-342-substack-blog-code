import tkinter as tk
from tkinter import messagebox, filedialog
from PIL import Image, ImageTk
from datetime import datetime, timedelta
import csv
import os

CSV_FILE = "foodapp_infosheet.csv"

# Woodsy colors
BG_COLOR = "#D2B48C"           # Tan Brown Background
BTN_COLOR = "#8B5E3C"          # Dark Brown Button
PANTRY_BG_COLOR = "#FFF8DC"    # Warm White / Light Yellow Pantry Background
PANTRY_ITEM_COLORS = {         # Text colors based on expiry
    "expired": "red",
    "warning": "green",
    "normal": "black"
}

DEFAULT_AVATAR_PATH = "default_avatar.png"  # Should be a woodsy style avatar image file


class Account:
    def __init__(self, username, age, password, gender="Fruit", date_format="%Y-%m-%d", profile_pic_path=None):
        self.username = username
        self.age = age
        self.password = password
        self.gender = gender
        self.date_format = date_format
        self.profile_pic_path = profile_pic_path
        self.profile_photo = None  # Loaded PhotoImage object


class LoginApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Food Tracker")
        self.root.geometry("300x220")
        self.root.configure(bg=BG_COLOR)

        self.accounts = {}  # username -> Account
        self.pantry_data = []
        self.friend_data = {}  # key=username, value=set(friend_usernames)
        self.sent_requests = {}  # key=username, value=set(sent usernames)
        self.received_requests = {}  # key=username, value=set(received usernames)

        # Add initial example account
        self.accounts["Apple"] = Account("Apple", "1 week", "Orange")

        self.frame = tk.Frame(root, bg=BG_COLOR)
        self.frame.pack(pady=10)

        lbl = tk.Label(self.frame, text="Username:", bg=BG_COLOR)
        lbl.pack()
        self.entry_username = tk.Entry(self.frame)
        self.entry_username.pack()

        lbl = tk.Label(self.frame, text="Password:", bg=BG_COLOR)
        lbl.pack()
        self.entry_password = tk.Entry(self.frame, show="*")
        self.entry_password.pack()

        self.btn_login = tk.Button(self.frame, text="Login", bg=BTN_COLOR, fg="white", command=self.check_login)
        self.btn_login.pack(pady=5)

        self.btn_create = tk.Button(self.frame, text="Create Account", bg=BTN_COLOR, fg="white", command=self.create_account)
        self.btn_create.pack()

        self.load_data_from_csv()  # Load on startup

    def check_login(self):
        user = self.entry_username.get()
        pwd = self.entry_password.get()
        account = self.accounts.get(user)
        if account and account.password == pwd:
            messagebox.showinfo("Login Success", f"Welcome {user}!")
            self.root.destroy()
            MainApp(account, self.accounts, self.pantry_data, self.friend_data, self.sent_requests, self.received_requests)
        else:
            messagebox.showerror("Login Failed", "Invalid username or password")

    def create_account(self):
        create_win = tk.Toplevel(self.root)
        create_win.title("Create Account")
        create_win.geometry("300x260")
        create_win.configure(bg=BG_COLOR)

        tk.Label(create_win, text="Username:", bg=BG_COLOR).pack(pady=2)
        entry_user = tk.Entry(create_win)
        entry_user.pack(pady=2)

        tk.Label(create_win, text="Age:", bg=BG_COLOR).pack(pady=2)
        entry_age = tk.Entry(create_win)
        entry_age.pack(pady=2)

        tk.Label(create_win, text="Password:", bg=BG_COLOR).pack(pady=2)
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
            # New account with no profile picture yet
            self.accounts[username] = Account(username, age, password)
            # Make sure friends and requests structures ready
            self.friend_data[username] = set()
            self.sent_requests[username] = set()
            self.received_requests[username] = set()
            messagebox.showinfo("Success", f"Account created for {username}. Please login.")
            self.save_data_to_csv()
            create_win.destroy()

        tk.Button(create_win, text="Create", bg=BTN_COLOR, fg="white", command=save_new_account).pack(pady=10)

    def load_data_from_csv(self):
        self.pantry_data = []
        self.friend_data = {}
        self.sent_requests = {}
        self.received_requests = {}

        if not os.path.exists(CSV_FILE):
            return
        try:
            with open(CSV_FILE, newline='', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    rtype = row['type']
                    if rtype == 'account':
                        username = row['username']
                        age = row['age']
                        password = row['password']
                        gender = row.get('gender', 'Fruit')
                        date_format = row.get('date_format', "%Y-%m-%d")
                        profile_pic_path = row.get('profile_pic_path') or None
                        if username not in self.accounts:
                            self.accounts[username] = Account(username, age, password, gender, date_format, profile_pic_path)
                        # Init friend/request containers if absent
                        if username not in self.friend_data:
                            self.friend_data[username] = set()
                        if username not in self.sent_requests:
                            self.sent_requests[username] = set()
                        if username not in self.received_requests:
                            self.received_requests[username] = set()
                    elif rtype == 'pantry':
                        expiry = None
                        if row['expiry']:
                            try:
                                expiry = datetime.strptime(row['expiry'], "%Y-%m-%d").date()
                            except:
                                expiry = None
                        self.pantry_data.append({
                            "username": row['username'],  # associate pantry item with a user
                            "name": row['name'],
                            "expiry": expiry,
                            "photo_path": row['photo_path'],
                        })
                    elif rtype == 'friend':
                        user = row['username']
                        friend = row['friend_username']
                        if user and friend:
                            if user not in self.friend_data:
                                self.friend_data[user] = set()
                            self.friend_data[user].add(friend)
                    elif rtype == 'sent_request':
                        user = row['username']
                        to_user = row['to_username']
                        if user and to_user:
                            if user not in self.sent_requests:
                                self.sent_requests[user] = set()
                            self.sent_requests[user].add(to_user)
                    elif rtype == 'received_request':
                        user = row['username']
                        from_user = row['from_username']
                        if user and from_user:
                            if user not in self.received_requests:
                                self.received_requests[user] = set()
                            self.received_requests[user].add(from_user)
        except Exception as e:
            print(f"Error loading CSV: {e}")

    def save_data_to_csv(self):
        try:
            with open(CSV_FILE, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = [
                    'type', 'username', 'age', 'password', 'gender', 'date_format', 'profile_pic_path',
                    'name', 'expiry', 'photo_path',
                    'friend_username', 'to_username', 'from_username'
                ]
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                for user, acc in self.accounts.items():
                    writer.writerow({
                        'type': 'account',
                        'username': acc.username,
                        'age': acc.age,
                        'password': acc.password,
                        'gender': acc.gender,
                        'date_format': acc.date_format,
                        'profile_pic_path': acc.profile_pic_path or '',
                        'name': '',
                        'expiry': '',
                        'photo_path': '',
                        'friend_username': '',
                        'to_username': '',
                        'from_username': '',
                    })
                for item in self.pantry_data:
                    writer.writerow({
                        'type': 'pantry',
                        'username': item.get('username', ''),
                        'age': '',
                        'password': '',
                        'gender': '',
                        'date_format': '',
                        'profile_pic_path': '',
                        'name': item["name"],
                        'expiry': item['expiry'].strftime("%Y-%m-%d") if item['expiry'] else '',
                        'photo_path': item['photo_path'] if item['photo_path'] else '',
                        'friend_username': '',
                        'to_username': '',
                        'from_username': '',
                    })
                for user, friends in self.friend_data.items():
                    for friend in friends:
                        writer.writerow({
                            'type': 'friend',
                            'username': user,
                            'friend_username': friend,
                            'age': '', 'password': '', 'gender': '', 'date_format': '', 'profile_pic_path': '',
                            'name': '', 'expiry': '', 'photo_path': '', 'to_username': '', 'from_username': '',
                        })
                for user, tos in self.sent_requests.items():
                    for to_user in tos:
                        writer.writerow({
                            'type': 'sent_request',
                            'username': user,
                            'to_username': to_user,
                            'age': '', 'password': '', 'gender': '', 'date_format': '', 'profile_pic_path': '',
                            'name': '', 'expiry': '', 'photo_path': '', 'friend_username': '', 'from_username': '',
                        })
                for user, froms in self.received_requests.items():
                    for from_user in froms:
                        writer.writerow({
                            'type': 'received_request',
                            'username': user,
                            'from_username': from_user,
                            'age': '', 'password': '', 'gender': '', 'date_format': '', 'profile_pic_path': '',
                            'name': '', 'expiry': '', 'photo_path': '', 'friend_username': '', 'to_username': '',
                        })
        except Exception as e:
            print(f"Error saving CSV: {e}")


class MainApp:
    def __init__(self, account, accounts, pantry_data, friend_data, sent_requests, received_requests):
        self.account = account
        self.accounts = accounts
        self.pantry_data = pantry_data
        self.friend_data = friend_data
        self.sent_requests = sent_requests
        self.received_requests = received_requests

        self.pantry = []  # Current user's pantry items as dict with loaded images

        # Main window
        self.window = tk.Tk()
        self.window.title("Food Tracker Main Menu")
        self.window.geometry("650x500")
        self.window.configure(bg=BG_COLOR)

        # Load user's pantry items & photos
        self.load_user_pantry()

        # Load profile photos for all accounts with caching
        self.load_all_profile_photos()

        # Buttons
        btn_scan = tk.Button(self.window, text="Scan Item", width=20, bg=BTN_COLOR, fg="white", command=self.scan_item)
        btn_pantry = tk.Button(self.window, text="Pantry", width=20, bg=BTN_COLOR, fg="white", command=self.show_pantry)
        btn_recipe = tk.Button(self.window, text="Generate Recipe", width=20, bg=BTN_COLOR, fg="white", command=self.generate_recipe)
        btn_cameras = tk.Button(self.window, text="Cameras", width=20, bg=BTN_COLOR, fg="white", command=self.cameras)
        btn_friends = tk.Button(self.window, text="Friends", width=20, bg=BTN_COLOR, fg="white", command=self.show_friends)
        btn_account = tk.Button(self.window, text="Account", width=20, bg=BTN_COLOR, fg="white", command=self.show_account)
        btn_signout = tk.Button(self.window, text="Sign Out", width=20, bg=BTN_COLOR, fg="white", command=self.sign_out)

        btn_scan.pack(pady=5)
        btn_pantry.pack(pady=5)
        btn_recipe.pack(pady=5)
        btn_cameras.pack(pady=5)
        btn_friends.pack(pady=5)
        btn_account.pack(pady=5)
        btn_signout.pack(pady=5)

        self.pantry_win = None
        self.friends_win = None

        self.window.mainloop()

    def load_user_pantry(self):
        self.pantry.clear()
        for item in self.pantry_data:
            if item.get("username") == self.account.username:
                photo = None
                if item.get("photo_path") and os.path.exists(item["photo_path"]):
                    try:
                        img = Image.open(item["photo_path"])
                        img.thumbnail((50, 50))
                        photo = ImageTk.PhotoImage(img)
                    except:
                        photo = None
                selected_var = tk.BooleanVar(value=False)
                self.pantry.append({
                    "name": item["name"],
                    "expiry": item["expiry"],
                    "photo": photo,
                    "photo_path": item.get("photo_path"),
                    "selected_var": selected_var
                })

    def load_all_profile_photos(self):
        # Load default avatar image once
        try:
            if os.path.exists(DEFAULT_AVATAR_PATH):
                img = Image.open(DEFAULT_AVATAR_PATH)
                img.thumbnail((100, 100))
                default_avatar = ImageTk.PhotoImage(img)
            else:
                default_avatar = None
        except:
            default_avatar = None
        for acc in self.accounts.values():
            acc.profile_photo = None
            if acc.profile_pic_path and os.path.exists(acc.profile_pic_path):
                try:
                    img = Image.open(acc.profile_pic_path)
                    img.thumbnail((100, 100))
                    acc.profile_photo = ImageTk.PhotoImage(img)
                except:
                    acc.profile_photo = default_avatar
            else:
                acc.profile_photo = default_avatar

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
            item_name = file_path.split("/")[-1]
            new_item = {
                "name": item_name,
                "expiry": None,
                "photo": photo,
                "photo_path": file_path,
                "selected_var": selected_var
            }
            self.pantry.append(new_item)
            self.pantry_data.append({
                "username": self.account.username,
                "name": item_name,
                "expiry": None,
                "photo_path": file_path
            })
            self.save_all_to_csv()
            messagebox.showinfo("Item Scanned", f"Added {item_name} to pantry with image.")
            self.check_expiry_reminders()

    def show_pantry(self):
        if self.pantry_win and tk.Toplevel.winfo_exists(self.pantry_win):
            self.refresh_pantry_contents()
            self.pantry_win.lift()
            return

        self.pantry_win = tk.Toplevel(self.window)
        self.pantry_win.title("Pantry Items")
        self.pantry_win.geometry("650x500")
        self.pantry_win.configure(bg=PANTRY_BG_COLOR)

        self.main_frame = tk.Frame(self.pantry_win, bg=PANTRY_BG_COLOR)
        self.main_frame.pack(fill="both", expand=True)

        self.canvas = tk.Canvas(self.main_frame, bg=PANTRY_BG_COLOR)
        self.scrollbar = tk.Scrollbar(self.main_frame, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas, bg=PANTRY_BG_COLOR)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        # Bottom button panel with soft brown background
        btn_frame = tk.Frame(self.pantry_win, bg=BG_COLOR)
        btn_frame.pack(side="bottom", pady=10, fill="x")

        btn_edit = tk.Button(btn_frame, text="Edit Selected", bg=BTN_COLOR, fg="white", command=self.edit_selected)
        btn_add = tk.Button(btn_frame, text="Add Item", bg=BTN_COLOR, fg="white", command=self.add_item)
        btn_delete = tk.Button(btn_frame, text="Delete Selected", bg=BTN_COLOR, fg="white", command=self.delete_selected)

        btn_edit.pack(side="left", padx=10)
        btn_add.pack(side="left", padx=10)
        btn_delete.pack(side="left", padx=10)

        self.refresh_pantry_contents()
        self.check_expiry_reminders()
        self.show_expired_warning()

    def refresh_pantry_contents(self):
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

        if len(self.pantry) == 0:
            empty_lbl = tk.Label(self.scrollable_frame, text="Pantry is empty. Add items below.", pady=10, bg=PANTRY_BG_COLOR)
            empty_lbl.pack()
            return

        for item in self.pantry:
            frame = tk.Frame(self.scrollable_frame, pady=5, bg=PANTRY_BG_COLOR)
            frame.pack(fill="x", padx=5)

            checkbox = tk.Checkbutton(frame, variable=item["selected_var"], bg=PANTRY_BG_COLOR)
            checkbox.pack(side="left", padx=5)

            if item["photo"]:
                lbl_img = tk.Label(frame, image=item["photo"], bg=PANTRY_BG_COLOR)
                lbl_img.pack(side="left", padx=5)

            color = PANTRY_ITEM_COLORS["normal"]
            today = datetime.now().date()
            if item["expiry"]:
                if item["expiry"] < today:
                    color = PANTRY_ITEM_COLORS["expired"]
                elif item["expiry"] <= today + timedelta(days=7):
                    color = PANTRY_ITEM_COLORS["warning"]

            expiry_str = item["expiry"].strftime(self.account.date_format) if item["expiry"] else "No expiry"
            lbl_text = tk.Label(frame, text=f"{item['name']} , Expiry: {expiry_str}", anchor="w", fg=color, bg=PANTRY_BG_COLOR)
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

            # Update pantry item and pantry_data for CSV saving
            orig_name = item["name"]
            self.pantry[index]["name"] = new_name
            self.pantry[index]["expiry"] = new_expiry
            self.pantry[index]["selected_var"].set(False)

            # Update pantry_data (only for this user) for matching name & photo_path
            for pdata in self.pantry_data:
                if pdata["name"] == orig_name and pdata.get("username") == self.account.username:
                    pdata["name"] = new_name
                    pdata["expiry"] = new_expiry
                    break

            self.save_all_to_csv()
            self.refresh_pantry_contents()
            edit_win.destroy()
            self.check_expiry_reminders()
            self.show_expired_warning()

        tk.Button(edit_win, text="Save", bg=BTN_COLOR, fg="white", command=save_changes).pack(pady=10)

    def add_item(self):
        add_win = tk.Toplevel(self.pantry_win)
        add_win.title("Add Pantry Item")
        add_win.geometry("300x190")
        add_win.configure(bg=PANTRY_BG_COLOR)

        tk.Label(add_win, text="Name:", bg=PANTRY_BG_COLOR).pack(pady=5)
        entry_name = tk.Entry(add_win)
        entry_name.pack()

        tk.Label(add_win, text=f"Expiry Date ({self.account.date_format}):", bg=PANTRY_BG_COLOR).pack(pady=5)
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
            item = {"name": name, "expiry": expiry, "photo": None, "selected_var": selected_var}
            self.pantry.append(item)
            self.pantry_data.append({"username": self.account.username, "name": name, "expiry": expiry, "photo_path": None})
            self.save_all_to_csv()
            self.refresh_pantry_contents()
            add_win.destroy()
            self.check_expiry_reminders()
            self.show_expired_warning()

        tk.Button(add_win, text="Add", bg=BTN_COLOR, fg="white", command=save_new).pack(pady=10)

    def delete_selected(self):
        indices = sorted(self.get_selected_indices(), reverse=True)
        if not indices:
            messagebox.showerror("Selection Error", "Please select at least one item to delete.")
            return
        confirm = messagebox.askyesno("Confirm Delete", f"Delete {len(indices)} selected item(s)?")
        if not confirm:
            return
        removed_names = []
        for index in indices:
            removed_names.append(self.pantry[index]["name"])
            del self.pantry[index]
        # Remove from pantry_data filtered by username and name
        self.pantry_data = [item for item in self.pantry_data if not (item["username"] == self.account.username and item["name"] in removed_names)]

        self.save_all_to_csv()
        self.refresh_pantry_contents()
        self.check_expiry_reminders()
        self.show_expired_warning()

    def check_expiry_reminders(self):
        soon = datetime.now().date() + timedelta(days=7)
        expiring_items = []
        for item in self.pantry:
            if item["expiry"] and item["expiry"] <= soon:
                if item["expiry"] >= datetime.now().date():
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

    def save_all_to_csv(self):
        try:
            with open(CSV_FILE, "w", newline="", encoding="utf-8") as csvfile:
                fieldnames = [
                    "type", "username", "age", "password", "gender", "date_format", "profile_pic_path",
                    "name", "expiry", "photo_path",
                    "friend_username", "to_username", "from_username"
                ]
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                for user, acc in self.accounts.items():
                    writer.writerow({
                        "type": "account",
                        "username": acc.username,
                        "age": acc.age,
                        "password": acc.password,
                        "gender": acc.gender,
                        "date_format": acc.date_format,
                        "profile_pic_path": acc.profile_pic_path or '',
                        "name": "",
                        "expiry": "",
                        "photo_path": "",
                        "friend_username": "",
                        "to_username": "",
                        "from_username": "",
                    })
                for item in self.pantry_data:
                    writer.writerow({
                        "type": "pantry",
                        "username": item.get("username", ""),
                        "age": "",
                        "password": "",
                        "gender": "",
                        "date_format": "",
                        "profile_pic_path": "",
                        "name": item["name"],
                        "expiry": item["expiry"].strftime("%Y-%m-%d") if item["expiry"] else "",
                        "photo_path": item["photo_path"] if item["photo_path"] else "",
                        "friend_username": "",
                        "to_username": "",
                        "from_username": "",
                    })
                for user, friends in self.friend_data.items():
                    for friend in friends:
                        writer.writerow({
                            "type": "friend",
                            "username": user,
                            "friend_username": friend,
                            "age": "", "password": "", "gender": "", "date_format": "", "profile_pic_path": "",
                            "name": "", "expiry": "", "photo_path": "", "to_username": "", "from_username": "",
                        })
                for user, tos in self.sent_requests.items():
                    for to_user in tos:
                        writer.writerow({
                            'type': 'sent_request',
                            'username': user,
                            'to_username': to_user,
                            'age': '', 'password': '', 'gender': '', 'date_format': '', 'profile_pic_path': '',
                            'name': '', 'expiry': '', 'photo_path': '', 'friend_username': '', 'from_username': '',
                        })
                for user, froms in self.received_requests.items():
                    for from_user in froms:
                        writer.writerow({
                            'type': 'received_request',
                            'username': user,
                            'from_username': from_user,
                            'age': '', 'password': '', 'gender': '', 'date_format': '', 'profile_pic_path': '',
                            'name': '', 'expiry': '', 'photo_path': '', 'friend_username': '', 'to_username': '',
                        })
        except Exception as e:
            print(f"Error saving CSV: {e}")

    
    def generate_recipe(self):
        if not self.pantry:
            messagebox.showinfo("Generate Recipe", "Pantry is empty, add some items first.")
            return
        ingredients = ", ".join([i["name"] for i in self.pantry])
        messagebox.showinfo("Recipe Generation", f"Generating recipe using: {ingredients}")

    def cameras(self):
        messagebox.showinfo("Coming Soon", "Cameras feature will be added later.")

    # FRIENDS FEATURE
    def show_friends(self):
        if self.friends_win and tk.Toplevel.winfo_exists(self.friends_win):
            self.friends_win.lift()
            return

        self.friends_win = tk.Toplevel(self.window)
        self.friends_win.title("Friends")
        self.friends_win.geometry("900x500")
        self.friends_win.configure(bg=BG_COLOR)

        # Header with "Add Friend" button
        header_frame = tk.Frame(self.friends_win, bg=BG_COLOR)
        header_frame.pack(fill="x", pady=5)
        tk.Label(header_frame, text="Friends", font=("Arial", 16), bg=BG_COLOR).pack(side="left", padx=10)
        tk.Button(header_frame, text="Add Friend", bg=BTN_COLOR, fg="white", command=self.open_add_friend_window).pack(side="right", padx=10)

        # Left side: Friends list with scrollbar
        friend_list_frame = tk.Frame(self.friends_win, bg=BG_COLOR)
        friend_list_frame.pack(side="left", fill="y", padx=10, pady=10)

        self.friend_listbox = tk.Listbox(friend_list_frame, height=25, width=30)
        self.friend_listbox.pack(side="left", fill="y")
        friend_scrollbar = tk.Scrollbar(friend_list_frame, orient="vertical", command=self.friend_listbox.yview)
        friend_scrollbar.pack(side="left", fill="y")
        self.friend_listbox.config(yscrollcommand=friend_scrollbar.set)
        self.friend_listbox.bind('<<ListboxSelect>>', self.on_friend_selected)
        self.refresh_friend_list()

        # Middle: Friend profile picture and pantry
        self.friend_info_frame = tk.Frame(self.friends_win, bg=PANTRY_BG_COLOR, relief="sunken", bd=2)
        self.friend_info_frame.pack(side="left", fill="both", expand=True, padx=10, pady=10)

        self.friend_profile_pic_label = tk.Label(self.friend_info_frame, bg=PANTRY_BG_COLOR)
        self.friend_profile_pic_label.pack(pady=10)

        self.friend_pantry_canvas = tk.Canvas(self.friend_info_frame, bg=PANTRY_BG_COLOR)
        self.friend_pantry_scrollbar = tk.Scrollbar(self.friend_info_frame, orient="vertical", command=self.friend_pantry_canvas.yview)
        self.friend_pantry_scrollable_frame = tk.Frame(self.friend_pantry_canvas, bg=PANTRY_BG_COLOR)

        self.friend_pantry_scrollable_frame.bind(
            "<Configure>",
            lambda e: self.friend_pantry_canvas.configure(scrollregion=self.friend_pantry_canvas.bbox("all"))
        )
        self.friend_pantry_canvas.create_window((0, 0), window=self.friend_pantry_scrollable_frame, anchor="nw")
        self.friend_pantry_canvas.configure(yscrollcommand=self.friend_pantry_scrollbar.set)
        self.friend_pantry_canvas.pack(side="left", fill="both", expand=True)
        self.friend_pantry_scrollbar.pack(side="right", fill="y")

        # Right side: Sent and Received Requests stacked vertically
        requests_frame = tk.Frame(self.friends_win, bg=BG_COLOR, width=300)
        requests_frame.pack(side="left", fill="y", padx=10, pady=10)

        # Sent Requests section
        sent_label = tk.Label(requests_frame, text="Pending Sent Requests", font=("Arial", 12, 'bold'), bg=BG_COLOR)
        sent_label.pack(pady=(0,5))

        sent_frame = tk.Frame(requests_frame)
        sent_frame.pack(pady=3, fill="x")

        self.sent_requests_listbox = tk.Listbox(sent_frame, height=8, width=35)
        self.sent_requests_listbox.pack(side="left", fill="y")

        sent_scrollbar = tk.Scrollbar(sent_frame, orient="vertical", command=self.sent_requests_listbox.yview)
        sent_scrollbar.pack(side="left", fill="y")

        self.sent_requests_listbox.config(yscrollcommand=sent_scrollbar.set)

        self.btn_cancel_sent = tk.Button(requests_frame, text="Cancel Request", bg=BTN_COLOR, fg="white", command=self.cancel_sent_request)
        self.btn_cancel_sent.pack(pady=5, fill="x")

        # Received Requests section
        recv_label = tk.Label(requests_frame, text="Pending Received Requests", font=("Arial", 12, 'bold'), bg=BG_COLOR)
        recv_label.pack(pady=(20,5))

        recv_frame = tk.Frame(requests_frame)
        recv_frame.pack(pady=3, fill="x")

        self.recv_requests_listbox = tk.Listbox(recv_frame, height=8, width=35)
        self.recv_requests_listbox.pack(side="left", fill="y")

        recv_scrollbar = tk.Scrollbar(recv_frame, orient="vertical", command=self.recv_requests_listbox.yview)
        recv_scrollbar.pack(side="left", fill="y")

        self.recv_requests_listbox.config(yscrollcommand=recv_scrollbar.set)

        btn_accept = tk.Button(requests_frame, text="Accept Request", bg=BTN_COLOR, fg="white", command=self.accept_friend_request)
        btn_decline = tk.Button(requests_frame, text="Decline Request", bg=BTN_COLOR, fg="white", command=self.decline_friend_request)
        btn_accept.pack(pady=5, fill="x")
        btn_decline.pack(pady=5, fill="x")


        self.refresh_requests_lists()


    def refresh_friend_list(self):
        self.friend_listbox.delete(0, tk.END)
        friends = sorted(self.friend_data.get(self.account.username, []))
        for friend in friends:
            self.friend_listbox.insert(tk.END, friend)

    def refresh_requests_lists(self):
        self.sent_requests_listbox.delete(0, tk.END)
        sent = sorted(self.sent_requests.get(self.account.username, []))
        for user in sent:
            self.sent_requests_listbox.insert(tk.END, user)

        self.recv_requests_listbox.delete(0, tk.END)
        received = sorted(self.received_requests.get(self.account.username, []))
        for user in received:
            self.recv_requests_listbox.insert(tk.END, user)


    def cancel_sent_request(self):
        sel = self.sent_requests_listbox.curselection()
        if not sel:
            messagebox.showerror("Error", "No sent request selected")
            return
        to_user = self.sent_requests_listbox.get(sel[0])
        self.sent_requests[self.account.username].remove(to_user)
        if to_user in self.received_requests:
            self.received_requests[to_user].discard(self.account.username)
        self.save_all_to_csv()
        self.refresh_requests_lists()

    def accept_friend_request(self):
        sel = self.recv_requests_listbox.curselection()
        if not sel:
            messagebox.showerror("Error", "No received request selected")
            return
        from_user = self.recv_requests_listbox.get(sel[0])
        # Add both ways friendship
        self.friend_data.setdefault(self.account.username, set()).add(from_user)
        self.friend_data.setdefault(from_user, set()).add(self.account.username)
        # Remove requests
        self.received_requests[self.account.username].remove(from_user)
        self.sent_requests[from_user].remove(self.account.username)
        self.save_all_to_csv()
        self.refresh_friend_list()
        self.refresh_requests_lists()

    def decline_friend_request(self):
        sel = self.recv_requests_listbox.curselection()
        if not sel:
            messagebox.showerror("Error", "No received request selected")
            return
        from_user = self.recv_requests_listbox.get(sel[0])
        # Just remove requests, no friendship
        self.received_requests[self.account.username].remove(from_user)
        self.sent_requests[from_user].remove(self.account.username)
        self.save_all_to_csv()
        self.refresh_requests_lists()

    def open_add_friend_window(self):
        add_win = tk.Toplevel(self.friends_win)
        add_win.title("Add Friend")
        add_win.geometry("350x150")
        add_win.configure(bg=BG_COLOR)

        tk.Label(add_win, text="Search Username:", bg=BG_COLOR).pack(pady=5)
        entry_search = tk.Entry(add_win)
        entry_search.pack(pady=5)

        lbl_info = tk.Label(add_win, text="", bg=BG_COLOR)
        lbl_info.pack(pady=5)

        def search_and_send():
            target = entry_search.get().strip()
            if not target:
                messagebox.showerror("Error", "Enter a username to search")
                return
            if target == self.account.username:
                messagebox.showerror("Error", "You cannot friend yourself")
                return
            if target not in self.accounts:
                messagebox.showerror("Error", f"User '{target}' not found")
                return
            # Check already friends
            if target in self.friend_data.get(self.account.username, set()):
                messagebox.showinfo("Info", f"You are already friends with '{target}'")
                return
            # Check existing requests
            sent = self.sent_requests.get(self.account.username, set())
            received = self.received_requests.get(self.account.username, set())
            if target in sent:
                messagebox.showinfo("Info", f"Friend request already sent to '{target}'")
                return
            if target in received:
                messagebox.showinfo("Info", f"User '{target}' has already sent you a request, accept it in received requests")
                return
            # Send friend request
            self.sent_requests.setdefault(self.account.username, set()).add(target)
            self.received_requests.setdefault(target, set()).add(self.account.username)
            self.save_all_to_csv()
            messagebox.showinfo("Success", f"Friend request sent to '{target}'")
            add_win.destroy()
            self.refresh_requests_lists()

        btn_search = tk.Button(add_win, text="Send Friend Request", bg=BTN_COLOR, fg="white", command=search_and_send)
        btn_search.pack(pady=5)

    def on_friend_selected(self, event):
        selection = event.widget.curselection()
        if not selection:
            return
        friend_name = event.widget.get(selection[0])
        friend_acc = self.accounts.get(friend_name)
        if not friend_acc:
            return
        # Show friend's profile image
        photo_label = self.friend_profile_pic_label
        if friend_acc.profile_photo:
            photo_label.configure(image=friend_acc.profile_photo)
            photo_label.image = friend_acc.profile_photo
        else:
            photo_label.configure(image='')
            photo_label.image = None
        # Populate friend's pantry items
        for w in self.friend_pantry_scrollable_frame.winfo_children():
            w.destroy()

        friend_pantry_items = [item for item in self.pantry_data if item.get("username") == friend_name]

        if not friend_pantry_items:
            lbl = tk.Label(self.friend_pantry_scrollable_frame, text="No items in friend's pantry.", bg=PANTRY_BG_COLOR)
            lbl.pack()
            return

        today = datetime.now().date()

        for item in friend_pantry_items:
            frame = tk.Frame(self.friend_pantry_scrollable_frame, pady=5, bg=PANTRY_BG_COLOR)
            frame.pack(fill="x", padx=5)

            photo = None
            if item.get("photo_path") and os.path.exists(item["photo_path"]):
                try:
                    img = Image.open(item["photo_path"])
                    img.thumbnail((50, 50))
                    photo = ImageTk.PhotoImage(img)
                except:
                    photo = None

            if photo:
                lbl_img = tk.Label(frame, image=photo, bg=PANTRY_BG_COLOR)
                lbl_img.photo = photo  # keep reference
                lbl_img.pack(side="left", padx=5)

            color = PANTRY_ITEM_COLORS["normal"]
            expiry = item.get("expiry")
            if expiry:
                if expiry < today:
                    color = PANTRY_ITEM_COLORS["expired"]
                elif expiry <= today + timedelta(days=7):
                    color = PANTRY_ITEM_COLORS["warning"]
            expiry_str = expiry.strftime(friend_acc.date_format) if expiry else "No expiry"
            lbl_text = tk.Label(frame, text=f"{item['name']} , Expiry: {expiry_str}", anchor="w", fg=color, bg=PANTRY_BG_COLOR)
            lbl_text.pack(side="left")

    def show_account(self):
        self.account_win = tk.Toplevel(self.window)
        self.account_win.title("User Account")
        self.account_win.geometry("350x350")
        self.account_win.configure(bg=BG_COLOR)

        def edit_personal_info():
            edit_win = tk.Toplevel(self.account_win)
            edit_win.title("Edit Personal Info")
            edit_win.geometry("300x260")
            edit_win.configure(bg=BG_COLOR)

            tk.Label(edit_win, text="Name:", bg=BG_COLOR).pack(pady=2)
            entry_name = tk.Entry(edit_win)
            entry_name.pack(pady=2)
            entry_name.insert(0, self.account.username)

            tk.Label(edit_win, text="Age:", bg=BG_COLOR).pack(pady=2)
            entry_age = tk.Entry(edit_win)
            entry_age.pack(pady=2)
            entry_age.insert(0, self.account.age)

            tk.Label(edit_win, text="Gender:", bg=BG_COLOR).pack(pady=2)
            entry_gender = tk.Entry(edit_win)
            entry_gender.pack(pady=2)
            entry_gender.insert(0, self.account.gender)

            tk.Label(edit_win, text="Profile Picture:", bg=BG_COLOR).pack(pady=2)
            btn_choose_pic = tk.Button(edit_win, text="Choose Image", bg=BTN_COLOR, fg="white")
            btn_choose_pic.pack(pady=2)

            pic_path_var = tk.StringVar(value=self.account.profile_pic_path or "")

            def choose_pic():
                path = filedialog.askopenfilename(title="Select Profile Picture",
                                                  filetypes=[("Image files", "*.jpg *.jpeg *.png")])
                if path:
                    pic_path_var.set(path)

            btn_choose_pic.config(command=choose_pic)

            def save_info():
                self.account.username = entry_name.get().strip()
                self.account.age = entry_age.get().strip()
                self.account.gender = entry_gender.get().strip()
                self.account.profile_pic_path = pic_path_var.get() or None
                # Reload profile photo
                try:
                    if self.account.profile_pic_path and os.path.exists(self.account.profile_pic_path):
                        img = Image.open(self.account.profile_pic_path)
                        img.thumbnail((100, 100))
                        self.account.profile_photo = ImageTk.PhotoImage(img)
                    else:
                        self.account.profile_photo = None
                except:
                    self.account.profile_photo = None
                messagebox.showinfo("Saved", "Personal info updated.")
                edit_win.destroy()
                self.account_win.destroy()
                # Save to CSV
                self.save_all_to_csv()

            tk.Button(edit_win, text="Save", bg=BTN_COLOR, fg="white", command=save_info).pack(pady=10)

        def settings():
            settings_win = tk.Toplevel(self.account_win)
            settings_win.title("Settings")
            settings_win.geometry("300x220")
            settings_win.configure(bg=BG_COLOR)

            tk.Label(settings_win, text="Date Format (Python strftime format):", bg=BG_COLOR).pack(pady=5)
            entry_date_fmt = tk.Entry(settings_win)
            entry_date_fmt.pack()
            entry_date_fmt.insert(0, self.account.date_format)

            def save_settings():
                fmt = entry_date_fmt.get().strip()
                try:
                    datetime.now().strftime(fmt)
                    self.account.date_format = fmt
                    self.save_all_to_csv()
                    messagebox.showinfo("Success", "Date format updated.")
                    settings_win.destroy()
                except:
                    messagebox.showerror("Error", "Invalid date format string.")

            tk.Button(settings_win, text="Save", command=save_settings, bg=BTN_COLOR, fg="white").pack(pady=10)

            def change_password():
                cp_win = tk.Toplevel(settings_win)
                cp_win.title("Change Password")
                cp_win.geometry("300x180")
                cp_win.configure(bg=BG_COLOR)

                tk.Label(cp_win, text="Current Password:", bg=BG_COLOR).pack(pady=2)
                entry_current = tk.Entry(cp_win, show="*")
                entry_current.pack(pady=2)

                tk.Label(cp_win, text="New Password:", bg=BG_COLOR).pack(pady=2)
                entry_new = tk.Entry(cp_win, show="*")
                entry_new.pack(pady=2)

                tk.Label(cp_win, text="Confirm New Password:", bg=BG_COLOR).pack(pady=2)
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
                    self.save_all_to_csv()
                    messagebox.showinfo("Success", "Password changed successfully.")
                    cp_win.destroy()

                tk.Button(cp_win, text="Save Password", command=save_password, bg=BTN_COLOR, fg="white").pack(pady=10)

            tk.Button(settings_win, text="Change Password", command=change_password, bg=BTN_COLOR, fg="white").pack(pady=10)

        info_str = (
            f"Name: {self.account.username}\n"
            f"Age: {self.account.age}\n"
            f"Gender: {self.account.gender}\n"
            f"Date Format: {self.account.date_format}"
        )
        tk.Label(self.account_win, text=info_str, bg=BG_COLOR).pack(pady=10)

        # Profile Picture display in account window
        img_label = tk.Label(self.account_win, bg=BG_COLOR)
        img_label.pack(pady=10)
        if self.account.profile_photo:
            img_label.config(image=self.account.profile_photo)
            img_label.image = self.account.profile_photo

        tk.Button(self.account_win, text="Edit Personal Info", command=edit_personal_info, bg=BTN_COLOR, fg="white").pack(pady=5)
        tk.Button(self.account_win, text="Settings", command=settings, bg=BTN_COLOR, fg="white").pack(pady=5)

    def sign_out(self):
        self.window.destroy()
        root = tk.Tk()
        LoginApp(root)
        root.mainloop()

if __name__ == "__main__":
    root = tk.Tk()
    login_app = LoginApp(root)
    root.mainloop()