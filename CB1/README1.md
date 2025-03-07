# Voice-Chatbot

FOR CHATBOT!-
README.md
markdown
Copy
# Book Finder Chatbot

## Overview
This is a simple Book Finder Chatbot built using Python and Tkinter for the GUI, MySQL for the database, and Google Text-to-Speech (gTTS) and SpeechRecognition for voice interactions. The chatbot helps users find books based on their preferences and allows them to place orders.

## Features
- *Interactive GUI*: Built using Tkinter.
- *Voice Interaction*: Users can interact with the chatbot using voice commands.
- *Book Search*: Users can search for books by genre, rating, and price range.
- *Order Placement*: Users can place orders for books, specifying the quantity and providing their mobile number.

## Requirements
- Python 3.x
- Tkinter (usually comes with Python)
- MySQL Connector/Python
- gTTS
- SpeechRecognition
- pyaudio (for microphone input)

## Installation
1. *Clone the repository*:
   bash
   git clone https://github.com/yourusername/book-finder-chatbot.git
   cd book-finder-chatbot
Install the required Python packages:

bash
Copy
pip install -r requirements.txt
Set up the MySQL database:

Import the database schema and data from chatbot1-db.txt into your MySQL server.

Update the DB_CONFIG in the chatbot.py file with your MySQL credentials.

Run the chatbot:

bash
Copy
python chatbot.py
Database Schema
The MySQL database consists of two tables: stock and orders.

stock Table
title: Title of the book (VARCHAR)

author: Author of the book (VARCHAR)

price: Price of the book (DECIMAL)

quantity: Available stock quantity (INT)

publisher: Publisher of the book (VARCHAR)

edition: Edition of the book (VARCHAR)

genre: Genre of the book (VARCHAR)

rating: Rating of the book (DECIMAL)

orders Table
id: Unique order ID (INT, AUTO_INCREMENT, PRIMARY KEY)

user_mobile: User's mobile number (VARCHAR)

book_title: Title of the ordered book (VARCHAR)

author: Author of the ordered book (VARCHAR)

quantity: Quantity ordered (INT)

total_price: Total price of the order (DECIMAL)

order_date: Date and time of the order (TIMESTAMP, DEFAULT CURRENT_TIMESTAMP)

Usage
Launch the Chatbot: Run the chatbot.py script to start the chatbot.

Interact with the Chatbot: Follow the on-screen prompts to search for books and place orders.

Voice Commands: Use the "Speak Answer" button to interact with the chatbot using voice commands.

Contributing
Contributions are welcome! Please fork the repository and submit a pull request with your changes.

License
This project is licensed under the MIT License. See the LICENSE file for details.

Acknowledgments
Tkinter

MySQL Connector/Python

gTTS

SpeechRecognition

Copy

### chatbot1-db.txt

sql
-- Database: books_db

CREATE DATABASE IF NOT EXISTS books_db;
USE books_db;

-- Table structure for table stock

CREATE TABLE IF NOT EXISTS stock (
  title VARCHAR(255) NOT NULL,
  author VARCHAR(255) NOT NULL,
  price DECIMAL(10, 2) NOT NULL,
  quantity INT NOT NULL,
  publisher VARCHAR(255) NOT NULL,
  edition VARCHAR(50) NOT NULL,
  genre VARCHAR(100) NOT NULL,
  rating DECIMAL(3, 2) NOT NULL
);

-- Dumping data for table stock

INSERT INTO stock (title, author, price, quantity, publisher, edition, genre, rating) VALUES
('The Great Gatsby', 'F. Scott Fitzgerald', 450.00, 10, 'Scribner', '1st', 'Fiction', 4.5),
('To Kill a Mockingbird', 'Harper Lee', 350.00, 15, 'J.B. Lippincott & Co.', '1st', 'Fiction', 4.8),
('1984', 'George Orwell', 400.00, 20, 'Secker & Warburg', '1st', 'Sci-Fi', 4.7),
('The Hobbit', 'J.R.R. Tolkien', 500.00, 12, 'Allen & Unwin', '1st', 'Fantasy', 4.6),
('The Da Vinci Code', 'Dan Brown', 550.00, 18, 'Doubleday', '1st', 'Mystery', 4.4),
('Steve Jobs', 'Walter Isaacson', 600.00, 8, 'Simon & Schuster', '1st', 'Biography', 4.3);

-- Table structure for table orders

CREATE TABLE IF NOT EXISTS orders (
  id INT AUTO_INCREMENT PRIMARY KEY,
  user_mobile VARCHAR(15) NOT NULL,
  book_title VARCHAR(255) NOT NULL,
  author VARCHAR(255) NOT NULL,
  quantity INT NOT NULL,
  total_price DECIMAL(10, 2) NOT NULL,
  order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
Explanation
README.md: This file provides an overview of the project, installation instructions, usage guidelines, and other relevant information.

chatbot1-db.txt: This file contains the SQL commands to create the database and tables, as well as some sample data for the stock table.

You can save these files in your project directory and use them to set up and document your Book Finder Chatbot project.












FOR CHATBOT2-
