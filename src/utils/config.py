from dotenv import load_dotenv
import os

load_dotenv()

WEBSHARE_API_KEY = os.getenv("WEBSHARE_API_KEY")
AUTH_TOKEN = os.getenv("AUTH_TOKEN")
SERVER_PORT = int(os.getenv("SERVER_PORT", 8000))
