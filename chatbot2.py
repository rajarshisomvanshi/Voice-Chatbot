import pandas as pd
import spacy
import re
import dateutil.parser
from fuzzywuzzy import process
import whisper
import pyaudio
import wave
import ffmpeg  # For audio processing

# Load Whisper model
whisper_model = whisper.load_model("base")  # Use "tiny", "base", "small", "medium", or "large"

# Function to record audio from the microphone
def record_audio(filename, record_seconds=5):
    CHUNK = 1024
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 16000

    p = pyaudio.PyAudio()

    stream = p.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    frames_per_buffer=CHUNK)

    print("🎤 Recording...")

    frames = []

    for _ in range(0, int(RATE / CHUNK * record_seconds)):
        data = stream.read(CHUNK)
        frames.append(data)

    print("✅ Recording complete.")

    stream.stop_stream()
    stream.close()
    p.terminate()

    wf = wave.open(filename, 'wb')
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(p.get_sample_size(FORMAT))
    wf.setframerate(RATE)
    wf.writeframes(b''.join(frames))
    wf.close()

# Function to transcribe audio using Whisper
def transcribe_audio(filename):
    print("🔍 Transcribing audio...")
    try:
        # Use ffmpeg to preprocess the audio (convert to 16kHz mono)
        processed_audio, _ = (
            ffmpeg.input(filename)
            .output("pipe:", format="wav", ar=16000, ac=1)
            .run(capture_stdout=True, capture_stderr=True)
        )
        result = whisper_model.transcribe(processed_audio)
        return result["text"]
    except ffmpeg.Error as e:
        print(f"❌ FFmpeg error: {e.stderr.decode()}")
        return None

# ✅ Define Column Names (Same as Database Schema)
columns = [
    "book_id", "title", "author", "edition", "price", "language", "genre",
    "bestseller", "pages", "year_of_publication", "rating", "age_grp", "quantity"
]

