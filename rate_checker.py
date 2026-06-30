import os
import requests
from datetime import datetime

BOT_TOKEN = os.environ['BOT_TOKEN']
CHAT_ID = os.environ['CHAT_ID']

message = f"✅ Test successful at {datetime.now().strftime('%H:%M')}\nCIMB Rate Bot is working!"

requests.post(
    f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
    json={"chat_id": CHAT_ID, "text": message}
)

print("Test message sent")
