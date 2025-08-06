from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
import os

load_dotenv()
API_KEY = os.getenv('GEMINI_API_KEY')

class Client:
    def __init__(self):
        if not API_KEY:
            raise ValueError("GEMINI_API_KEY not found in environment variables. Please set it in your .env file.")
        
        self.google_llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            temperature=0,
            google_api_key=API_KEY,
            )

    def load_google_llm(self):
        return self.google_llm
