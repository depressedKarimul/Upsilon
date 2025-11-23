CREATE DATABASE IF NOT EXISTS skillprodb;
USE skillprodb;

CREATE TABLE Chat_Session (
CREATE DATABASE IF NOT EXISTS skillprodb;
USE skillprodb;

CREATE TABLE Chat_Session (
  session_id INT AUTO_INCREMENT PRIMARY KEY,
  user_id INT NOT NULL,
  started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (user_id) REFERENCES User(user_id) ON DELETE CASCADE
);

CREATE TABLE Chat_History (
  chat_id INT AUTO_INCREMENT PRIMARY KEY,
  session_id INT NOT NULL,
  sender ENUM('user', 'chatbot') NOT NULL,
  message TEXT NOT NULL,
  file_path VARCHAR(255) DEFAULT NULL,
  media_type VARCHAR(50) DEFAULT NULL,
  message_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (session_id) REFERENCES Chat_Session(session_id) ON DELETE CASCADE
);