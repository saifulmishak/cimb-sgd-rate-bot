import os
import json
import requests
from datetime import datetime
import re

BOT_TOKEN = os.environ['BOT_TOKEN']
CHAT_ID = os.environ['CHAT_ID']
DATA_FILE = "rate_data.json"

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    return {"high": None, "low": None, "date": None, "target": None}

def save_data(data):
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=2)

def get_cimb_rate():
    try:
        url = "https://www.cimbclicks.com.sg/sgd-to-myr"
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
        resp = requests.get(url, headers=headers, timeout=15)
        text = resp.text
        match = re.search(r'SGD 1\.00 = MYR ([\d\.]+)', text)
        if match:
            return float(match.group(1))
    except:
        pass
    # Fallback public API
    try:
        resp = requests.get("https://api.frankfurter.app/latest?from=SGD&to=MYR", timeout=10)
        return resp.json()['rates']['MYR']
    except:
        return None

data = load_data()
rate = get_cimb_rate()
now = datetime.now()
today = now.strftime("%Y-%m-%d")

if rate:
    if data.get("date") != today:
        data["high"] = data["low"] = rate
        data["date"] = today
    else:
        if rate > data.get("high", rate):
            data["high"] = rate
        if rate < data.get("low", rate):
            data["low"] = rate

    message = f"""🔔 CIMB SG → MYR Update

Current: 1 SGD = {rate:.4f} MYR
High: {data['high']:.4f} MYR
Low: {data['low']:.4f} MYR
Time: {now.strftime('%d %b %H:%M')}

"""

    # Target alert
    target = data.get("target")
    if target and rate <= target:
        message += f"🎯 TARGET ALERT! Rate reached your target of {target}\n\n"

    message += "Rates are indicative. /target X.XX to set alert."

    # Send message
    try:
        requests.post(
            f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
            json={"chat_id": CHAT_ID, "text": message, "parse_mode": "Markdown"}
        )
    except:
        pass

    save_data(data)
