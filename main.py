import os
import mysql.connector
from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from dotenv import load_dotenv
from typing import List, Optional
import shutil
import pypdf

# Optional Groq SDK import
try:
    from groq import Groq
except Exception:
    Groq = None

load_dotenv()

# Load environment variables
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
PROVIDER = os.getenv("PROVIDER", "groq").lower()

# Database Credentials
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")
DB_NAME = os.getenv("DB_NAME", "skillprodb")

# Initialize FastAPI
app = FastAPI()

# CORS setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8000"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve frontend files
app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/uploads", StaticFiles(directory="upload file"), name="uploads")

class ChatRequest(BaseModel):
    user_id: int
    message: str
    file_path: Optional[str] = None
    media_type: Optional[str] = None

def get_db_connection():
    try:
        conn = mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME
        )
        return conn
    except mysql.connector.Error as err:
        print(f"Error connecting to database: {err}")
        return None

def get_or_create_session(user_id: int):
    conn = get_db_connection()
    if not conn:
        return None
    
    cursor = conn.cursor(dictionary=True)
    
    try:
        # Check if user exists (Optional: In a real app, we'd ensure user exists first)
        # For this demo, we assume the user_id provided is valid or we might fail on FK constraint if not.
        
        # Check for an active session (or just create a new one for simplicity/per requirements)
        # The requirement says: "A new chat session should be created (if not already active)."
        # We'll check for the most recent session.
        
        cursor.execute("SELECT session_id FROM Chat_Session WHERE user_id = %s ORDER BY started_at DESC LIMIT 1", (user_id,))
        result = cursor.fetchone()
        
        if result:
            return result['session_id']
        else:
            cursor.execute("INSERT INTO Chat_Session (user_id) VALUES (%s)", (user_id,))
            conn.commit()
            return cursor.lastrowid
    except mysql.connector.Error as err:
        print(f"Database error: {err}")
        return None
    finally:
        cursor.close()
        conn.close()

def save_message(session_id: int, sender: str, message: str, file_path: Optional[str] = None, media_type: Optional[str] = None):
    conn = get_db_connection()
    if not conn:
        return
    
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO Chat_History (session_id, sender, message, file_path, media_type) VALUES (%s, %s, %s, %s, %s)",
            (session_id, sender, message, file_path, media_type)
        )
        conn.commit()
    except mysql.connector.Error as err:
        print(f"Error saving message: {err}")
    finally:
        cursor.close()
        conn.close()

@app.get("/")
async def root():
    """Serve the main chatbot HTML page"""
    return FileResponse("static/index.html")

@app.get("/history/{user_id}")
async def get_history(user_id: int):
    conn = get_db_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Database connection failed")
    
    cursor = conn.cursor(dictionary=True)
    try:
        # Get the session ID first
        cursor.execute("SELECT session_id FROM Chat_Session WHERE user_id = %s ORDER BY started_at DESC LIMIT 1", (user_id,))
        session = cursor.fetchone()
        
        if not session:
            return {"history": []}
        
        session_id = session['session_id']
        
        cursor.execute(
            "SELECT sender, message, file_path, media_type, message_time FROM Chat_History WHERE session_id = %s ORDER BY message_time ASC",
            (session_id,)
        )
        history = cursor.fetchall()
        return {"history": history}
    except mysql.connector.Error as err:
        raise HTTPException(status_code=500, detail=str(err))
    finally:
        cursor.close()
        conn.close()

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    upload_dir = "upload file"
    os.makedirs(upload_dir, exist_ok=True)
    file_path = os.path.join(upload_dir, file.filename)
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    return {"file_path": file_path, "media_type": file.content_type}

@app.post("/chat")
async def chat_endpoint(req: ChatRequest):
    user_id = req.user_id
    user_message = req.message
    file_path = req.file_path
    media_type = req.media_type
    
    session_id = get_or_create_session(user_id)
    if not session_id:
        return {"reply": "❌ Database error: Could not create/retrieve session."}

    # Save user message
    save_message(session_id, 'user', user_message, file_path, media_type)

    # ---- GROQ API ----
    reply = ""
    if PROVIDER == "groq":
        if Groq is None:
            reply = "❌ Groq SDK not installed. Run: pip install groq"
        elif not GROQ_API_KEY:
            reply = "❌ GROQ_API_KEY not found. Check your .env file."
        else:
            try:
                client = Groq(api_key=GROQ_API_KEY)
                messages = [{"role": "user", "content": user_message}]
                
                # Handle Multimodal Inputs
                current_model = GROQ_MODEL
                
                if file_path and os.path.exists(file_path):
                    if media_type and "image" in media_type:
                        # Image Processing
                        import base64
                        with open(file_path, "rb") as image_file:
                            encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
                        
                        messages[0]["content"] = [
                            {"type": "text", "text": user_message},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:{media_type};base64,{encoded_string}"
                                }
                            }
                        ]
                        # Force vision model for images
                        current_model = "meta-llama/llama-4-scout-17b-16e-instruct"
                        
                    elif media_type and "pdf" in media_type:
                        # PDF Processing
                        try:
                            reader = pypdf.PdfReader(file_path)
                            pdf_text = ""
                            for page in reader.pages:
                                pdf_text += page.extract_text() + "\n"
                            
                            messages[0]["content"] = f"{user_message}\n\n[Attached PDF Content]:\n{pdf_text}"
                        except Exception as e:
                            print(f"PDF Error: {e}")
                            messages[0]["content"] = f"{user_message}\n\n[System]: Failed to read PDF content."

                    elif media_type and "audio" in media_type:
                        # Audio Processing (Whisper)
                        try:
                            with open(file_path, "rb") as file:
                                transcription = client.audio.transcriptions.create(
                                    file=(os.path.basename(file_path), file.read()),
                                    model="distil-whisper-large-v3-en",
                                    response_format="json",
                                    language="en",
                                    temperature=0.0
                                )
                                transcribed_text = transcription.text
                                messages[0]["content"] = f"{user_message}\n\n[Audio Transcription]:\n{transcribed_text}"
                        except Exception as e:
                            print(f"Audio Error: {e}")
                            messages[0]["content"] = f"{user_message}\n\n[System]: Failed to transcribe audio."

                completion = client.chat.completions.create(
                    messages=messages,
                    model=current_model,
                )
                reply = completion.choices[0].message.content
            except Exception as e:
                reply = f"Groq API error: {str(e)}"
    else:
        # ---- Default fallback ----
        reply = "⚠️ Hugging Face not configured. Set PROVIDER=groq in .env"
    
    # Save bot reply
    save_message(session_id, 'chatbot', reply)
    
    return {"reply": reply}

