# SkillPro Multimodal AI Assistant

A powerful, full-stack AI chatbot application built with **FastAPI**, **MySQL**, and the **Groq API**. This assistant supports **Text**, **Images**, **Audio**, and **PDF** inputs, providing intelligent, context-aware responses.

## 🚀 Features

- **Multimodal Capabilities**:
  - **Text**: Intelligent conversations using Llama 3 models.
  - **Images**: Visual analysis and descriptions using `meta-llama/llama-4-scout-17b-16e-instruct`.
  - **Audio**: Speech-to-text transcription using Whisper models.
  - **PDF**: Content extraction and context-aware Q&A.
- **Persistent History**: Stores chat sessions, messages, and file attachments in a MySQL database.
- **User Sessions**: Automatically manages chat sessions for different users.
- **Modern UI**: Clean, responsive interface with glassmorphism design elements, file previews, and attachment support.
- **FastAPI Backend**: High-performance, asynchronous Python backend.

## 🛠️ Tech Stack

- **Backend**: Python, FastAPI, Uvicorn
- **Database**: MySQL
- **Frontend**: HTML5, CSS3, Vanilla JavaScript
- **AI Provider**: Groq API (Llama 3/4, Whisper)

## 📋 Prerequisites

- Python 3.8+
- MySQL Server
- Groq API Key

## ⚙️ Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/depressedKarimul/Upsilon.git
   cd Upsilon
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
       chat_id INT AUTO_INCREMENT PRIMARY KEY,
       session_id INT NOT NULL,
       sender ENUM('user', 'chatbot') NOT NULL,
       message TEXT NOT NULL,
       file_path VARCHAR(255) DEFAULT NULL,
       media_type VARCHAR(50) DEFAULT NULL,
       message_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
       FOREIGN KEY (session_id) REFERENCES Chat_Session(session_id) ON DELETE CASCADE
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

## 🏃‍♂️ Usage

1. **Start the server**
   ```bash
   uvicorn main:app --reload
   ```

2. **Access the application**
   Open your browser and navigate to `http://localhost:8000`.

## 📡 API Endpoints

- `GET /`: Serves the chatbot interface.
- `GET /history/{user_id}`: Retrieves chat history for a specific user.
- `POST /chat`: Sends a message (text + attachments) to the chatbot.
- `POST /upload`: Handles file uploads.

## 🧪 Testing

Run the automated test script to verify backend functionality:
```bash
python test_api.py
```
