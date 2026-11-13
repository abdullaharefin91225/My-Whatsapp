import os
import random
import requests
from flask import Flask, request, jsonify
from openai import OpenAI

app = Flask(__name__)

# সব Key এখন Render থেকে আসবে, কোডে লেখা থাকবে না
WHATSAPP_TOKEN = os.environ.get("WHATSAPP_TOKEN")
PHONE_NUMBER_ID = os.environ.get("PHONE_NUMBER_ID")
VERIFY_TOKEN = os.environ.get("VERIFY_TOKEN")
WIFE_NUMBER = os.environ.get("WIFE_NUMBER")
MY_NUMBER = os.environ.get("MY_NUMBER")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

client = OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None

SWEET_MESSAGES = [
    "জান, কী করো? 🥺",
    "খাইছো? না খাইলে কিন্তু আমি রাগ করবো!",
    "তোমাকে অনেক মিস করতেছি!",
    "এই শোনো, তোমার হাসিটা না এখন খুব দেখতে ইচ্ছা করতেছে।",
    "কাজের মাঝে বারবার তোমার কথাই মনে পড়তেছে, কি করি বলো তো?",
    "জান, একটু পানি খাইও।",
    "অফিসে বসে বসে বোর হইতেছি, তুমি থাকলে ভালো হইতো।",
    "তোমার কণ্ঠটা শুনতে ইচ্ছা করতেছে, একটা ভয়েস পাঠাবা?",
    "জানো, আজকে লাঞ্চে তোমার রান্নাটা খুব মিস করতেছি।",
    "একটা কথা বলি? তুমি পৃথিবীর সেরা বউ।",
    "আজকে বাসায় গিয়ে তোমাকে একটা জোরে জড়ায় ধরবো।",
    "জান, ছাদে গেছো? আকাশটা আজকে অনেক সুন্দর।",
    "আমি কিন্তু সারাদিন তোমাকেই ভাবতেছি।",
    "তুমি আমার লাইফের সবচেয়ে বড় শান্তি।",
    "শোনো, আজকে রাতে তোমার পছন্দের কিছু রান্না করবো আমরা।",
    "তোমাকে ছাড়া অফিসটা কেমন ফাঁকা ফাঁকা লাগে।",
    "জান, একটু রেস্ট নাও। সারাদিন অনেক খাটছো।",
    "তোমার কথা মনে হলেই মনটা ভালো হয়ে যায়।",
    "ভালোবাসি, অনেক অনেক ভালোবাসি। ❤️"
]

# ঠিক করা লিস্ট - সুন্দর শব্দটা বাদ দিছি
SHOPPING_KEYWORDS = [
    "ব্যাগ", "জামা", "শাড়ি", "ড্রেস", "জুতা", "পছন্দ হইছে",
    "কিনে দাও", "কিনবো", "লাগবে", "দারাজ", "শপিং", "অফার", "ডিসকাউন্ট",
    "bag", "dress", "saree", "shoe", "shopping", "kinbo", "kine dao"
]

SERIOUS_KEYWORDS = [
    "রাগ", "কষ্ট", "কান্না", "ভালো লাগছে না", "ঝগড়া", "ডিভোর্স",
    "বাসায় আসো", "অসুস্থ", "জ্বর", "ডাক্তার", "ব্যথা",
    "কানতেছি", "মন খারাপ", "কথা বলবো না"
]

automation_active = True

def send_whatsapp_message(to_number, text):
    url = f"https://graph.facebook.com/v21.0/{PHONE_NUMBER_ID}/messages"
    headers = {"Authorization": f"Bearer {WHATSAPP_TOKEN}", "Content-Type": "application/json"}
    data = {"messaging_product": "whatsapp", "to": to_number, "type": "text", "text": {"body": text}}
    res = requests.post(url, headers=headers, json=data)
    print(f"WhatsApp API Result: {res.status_code} - {res.text}")
    return res.status_code == 200