# ✅ Book Data (From Your Given Dataset)
books_data = [
    (1, 'Don Quixote', 'Miguel de Cervantes', '1st', 499.99, 'English', 'Classic', 1, 992, 1605, 4.9, '16+', 10),
    (2, 'Alice\'s Adventures in Wonderland', 'Lewis Carroll', '1st', 299.99, 'English', 'Fantasy', 1, 96, 1865, 4.8, '10+', 2),
    (3, 'The Adventures of Huckleberry Finn', 'Mark Twain', '1st', 399.99, 'English', 'Adventure', 1, 366, 1884, 4.7, '12+', 3),
    (4, 'The Adventures of Tom Sawyer', 'Mark Twain', '1st', 349.99, 'English', 'Adventure', 1, 274, 1876, 4.6, '12+', 4),
    (5, 'Pride and Prejudice', 'Jane Austen', '1st', 349.99, 'English', 'Romance', 1, 279, 1813, 4.6, '14+', 32),
    (6, 'Wuthering Heights', 'Emily Brontë', '1st', 399.99, 'English', 'Romance', 1, 416, 1847, 4.5, '16+', 2),
    (7, 'Jane Eyre', 'Charlotte Brontë', '1st', 399.99, 'English', 'Romance', 1, 500, 1847, 4.7, '16+', 15),
    (8, 'Moby Dick', 'Herman Melville', '1st', 499.99, 'English', 'Adventure', 0, 635, 1851, 4.2, '16+', 19),
    (9, 'The Scarlet Letter', 'Nathaniel Hawthorne', '1st', 299.99, 'English', 'Classic', 1, 272, 1850, 4.4, '14+', 21),
    (10, 'Gulliver\'s Travels', 'Jonathan Swift', '1st', 349.99, 'English', 'Adventure', 1, 306, 1726, 4.3, '12+', 33),
    (11, 'A Christmas Carol', 'Charles Dickens', '1st', 249.99, 'English', 'Classic', 1, 104, 1843, 4.8, '10+', 60),
    (12, 'David Copperfield', 'Charles Dickens', '1st', 499.99, 'English', 'Classic', 1, 882, 1850, 4.6, '14+', 100),
    (13, 'A Tale of Two Cities', 'Charles Dickens', '1st', 399.99, 'English', 'Historical Fiction', 1, 489, 1859, 4.7, '14+', 32),
    (14, 'Little Women', 'Louisa May Alcott', '1st', 349.99, 'English', 'Classic', 1, 759, 1868, 4.8, '12+', 21),
    (15, 'Great Expectations', 'Charles Dickens', '1st', 399.99, 'English', 'Classic', 1, 505, 1861, 4.6, '14+', 12),
    (16, 'The Hobbit', 'J.R.R. Tolkien', '1st', 399.99, 'English', 'Fantasy', 1, 310, 1937, 4.8, '12+', 10),
    (17, 'Frankenstein', 'Mary Shelley', '1st', 299.99, 'English', 'Horror', 1, 280, 1818, 4.5, '16+', 15),
    (18, 'Oliver Twist', 'Charles Dickens', '1st', 399.99, 'English', 'Classic', 1, 554, 1837, 4.4, '12+', 5),
    (19, 'Crime and Punishment', 'Fyodor Dostoevsky', '1st', 449.99, 'English', 'Philosophical Fiction', 0, 671, 1866, 4.7, '18+', 5),
    (20, 'Dracula', 'Bram Stoker', '1st', 349.99, 'English', 'Horror', 1, 418, 1897, 4.6, '16+', 10),
    (21, 'Harry Potter and the Philosopher\'s Stone', 'J.K. Rowling', '1st', 299.99, 'English', 'Fantasy', 1, 223, 1997, 4.7, '9+', 17),
    (22, 'The Lord of the Rings', 'J.R.R. Tolkien', '1st', 599.99, 'English', 'Fantasy', 1, 1178, 1954, 4.9, '14+', 18),
    (23, 'The Da Vinci Code', 'Dan Brown', '1st', 349.99, 'English', 'Mystery Thriller', 1, 454, 2003, 4.1, '16+', 45),
    (24, 'The Alchemist', 'Paulo Coelho', '1st', 249.99, 'English', 'Philosophical', 1, 208, 1988, 4.3, '13+', 26),
    (25, 'The Hunger Games', 'Suzanne Collins', '1st', 349.99, 'English', 'Young Adult Dystopian', 1, 374, 2008, 4.3, '12+', 76),
    (26, 'Don Quixote', 'Miguel de Cervantes', '1st', 499.99, 'English', 'Classic', 1, 992, 1605, 4.9, '16+', 89),
    (27, "Alice's Adventures in Wonderland", 'Lewis Carroll', '1st', 299.99, 'English', 'Fantasy', 1, 96, 1865, 4.8, '10+', 34),
    (28, 'The Adventures of Huckleberry Finn', 'Mark Twain', '1st', 399.99, 'English', 'Adventure', 1, 366, 1884, 4.7, '12+', 88),
    (29, 'The Adventures of Tom Sawyer', 'Mark Twain', '1st', 349.99, 'English', 'Adventure', 1, 274, 1876, 4.6, '12+', 90),
    (30, 'Pride and Prejudice', 'Jane Austen', '1st', 349.99, 'English', 'Romance', 1, 279, 1813, 4.6, '14+', 12),
    (31, 'Wuthering Heights', 'Emily Brontë', '1st', 399.99, 'English', 'Romance', 1, 416, 1847, 4.5, '16+', 5),
    (32, 'Jane Eyre', 'Charlotte Brontë', '1st', 399.99, 'English', 'Romance', 1, 500, 1847, 4.7, '16+', 10),
    (33, 'Moby Dick', 'Herman Melville', '1st', 499.99, 'English', 'Adventure', 0, 635, 1851, 4.2, '16+', 15),
    (34, 'The Scarlet Letter', 'Nathaniel Hawthorne', '1st', 299.99, 'English', 'Classic', 1, 272, 1850, 4.4, '14+', 20),
    (35, 'Gulliver\'s Travels', 'Jonathan Swift', '1st', 349.99, 'English', 'Adventure', 1, 306, 1726, 4.3, '12+', 25),
    (36, 'A Christmas Carol', 'Charles Dickens', '1st', 249.99, 'English', 'Classic', 1, 104, 1843, 4.8, '10+', 30),
    (37, 'David Copperfield', 'Charles Dickens', '1st', 499.99, 'English', 'Classic', 1, 882, 1850, 4.6, '14+', 35),
    (38, 'A Tale of Two Cities', 'Charles Dickens', '1st', 399.99, 'English', 'Historical Fiction', 1, 489, 1859, 4.7, '14+', 40),
    (39, 'Little Women', 'Louisa May Alcott', '1st', 349.99, 'English', 'Classic', 1, 759, 1868, 4.8, '12+', 42),
    (40, 'Great Expectations', 'Charles Dickens', '1st', 399.99, 'English', 'Classic', 1, 505, 1861, 4.6, '14+', 24),
    (41, 'The Hobbit', 'J.R.R. Tolkien', '1st', 399.99, 'English', 'Fantasy', 1, 310, 1937, 4.8, '12+', 5),
    (42, 'Frankenstein', 'Mary Shelley', '1st', 299.99, 'English', 'Horror', 1, 280, 1818, 4.5, '16+', 10),
    (43, 'Oliver Twist', 'Charles Dickens', '1st', 399.99, 'English', 'Classic', 1, 554, 1837, 4.4, '12+', 2),
    (44, 'Crime and Punishment', 'Fyodor Dostoevsky', '1st', 449.99, 'English', 'Philosophical Fiction', 0, 671, 1866, 4.7, '18+', 1),
    (45, 'Dracula', 'Bram Stoker', '1st', 349.99, 'English', 'Horror', 1, 418, 1897, 4.6, '16+', 15),
    (46, 'Harry Potter and the Chamber of Secrets', 'J.K. Rowling', '1st', 299.99, 'English', 'Fantasy', 1, 251, 1998, 4.8, '9+', 25),
    (47, 'Harry Potter and the Prisoner of Azkaban', 'J.K. Rowling', '1st', 349.99, 'English', 'Fantasy', 1, 317, 1999, 4.9, '9+', 35),
    (48, 'A Game of Thrones', 'George R.R. Martin', '1st', 499.99, 'English', 'Fantasy', 1, 694, 1996, 4.8, '18+', 23),
    (49, 'A Clash of Kings', 'George R.R. Martin', '1st', 599.99, 'English', 'Fantasy', 1, 768, 1998, 4.7, '18+', 3),
    (50, 'A Storm of Swords', 'George R.R. Martin', '1st', 699.99, 'English', 'Fantasy', 1, 973, 2000, 4.9, '18+', 2),
]

