from dotenv import load_dotenv
import os

load_dotenv()

WEBSHARE_API_KEY = os.getenv("WEBSHARE_API_KEY", "").strip()
AUTH_TOKEN = os.getenv("AUTH_TOKEN", "").strip()
