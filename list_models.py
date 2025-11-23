import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("GROQ_API_KEY")
if not api_key:
    print("Error: GROQ_API_KEY not found.")
    exit(1)

client = Groq(api_key=api_key)

try:
    models = client.models.list()
    with open("models_list.txt", "w") as f:
        f.write("Available Models:\n")
        for model in models.data:
            f.write(f"- {model.id}\n")
    print("Models written to models_list.txt")
except Exception as e:
    print(f"Error listing models: {e}")
