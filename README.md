# AI Chatbot with MySQL Integration

A full-stack AI chatbot application built with FastAPI, MySQL, and the Groq API. This application features a modern, responsive UI and persists chat history per user.

## Features

- **AI-Powered Conversations**: Utilizes the Groq API (Llama 3 models) for intelligent responses.
- **Persistent History**: Stores chat sessions and messages in a MySQL database.
- **User Sessions**: Automatically manages chat sessions for different users.
- **Modern UI**: Clean, responsive interface with glassmorphism design elements.
- **FastAPI Backend**: High-performance, asynchronous Python backend.

## Tech Stack

- **Backend**: Python, FastAPI
- **Database**: MySQL
- **Frontend**: HTML, CSS, JavaScript
- **AI Provider**: Groq API

## Prerequisites

- Python 3.8+
- MySQL Server
- Groq API Key

## Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd <repository-directory>
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Database Setup**
   Create a MySQL database named `skillprodb` and run the following SQL to create the necessary tables:

   ```sql
   CREATE DATABASE IF NOT EXISTS skillprodb;
   USE skillprodb;

   CREATE TABLE IF NOT EXISTS Chat_Session (
       session_id INT AUTO_INCREMENT PRIMARY KEY,
       user_id INT NOT NULL,
       started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
   );

   CREATE TABLE IF NOT EXISTS Chat_History (
       id INT AUTO_INCREMENT PRIMARY KEY,
       session_id INT NOT NULL,
       sender ENUM('user', 'chatbot') NOT NULL,
       message TEXT NOT NULL,
       message_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
       FOREIGN KEY (session_id) REFERENCES Chat_Session(session_id)
   );
   ```

4. **Environment Configuration**
   Create a `.env` file in the root directory with the following variables:

   ```env
   GROQ_API_KEY=your_groq_api_key_here
   GROQ_MODEL=llama-3.3-70b-versatile
   PROVIDER=groq

   DB_HOST=localhost
   DB_USER=root
   DB_PASSWORD=your_mysql_password
   DB_NAME=skillprodb
   ```

## Usage

1. **Start the server**
   ```bash
   uvicorn main:app --reload
   ```

2. **Access the application**
   Open your browser and navigate to `http://localhost:8000`.

## API Endpoints

- `GET /`: Serves the chatbot interface.
- `GET /history/{user_id}`: Retrieves chat history for a specific user.
- `POST /chat`: Sends a message to the chatbot and receives a reply.
