from dotenv import load_dotenv
import os

load_dotenv()
print("TELEGRAM_TOKEN =", os.getenv("TELEGRAM_TOKEN"))
