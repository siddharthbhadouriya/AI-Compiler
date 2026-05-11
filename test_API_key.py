from dotenv import load_dotenv
import os

load_dotenv()

print(print("GROQ_API_KEY loaded:", bool(os.getenv("GROQ_API_KEY")))
)