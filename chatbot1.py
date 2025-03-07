import tkinter as tk
from tkinter import messagebox
import mysql.connector
import speech_recognition as sr
from gtts import gTTS
import os

# Database Configuration
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "aditya",
    "database": "books_db"
}

# Questions flow
chatbotFlow = [
    {"question": "Are you looking for a specific book?", "options": ["Sure", "No"]},
    {"question": "What genre are you interested in?", "options": ["Fiction", "Mystery", "Fantasy", "Sci-Fi", "Biography", "No Preference"]},
    {"question": "What is your minimum rating preference?", "options": ["Above 4.5", "Above 4", "Above 3.5", "No Preference"]},
    {"question": "What price range are you looking for?", "options": ["Under 500", "500 to 1000", "Above 1000", "No Preference"]},
]

class ChatbotApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Book Finder Chatbot")
        self.root.geometry("500x600")
        self.root.configure(bg="#1a1a1a")
        
        self.step = 0
        self.responses = {}
        self.search_entries = {}
        self.selected_book = None
        
        self.create_widgets()
        self.display_question()
    
    def create_widgets(self):
        self.chat_frame = tk.Frame(self.root, bg="#2a2a2a", padx=20, pady=20)
        self.chat_frame.pack(pady=20, padx=20, fill="both", expand=True)
        
        self.chat_label = tk.Label(self.chat_frame, text="", font=("Arial", 14), fg="white", bg="#2a2a2a", wraplength=450, justify="left")
        self.chat_label.pack(anchor="w")
        
        self.button_frame = tk.Frame(self.root, bg="#1a1a1a")
        self.button_frame.pack(fill="x")
    
    def speak(self, text):
        tts = gTTS(text=text, lang='en')
        tts.save("output.mp3")
        os.system("start output.mp3" if os.name == "nt" else "mpg321 output.mp3")

    def listen(self):
        recognizer = sr.Recognizer()
        with sr.Microphone() as source:
            self.chat_label.config(text="🎤 Listening...")
            self.root.update()
            try:
                audio = recognizer.listen(source, timeout=5)
                response = recognizer.recognize_google(audio).strip().lower()
                return response
            except sr.UnknownValueError:
                return ""
            except sr.RequestError:
                return "ERROR"
    
    def display_question(self):
        question = chatbotFlow[self.step]["question"]
        self.chat_label.config(text=question)
        self.speak(question)
        self.clear_widgets()
        
        for option in chatbotFlow[self.step].get("options", []):
            btn = tk.Button(self.button_frame, text=option, command=lambda o=option: self.handle_select(o.lower()), bg="#4a4a4a", fg="white", font=("Arial", 12), padx=10, pady=5)
            btn.pack(fill="x", pady=5)
        
        voice_btn = tk.Button(self.button_frame, text="🎤 Speak Answer", command=self.voice_input, bg="#ff4a4a", fg="white", font=("Arial", 12), padx=10, pady=5)
        voice_btn.pack(pady=10)
    
    def voice_input(self):
        response = self.listen()
        options = [opt.lower() for opt in chatbotFlow[self.step]["options"]]
        if response in options:
            self.handle_select(response)
        elif response == "ERROR":
            self.chat_label.config(text="⚠ Speech Recognition service unavailable.")
        else:
            self.chat_label.config(text=f"⚠ Couldn't recognize '{response}'. Please try again.")

    def handle_select(self, option):
        self.speak(f"You selected {option}")
        
        if self.step == 0 and option == "sure":
            self.ask_for_book_details()
        else:
            self.responses[chatbotFlow[self.step]["question"]] = option
            if self.step == len(chatbotFlow) - 1:
                self.fetch_books()
            else:
                self.step += 1
                self.display_question()
    
    def ask_for_book_details(self):
        self.chat_label.config(text="Please enter the book details:")
        self.speak("Please enter the book details")
        self.clear_widgets()

        fields = ["Title", "Author", "Publisher", "Language"]
        for field in fields:
            label = tk.Label(self.button_frame, text=field + ":", bg="#1a1a1a", fg="white", font=("Arial", 12))
            label.pack(anchor="w")
            entry = tk.Entry(self.button_frame, font=("Arial", 12))
            entry.pack(fill="x", pady=5)
            self.search_entries[field] = entry

            voice_btn = tk.Button(self.button_frame, text=f"🎤 Speak {field}", command=lambda e=entry: self.fill_entry(e), bg="#ff4a4a", fg="white", font=("Arial", 10), padx=5, pady=2)
            voice_btn.pack(pady=3)

        search_btn = tk.Button(self.button_frame, text="Search", command=self.fetch_specific_book, bg="#4a4a4a", fg="white", font=("Arial", 12), padx=10, pady=5)
        search_btn.pack(pady=10)

    def fill_entry(self, entry):
        response = self.listen()
        if response:
            entry.delete(0, tk.END)
            entry.insert(0, response)

    def fetch_specific_book(self):
        conditions = []
        values = []
        for field, entry in self.search_entries.items():
            text = entry.get().strip()
            if text:
                conditions.append(f"LOWER({field.lower()}) LIKE %s")
                values.append(f"%{text.lower()}%")

        query = "SELECT title, author, price, quantity, publisher, edition, genre FROM stock"
        if conditions:
            query += " WHERE " + " AND ".join(conditions)

        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        cursor.execute(query, values)
        books = cursor.fetchall()
        conn.close()

        if books:
            book_list = "\n".join([f"📖 {title} by {author} - ₹{price} (Stock: {quantity}, Publisher: {publisher}, Edition: {edition}, Genre: {genre})" 
                                   for title, author, price, quantity, publisher, edition, genre in books])
            self.chat_label.config(text=f"📚 Found Book:\n{book_list}")
            self.speak("Here are the books I found")
            # Call the confirm order method for the first book found
            first_book = books[0]
            self.confirm_order(first_book[0], first_book[1], first_book[2], first_book[3])  # title, author, price, stock
        else:
            self.chat_label.config(text="⚠ No book found matching your criteria.")
            self.speak("No book found matching your criteria")

    def fetch_books(self):
        conditions = []
        values = []
        
        if "What genre are you interested in?" in self.responses and self.responses["What genre are you interested in?"] != "no preference":
            conditions.append("LOWER(genre) = %s")
            values.append(self.responses["What genre are you interested in?"].lower())
        
        if "What is your minimum rating preference?" in self.responses:
            rating_map = {"above 4.5": 4.5, "above 4": 4.0, "above 3.5": 3.5}
            rating = self.responses["What is your minimum rating preference?"]
            if rating in rating_map:
                conditions.append("rating >= %s")
                values.append(rating_map[rating])
        
        if "What price range are you looking for?" in self.responses:
            price_map = {"under 500": (0, 500), "500 to 1000": (500, 1000), "above 1000": (1000, 99999)}
            price = self.responses["What price range are you looking for?"]
            if price in price_map:
                conditions.append("price BETWEEN %s AND %s")
                values.append(price_map[price][0])
                values.append(price_map[price][1])
        
        query = "SELECT title, author, price FROM stock"
        if conditions:
            query += " WHERE " + " AND ".join(conditions)
        
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        cursor.execute(query, values)
        books = cursor.fetchall()
        conn.close()
        
        if books:
            book_list = "\n".join([f"📖 {title} by {author} - ₹{price}" for title, author, price in books])
            self.chat_label.config(text=f"📚 Found Books:\n{book_list}")
            self.speak("Here are the books I found")
        else:
            self.chat_label.config(text="⚠ No book found matching your criteria.")
            self.speak("No book found matching your criteria")
    
    def clear_widgets(self):
        for widget in self.button_frame.winfo_children():
            widget.destroy()

    def confirm_order(self, book_title, book_author, book_price, available_stock):
        order_window = tk.Toplevel(self.root)
        order_window.title("Confirm Order")
        order_window.geometry("400x300")

        tk.Label(order_window, text=f"Book: {book_title} by {book_author}", font=("Arial", 14)).pack(pady=10)
        tk.Label(order_window, text=f"Price: ₹{book_price}", font=("Arial", 12)).pack(pady=5)

        tk.Label(order_window, text="Enter Quantity:", font=("Arial", 12)).pack(pady=5)
        quantity_entry = tk.Entry(order_window, font=("Arial", 12))
        quantity_entry.pack(pady=5)

        tk.Label(order_window, text="Enter Mobile Number:", font=("Arial", 12)).pack(pady=5)
        mobile_entry = tk.Entry(order_window, font=("Arial", 12))
        mobile_entry.pack(pady=5)

        def fill_quantity():
            response = self.listen()
            if response:
                quantity_entry.delete(0, tk.END)
                quantity_entry.insert(0, response)

        def fill_mobile():
            response = self.listen()
            if response:
                mobile_entry.delete(0, tk.END)
                mobile_entry.insert(0, response)

        voice_quantity_btn = tk.Button(order_window, text="🎤 Speak Quantity", command=fill_quantity, bg="#ff4a4a", fg="white", font=("Arial", 10), padx=5, pady=2)
        voice_quantity_btn.pack(pady=3)

        voice_mobile_btn = tk.Button(order_window, text="🎤 Speak Mobile Number", command=fill_mobile, bg="#ff4a4a", fg="white", font=("Arial", 10), padx=5, pady=2)
        voice_mobile_btn.pack(pady=3)

        def place_order():
            try:
                quantity = int(quantity_entry.get())
                mobile = mobile_entry.get().strip()
                if quantity <= available_stock:
                    total_price = quantity * book_price
                    self.insert_order(mobile, book_title, book_author, quantity, total_price)
                    messagebox.showinfo("Order Confirmation", "Your order has been placed successfully!")
                    order_window.destroy()
                else:
                    messagebox.showerror("Error", "Not enough stock available.")
            except ValueError:
                messagebox.showerror("Error", "Please enter a valid quantity.")

        confirm_btn = tk.Button(order_window, text="Confirm Order", command=place_order, bg="#4a4a4a", fg="white", font=("Arial", 12))
        confirm_btn.pack(pady=3)

    def insert_order(self, mobile, title, author, quantity, total_price):
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO orders (mobile_number,book_title, author, quantity, total_price) VALUES (%s, %s, %s, %s, %s)",
                       (mobile, title, author, quantity, total_price))
        cursor.execute("Update stock set quantity = quantity - %s where title = %s",
                       (quantity, title))
        conn.commit()
        cursor.close()
        conn.close()

if __name__ == "__main__":
    root = tk.Tk()
    app = ChatbotApp(root)
    root.mainloop()
