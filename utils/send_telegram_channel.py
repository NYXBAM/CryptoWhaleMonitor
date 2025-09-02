import os
import requests
from dotenv import load_dotenv
from functools import wraps
import time
import threading
from collections import deque


load_dotenv()
TELEGRAM_BOT_TOKEN = os.getenv("TG_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TG_CHAT_ID")


class RateLimiter:
    """Simple rate limiter to avoid telegram API spam"""
    def __init__(self, max_calls, period):
        self.max_calls = max_calls
        self.period = period
        self.calls = deque()
        self.lock = threading.Lock()
    
    def __call__(self, func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            with self.lock:
                now = time.time()
                while self.calls and self.calls[0] <= now - self.period:
                    self.calls.popleft()
                
                if len(self.calls) >= self.max_calls:
                    wait_time = self.period - (now - self.calls[0])
                    if wait_time > 0:
                        time.sleep(wait_time)
                        now = time.time()
                
                self.calls.append(now)
            
            return func(*args, **kwargs)
        return wrapper

@RateLimiter(max_calls=1, period=2)
def send_telegram_message(message: str) -> bool:
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print("Telegram token or chat_id not set in .env")
        return False

    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "HTML",
        "disable_web_page_preview": True
    }

    try:
        r = requests.post(url, json=payload, timeout=10)
        r.raise_for_status()
        result = r.json()
        if result.get("ok"):
            return True
        else:
            print("Telegram API error:", result)
            return False
    except Exception as e:
        print("Error sending Telegram message:", e)
        return False
