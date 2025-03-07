Bookstore Voice Assistant

Overview

This project implements an AI-powered voice assistant for a bookstore. It allows users to check book availability, manage orders, and receive recommendations using natural language queries. The assistant integrates real-time voice processing using Whisper for speech-to-text and gTTS for text-to-speech responses.

Features

Natural Language Processing (NLP): Extracts keywords and intent from user queries.

Book Availability Check: Retrieves book stock details from a Pandas dataframe (chatbot2-db).

Order Management: Processes orders and updates stock accordingly.

Real-time Voice Interface: Converts user speech into text using Whisper and provides spoken responses via gTTS.

Interactive Chatbot Behavior: Responds conversationally, offering a smooth user experience.

Technologies Used

Python

Pandas (for book database management)

Hugging Face Transformers (for LLM-powered query interpretation)

Whisper (for voice-to-text conversion)

gTTS (Google Text-to-Speech) (for text-to-voice responses)

FAISS (for vector-based memory retrieval)

Neo4j (for knowledge graph retrieval)

Llama.cpp (for running the LLM)

Installation

Clone the repository:

git clone https://github.com/your-repo/bookstore-assistant.git
cd bookstore-assistant

Install dependencies:

pip install -r requirements.txt

Run the assistant:

python main.py

Usage

Ask about book availability: "Do you have 'The Great Gatsby' in stock?"

Place an order: "I'd like to order 2 copies of '1984'."

Get recommendations: "Suggest me a sci-fi novel."

Check order details: "What books have I ordered before?"

Future Enhancements

Phone Call Integration for real-time voice-based interactions.

Multi-lingual Support for broader accessibility.

Enhanced Personalization using user history and preferences.

Contribution

Feel free to fork and contribute to this project! Open an issue for bugs or feature requests.
