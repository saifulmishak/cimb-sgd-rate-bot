import os
import json
import requests
from datetime import datetime
import re

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
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=2)

def get_cimb_rate():
    try:
        url = "https://www.cimbclicks.com.sg/sgd-to-myr"
        headers = {"User-Agent": "Mozilla/5.0"}
        resp = requests.get(url, headers=headers, timeout=15)
        match = re.search(r'SGD 1\.00 = MYR ([\d\.]+)', resp.text)
        if match:
            return float(match.group(1))
    except:
        pass
    try:
        resp = requests.get("https://api.frankfurter.app/latest?from=SGD&to=MYR", timeout=10)
        return resp.json()['rates']['MYR']
    except:
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

    message = f"""🔔 **CIMB SG 🇸🇬 → MY 🇲🇾 Update**
====================================

Current: 1 SGD = {rate:.4f} MYR
High: {data['high']:.4f} MYR 📈
Low: {data['low']:.4f} MYR 📉
Time: {now.strftime('%d %b %H:%Mhrs')}

===================================="""

    if data.get("target"):
        message += f"\n✅ Target set to {data['target']}"

    target = data.get("target")
    if target and rate <= float(target):
        message += f"\n🎯 **TARGET ALERT!** Rate reached {target}"

    message += "\n\nSend `/target X.XX` to change alert."

    requests.post(
        f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
        json={"chat_id": CHAT_ID, "text": message}
    )

    save_data(data)
