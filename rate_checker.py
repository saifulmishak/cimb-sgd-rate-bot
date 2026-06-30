import os
import json
import requests
from datetime import datetime
import re

print("Starting CIMB Rate Checker...")

BOT_TOKEN = os.environ['BOT_TOKEN']
CHAT_ID = os.environ['CHAT_ID']
DATA_FILE = "rate_data.json"

def load_data():
    try:
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, 'r') as f:
                return json.load(f)
    except:
        pass
    return {"high": None, "low": None, "date": None, "target": None}

def save_data(data):
    try:
        with open(DATA_FILE, 'w') as f:
            json.dump(data, f, indent=2)
    except:
        print("Could not save data file")

def get_cimb_rate():
    # Try CIMB page
    try:
        url = "https://www.cimbclicks.com.sg/sgd-to-myr"
        headers = {"User-Agent": "Mozilla/5.0"}
        resp = requests.get(url, headers=headers, timeout=15)
        match = re.search(r'SGD 1\.00 = MYR ([\d\.]+)', resp.text)
        if match:
            rate = float(match.group(1))
            print(f"Got rate from CIMB: {rate}")
            return rate
    except Exception as e:
        print(f"CIMB scrape failed: {e}")
    
    # Fallback
    try:
        resp = requests.get("https://api.frankfurter.app/latest?from=SGD&to=MYR", timeout=10)
        rate = resp.json()['rates']['MYR']
        print(f"Got fallback rate: {rate}")
        return rate
    except Exception as e:
        print(f"Fallback failed: {e}")
        return None

rate = get_cimb_rate()
now = datetime.now()
today = now.strftime("%Y-%m-%d")
data = load_data()

if rate:
    if data.get("date") != today:
        data["high"] = data["low"] = rate
        data["date"] = today
    else:
        data["high"] = max(data.get("high", rate), rate)
        data["low"] = min(data.get("low", rate), rate)

    message = f"""🔔 **CIMB SG → MYR Update**

Current: `1 SGD = {rate:.4f} MYR`
High: `{data['high']:.4f}` MYR
Low: `{data['low']:.4f}` MYR
Time: {now.strftime('%d %b %H:%M')}

Set target: /target X.XX"""

    # Simple test message first
    test_message = f"🧪 Test from GitHub Actions - {now.strftime('%H:%M')}\nRate: {rate if rate else 'Failed to fetch'}"
    try:
        requests.post(
            f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
            json={"chat_id": CHAT_ID, "text": test_message}
        )
        print("Test message sent successfully")
    except Exception as e:
        print(f"Send error: {e}")