# ✅ Convert Data into a Pandas DataFrame
book_table = pd.DataFrame(books_data, columns=columns)

# ✅ Print the Pandas Table
print("\n🔹 Bookstore Table (Stored in Pandas)\n")
print(book_table)

# ✅ Load spaCy NLP model
nlp = spacy.load("en_core_web_sm")

# Rest of your functions (extract_rating, extract_author, extract_pages, etc.) remain the same...

# Modify the search_books function to accept audio input
def search_books(user_input=None):
    """Runs in a loop until user types 'exit'."""

    global order_list  # Declare order_list as global to modify it inside the function

    while True:
        if user_input is None:
            print("\n🎤 Press '1' to speak or '2' to type your query (or type 'exit' to stop): ")
            choice = input().strip()

            if choice == "1":
                # Record audio
                audio_filename = "user_input.wav"
                record_audio(audio_filename, record_seconds=5)
                user_input = transcribe_audio(audio_filename)
                if user_input:
                    print(f"\n🎤 You said: {user_input}")
                else:
                    print("\n❌ Failed to transcribe audio. Please try again.")
                    continue
            elif choice == "2":
                user_input = input("\n📚 Enter your book query: ").strip().lower()
            elif user_input == "exit":
                print("\n👋 Exiting the bookstore search. Have a great day!")
                break
            else:
                print("\n❌ Invalid choice. Please try again.")
                continue
        else:
            user_input = user_input.strip().lower()

        if user_input == "exit":
            print("\n👋 Exiting the bookstore search. Have a great day!")
            break

        # Handle Order Summary Request
        if "order summary" in user_input:
            user_id = input("📞 Enter your phone number to fetch your order summary: ").strip()
            user_orders = order_list[order_list["user_id"] == user_id]

            if not user_orders.empty:
                total_value = user_orders["price"].sum()  # Calculate total price
                print("\n🛒 Here is your order summary:\n")
                print(user_orders)
                print(f"\n💰 Order value = {total_value}")  # Print total order value
            else:
                print("\n❌ No orders found for this number.")

            continue

        # Extract all possible details
        extracted_data = extract_query_details(user_input, book_table)

        # Debugging: Show extracted filters
        print("\n🔹 Extracted Data:", extracted_data)

        conditions = []

        # Detect if user wants to buy/order a specific book
        if "buy" in user_input or "order" in user_input:
            if extracted_data["title"]:
                book_title = extracted_data["title"][0]  # Extract first title match
                book_row = book_table[book_table["title"].str.contains(book_title, case=False, na=False)]

                if not book_row.empty:
                    available_quantity = book_row.iloc[0]["quantity"]
                    print(f"\n📦 '{book_title}' is available. ({available_quantity} in stock)")

                    # Ask for order quantity
                    order_quantity = int(input("Enter the quantity you want to order: "))

                    if order_quantity > available_quantity:
                        print(f"\n❌ Only {available_quantity} available.")
                    else:
                        # Get user ID (phone number)
                        user_id = input("Enter your phone number: ").strip()

                        # Calculate total price
                        total_price = order_quantity * book_row.iloc[0]["price"]

                        # Create a new order entry
                        new_order = pd.DataFrame([[user_id] + list(book_row.iloc[0])], columns=["user_id"] + list(book_table.columns))
                        new_order["quantity"] = order_quantity
                        new_order["price"] = total_price  # Updating price to reflect total cost

                        order_list = pd.concat([order_list, new_order], ignore_index=True)

                        # Deduct ordered quantity from stock
                        book_table.at[book_row.index[0], "quantity"] -= order_quantity

                        print("\n✅ Order placed successfully!")
                        print("\n🛒 Updated Order List:\n", order_list)
                else:
                    print(f"\n❌ Sorry, '{book_title}' is not available in our store.")

                continue

        # Regular search functionality (if user is not ordering)
        if extracted_data["title"]:
            title_conditions = " | ".join([f'title.str.contains("{t}", case=False, na=False)' for t in extracted_data["title"]])
            conditions.append(f"({title_conditions})")

        if extracted_data["author"]:
            conditions.append(f'author.str.contains("{extracted_data["author"]}", case=False, na=False)')

        if extracted_data["genre"]:
            genre_conditions = " | ".join([f'genre.str.contains("{g}", case=False, na=False)' for g in extracted_data["genre"]])
            conditions.append(f"({genre_conditions})")

        if extracted_data["year_of_publication"]:
            conditions.append(f"year_of_publication {extracted_data['year_condition']} {extracted_data['year_of_publication']}")

        if extracted_data["bestseller"] is not None:
            conditions.append("bestseller == 1")

        if extracted_data["price"] is not None:
            conditions.append(f"price {extracted_data['price_condition']} {extracted_data['price']}")

        if extracted_data["pages"] is not None:
            conditions.append(f"pages {extracted_data['pages_condition']} {extracted_data['pages']}")

        if extracted_data["rating"] is not None:
            conditions.append(f"rating {extracted_data['rating_condition']} {extracted_data['rating']}")

        if not conditions:
            print("\n❌ Error: Could not understand your query. Please try again.")
            continue

        # Apply Filtering
        query_string = " and ".join(conditions)
        print(f"\n🔍 Query String: {query_string}")
        matching_books = book_table.query(query_string)

        # Display Results
        if not matching_books.empty:
            print("\n🔹 Matching Books:\n")
            print(matching_books)
        else:
            print("\n❌ No books found matching your query. Try modifying your search.")

# Run the search_books function
search_books()