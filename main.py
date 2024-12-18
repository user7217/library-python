import tkinter as tk
from tkinter import messagebox, simpledialog, ttk
from PIL import Image, ImageTk
import json
import os
import urllib.request

# JSON Database Files
user_db_file = "user_db.json"
book_db_file = "book_db.json"

# Initial Database Structure
def initialize_database():
    if not os.path.exists(user_db_file):
        users = {
            "users": {
                "admin": {"password": "admin123"},
                "user1": {"password": "password1"}
            }
        }
        with open(user_db_file, 'w') as f:
            json.dump(users, f, indent=4)

    if not os.path.exists(book_db_file):
        books = {
            "books": [
                {"title": "1984", "author": "George Orwell", "is_available": True, "image": "https://covers.openlibrary.org/b/id/7222246-L.jpg"},
                {"title": "To Kill a Mockingbird", "author": "Harper Lee", "is_available": True, "image": "https://covers.openlibrary.org/b/id/8228691-L.jpg"},
                {"title": "The Great Gatsby", "author": "F. Scott Fitzgerald", "is_available": True, "image": "https://covers.openlibrary.org/b/id/6516725-L.jpg"}
            ]
        }
        with open(book_db_file, 'w') as f:
            json.dump(books, f, indent=4)

# Load JSON Database
def load_database(file):
    with open(file, 'r') as f:
        return json.load(f)

# Save JSON Database
def save_database(data, file):
    with open(file, 'w') as f:
        json.dump(data, f, indent=4)

# Main Library Kiosk Class
class LibraryKiosk:
    def __init__(self, root):
        self.root = root
        self.root.title("Library Kiosk System")
        self.current_user = None
        
        # Login Frame
        self.login_frame = tk.Frame(root)
        self.login_frame.pack(pady=50)

        tk.Label(self.login_frame, text="Library Kiosk Login", font=("Helvetica", 16)).pack(pady=10)
        tk.Label(self.login_frame, text="Username:").pack()
        self.username_entry = tk.Entry(self.login_frame)
        self.username_entry.pack()
        
        tk.Label(self.login_frame, text="Password:").pack()
        self.password_entry = tk.Entry(self.login_frame, show="*")
        self.password_entry.pack()
        
        tk.Button(self.login_frame, text="Login", command=self.login).pack(pady=10)

    def login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        
        db = load_database(user_db_file)
        
        if username in db["users"] and db["users"][username]["password"] == password:
            self.current_user = username
            messagebox.showinfo("Success", f"Welcome, {username}!")
            self.show_main_menu()
        else:
            messagebox.showerror("Error", "Invalid username or password")

    def show_main_menu(self):
        self.login_frame.destroy()
        
        self.main_frame = tk.Frame(self.root)
        self.main_frame.pack(pady=50)

        tk.Label(self.main_frame, text=f"Welcome, {self.current_user}!", font=("Helvetica", 16)).pack(pady=10)
        tk.Button(self.main_frame, text="View Books", command=self.view_books).pack(pady=5)
        tk.Button(self.main_frame, text="Borrow Book", command=self.borrow_book).pack(pady=5)
        tk.Button(self.main_frame, text="Return Book", command=self.return_book).pack(pady=5)
        tk.Button(self.main_frame, text="Logout", command=self.logout).pack(pady=5)

    def view_books(self):
        db = load_database(book_db_file)
        books = db["books"]
        
        self.main_frame.destroy()
        self.books_frame = tk.Frame(self.root)
        self.books_frame.pack(pady=20)

        tk.Label(self.books_frame, text="Library Books", font=("Helvetica", 16)).pack(pady=10)
        
        canvas = tk.Canvas(self.books_frame)
        scrollbar = ttk.Scrollbar(self.books_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(
                scrollregion=canvas.bbox("all")
            )
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        for book in books:
            frame = tk.Frame(scrollable_frame, borderwidth=2, relief="groove")
            frame.pack(pady=10, padx=10, fill="x")

            try:
                image_url = book.get("image", "")
                image_file = f"temp_{book['title'].replace(' ', '_')}.jpg"
                urllib.request.urlretrieve(image_url, image_file)
                img = Image.open(image_file)
                img = img.resize((100, 150))
                photo = ImageTk.PhotoImage(img)
            except Exception as e:
                photo = None

            if photo:
                image_label = tk.Label(frame, image=photo)
                image_label.image = photo
                image_label.pack(side="left", padx=10)
            
            text = f"Title: {book['title']}\nAuthor: {book['author']}\nStatus: {'Available' if book['is_available'] else 'Borrowed'}"
            tk.Label(frame, text=text, justify="left", anchor="w").pack(side="left", padx=10)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        tk.Button(self.books_frame, text="Back", command=self.show_main_menu).pack(pady=10)

    def borrow_book(self):
        db = load_database(book_db_file)
        books = db["books"]
        
        available_books = [book for book in books if book["is_available"]]
        if not available_books:
            messagebox.showinfo("No Books", "No books are currently available for borrowing.")
            return

        book_titles = [book['title'] for book in available_books]
        book_to_borrow = simpledialog.askstring("Borrow Book", f"Available Books:\n{chr(10).join(book_titles)}\n\nEnter book title to borrow:")

        if book_to_borrow:
            for book in books:
                if book['title'].lower() == book_to_borrow.lower() and book["is_available"]:
                    book["is_available"] = False
                    save_database({"books": books}, book_db_file)
                    messagebox.showinfo("Success", f"You borrowed '{book['title']}'!")
                    return
            messagebox.showerror("Error", "Book not found or already borrowed.")

    def return_book(self):
        db = load_database(book_db_file)
        books = db["books"]
        
        borrowed_books = [book for book in books if not book["is_available"]]
        if not borrowed_books:
            messagebox.showinfo("No Books", "No books are currently borrowed.")
            return

        book_titles = [book['title'] for book in borrowed_books]
        book_to_return = simpledialog.askstring("Return Book", f"Borrowed Books:\n{chr(10).join(book_titles)}\n\nEnter book title to return:")

        if book_to_return:
            for book in books:
                if book['title'].lower() == book_to_return.lower() and not book["is_available"]:
                    book["is_available"] = True
                    save_database({"books": books}, book_db_file)
                    messagebox.showinfo("Success", f"You returned '{book['title']}'!")
                    return
            messagebox.showerror("Error", "Book not found or already available.")

    def logout(self):
        self.books_frame.destroy()
        self.__init__(self.root)

# Main Function
if __name__ == "__main__":
    initialize_database()
    root = tk.Tk()
    app = LibraryKiosk(root)
    root.mainloop()