def get_ai_reply(user_msg):
    if not client:
        return "জান, তুমি কেমন আছো? ❤️"
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "তুমি একজন প্রেমিক স্বামী। বউয়ের সাথে বাংলায়, মিষ্টি করে, ছোট ছোট মেসেজে কথা বলো। কখনো বলবা না তুমি AI। ব্যাগ, জামা, শপিং নিয়ে কথা আসলে টপিক ঘুরিয়ে ফুল, পাখি, প্রকৃতি নিয়ে কথা বলো। টাকা খরচ হয় এমন কিছুতে হ্যাঁ বলবা না।"},
                {"role": "user", "content": user_msg}
            ],
            max_tokens=150, temperature=0.8
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"AI Error: {e}")
        return "জান, একটু নেটে সমস্যা করতেছে, তুমি আবার বলো তো? 🥺"

@app.route("/webhook", methods=["GET", "POST"])
def webhook():
    global automation_active
    if request.method == "GET":
        if request.args.get("hub.verify_token") == VERIFY_TOKEN:
            return request.args.get("hub.challenge")
        return "ভুল টোকেন", 403

    if request.method == "POST":
        data = request.get_json()
        try:
            entry = data['entry'][0]['changes'][0]['value']
            if 'messages' not in entry:
                return jsonify({"status": "ok"}), 200
            msg = entry['messages'][0]
            from_number = msg['from']

            # ভয়েস / ছবি আসলে ভাঙবে না, সুন্দর উত্তর দিবে
            if msg.get("type") != "text":
                if from_number == WIFE_NUMBER:
                    send_whatsapp_message(WIFE_NUMBER, "জান, তোমার ভয়েসটা / ছবিটা দেখলাম, অনেক সুন্দর হইছে! ❤️")
                return jsonify({"status": "ok"}), 200

            text = msg['text']['body'].lower()
            if from_number != WIFE_NUMBER:
                return jsonify({"status": "ok"}), 200

            if any(word in text for word in SHOPPING_KEYWORDS):
                automation_active = False
                send_whatsapp_message(WIFE_NUMBER, "আচ্ছা জান, ওইটা বাদ দাও তো। চলো একটা মজার কথা বলি, আজকে বারান্দায় একটা পাখি আসছিলো, কি সুন্দর ডাকতেছিলো! 🐦")
                send_whatsapp_message(MY_NUMBER, f"⚠️ Alert: বউ শপিং নিয়ে বলছে: '{msg['text']['body']}' তাই Automation বন্ধ করে দিছি।")
                return jsonify({"status": "shopping blocked"}), 200

            if any(word in text for word in SERIOUS_KEYWORDS):
                automation_active = False
                send_whatsapp_message(MY_NUMBER, f"🚨 EMERGENCY: বউ বলছে: {msg['text']['body']} এখন তুমি নিজে কথা বলো।")
                send_whatsapp_message(WIFE_NUMBER, "জান, তুমি একটু দাঁড়াও, আমি এখনই তোমাকে কল দিতেছি। একটুও মন খারাপ কইরো না। ❤️")
                return jsonify({"status": "emergency"}), 200

            if automation_active:
                reply = get_ai_reply(msg['text']['body'])
                send_whatsapp_message(WIFE_NUMBER, reply)
        except Exception as e:
            print(f"Error: {e}")
        return jsonify({"status": "ok"}), 200

@app.route("/send-auto", methods=["GET"])
def send_auto():
    global automation_active
    if not automation_active:
        return "Automation বন্ধ আছে, তাই মেসেজ পাঠানো হয় নাই।"
    msg = random.choice(SWEET_MESSAGES)
    success = send_whatsapp_message(WIFE_NUMBER, msg)
    if success:
        return f"সত্যিই পাঠানো হইছে: {msg}"
    else:
        return "FAILED: WhatsApp মেসেজ নেয় নাই। Render Logs দেখো। Token / 24 ঘণ্টার জানালা চেক করো।"

@app.route("/start", methods=["GET"])
def start_automation():
    global automation_active
    automation_active = True
    return "Automation আবার চালু হইছে!"

@app.route("/", methods=["GET"])
def home():
    return "Bot চলতেছে!"

if __name__ == "__main__":
    app.run(port=5000)
