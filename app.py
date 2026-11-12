import os
import random
import requests
import time
from flask import Flask, request, jsonify
from datetime import datetime
from openai import OpenAI

app = Flask(__name__)

# ===== তোমার সেটিংস এখানে বসাও =====
WHATSAPP_TOKEN = "EAAVNVudEJZA0BSZC25oQfXeohf70crQ4gqczdSUbJBEelNUbP3UyE0OlpduR9aqCxvsZBrVgGt787ZBYY1XFnsnMh8V32pZCMQymlsz9Mkc8SswDyJjEoB3U4kh9pcXUsO93NrFVfVGkTZAebzRWKkZCcFChRptQVnpv9iyJiXjt91pIGLrAZBSzlPiakxzeJDTXXTtm1OCRsKHLZCQbpxV1x5z3IvUCaXIZBlEygD70Wbjiqo5ld6NFiKIFg6OKZCtQdNhGgBlFRJBKGEkaTsTXIvS"
PHONE_NUMBER_ID = "1401593493045803"
VERIFY_TOKEN = "soulmate91225"  # 【entity-Meta¦canonical_name=Meta】 তে এটাই দিবা
WIFE_NUMBER = "8801992619083"  # বউয়ের নাম্বার, 88 সহ, + ছাড়া
MY_NUMBER = "8801400415585" # তোমার নাম্বার, Emergency Alert যাবে এখানে
OPENAI_API_KEY = "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"

client = OpenAI(api_key=OPENAI_API_KEY)

# ===== ১. তোমার ২৫ টা রেডিমেড মিষ্টি মেসেজ =====
SWEET_MESSAGES = [
    "জান, কী করো? 🥺",
    "খাইছো? না খাইলে কিন্তু আমি রাগ করবো!",
    "তোমাকে অনেক মিস করতেছি!",
    "এই শোনো, তোমার হাসিটা না এখন খুব দেখতে ইচ্ছা করতেছে।",
    "কাজের মাঝে বারবার তোমার কথাই মনে পড়তেছে, কি করি বলো তো?",
    "জান, একটু পানি খাইও।",
    "আচ্ছা, আজকে তুমি এতো সুন্দর কেন? 😍",
    "অফিসে বসে বসে বোর হইতেছি, তুমি থাকলে ভালো হইতো।",
    "তোমার কণ্ঠটা শুনতে ইচ্ছা করতেছে, একটা ভয়েস পাঠাবা?",
    "জানো, আজকে লাঞ্চে তোমার রান্নাটা খুব মিস করতেছি।",
    "এই, তুমি কি এখনো আমার উপর রাগ করে আছো? 🥺",
    "একটা কথা বলি? তুমি পৃথিবীর সেরা বউ।",
    "আজকে বাসায় গিয়ে তোমাকে একটা জোরে জড়ায় ধরবো।",
    "জান, ছাদে গেছো? আকাশটা আজকে অনেক সুন্দর।",
    "তোমার চুলগুলো আজকে কেমন লাগতেছে? ছবি পাঠাও তো একটা।",
    "আমি কিন্তু সারাদিন তোমাকেই ভাবতেছি।",
    "তুমি আমার লাইফের সবচেয়ে বড় শান্তি।",
    "কি করো? কাজ কম হইছে?",
    "শোনো, আজকে রাতে তোমার পছন্দের কিছু রান্না করবো আমরা।",
    "তোমাকে ছাড়া অফিসটা কেমন ফাঁকা ফাঁকা লাগে।",
    "আচ্ছা, তুমি কি জানো তুমি হাসলে তোমাকে কত কিউট লাগে?",
    "জান, একটু রেস্ট নাও। সারাদিন অনেক খাটছো।",
    "মন খারাপ? আসো একটু গল্প করি।",
    "তোমার কথা মনে হলেই মনটা ভালো হয়ে যায়।",
    "ভালোবাসি, অনেক অনেক ভালোবাসি। ❤️"
]

# ===== ২. বিপদজনক শব্দ - এগুলা বললেই Automation বন্ধ =====
# বউ যদি শপিং নিয়ে কিছু বলে, সাথে সাথে বন্ধ
SHOPPING_KEYWORDS = [
    "ব্যাগ", "জামা", "শাড়ি", "ড্রেস", "জুতা", "সুন্দর", "পছন্দ হইছে",
    "কিনে দাও", "লাগবে", "দারাজ", "শপিং", "অফার", "ডিসকাউন্ট",
    "bag", "dress", "saree", "shoe", "shopping", "kinbo", "kine dao"
]

# ===== ৩. সিরিয়াস শব্দ - এগুলা বললে তোমার কাছে Emergency Alert =====
SERIOUS_KEYWORDS = [
    "রাগ", "কষ্ট", "কান্না", "ভালো লাগছে না", "ঝগড়া", "ডিভোর্স",
    "বাসায় আসো", "অসুস্থ", "জ্বর", "ডাক্তার", "ব্যথা", "মা অসুস্থ",
    "কানতেছি", "মন খারাপ", "রাগ করছি", "কথা বলবো না"
]

# Automation চালু আছে কিনা, এটা মনে রাখবে
automation_active = True

def send_whatsapp_message(to_number, text):
    url = f"https://graph.facebook.com/v21.0/{PHONE_NUMBER_ID}/messages"
    headers = {"Authorization": f"Bearer {WHATSAPP_TOKEN}", "Content-Type": "application/json"}
    data = {
        "messaging_product": "【entity-whatsapp¦canonical_name=WhatsApp】",
        "to": to_number,
        "type": "text",
        "text": {"body": text}
    }
    requests.post(url, headers=headers, json=data)
    print(f"পাঠানো হইছে -> {to_number}: {text}")

def send_emergency_alert(reason, wife_msg):
    alert = f"🚨 EMERGENCY ALERT 🚨\n\nবউ বলছে: {wife_msg}\nকারণ: {reason}\n\nAutomation বন্ধ করে দেওয়া হইছে। এখন তুমি নিজে কথা বলো।"
    send_whatsapp_message(MY_NUMBER, alert)

def get_ai_reply(user_msg):
    """বউ রিপ্লাই দিলে AI সুন্দর করে উত্তর দিবে"""
    system_prompt = """
    তুমি একজন প্রেমিক স্বামী। তুমি তোমার বউয়ের সাথে বাংলায় কথা বলতেছো, খুব মিষ্টি করে, রোমান্টিক ভাবে।
    তুমি কখনোই বলবা না তুমি AI। তুমি বলবা তুমি তার স্বামী।
    ভাষা হবে ঢাকাইয়া মিষ্টি বাংলা, ছোট ছোট মেসেজ, ইমোজি ব্যবহার করবা।

    কড়া নিয়ম:
    1. বউ যদি ব্যাগ, জামা, শাড়ি, শপিং নিয়ে কিছু বলে, তুমি সাথে সাথে টপিক ঘুরায় দিবা। বলবা 'আচ্ছা বাদ দাও, চলো ফুল নিয়ে গল্প করি' - এই টাইপ।
    2. কখনোই টাকা খরচ হয় এমন কিছুতে হ্যাঁ বলবা না। বলবা 'পরে দেখবো জান'।
    3. যদি কথা বেশি সিরিয়াস হয়ে যায়, তুমি বলবা 'জান, একটু দাঁড়াও, আমি একটু কাজটা সেরে তোমাকে কল দিতেছি।'
    4. সবসময় ফুল, পাখি, প্রকৃতি, ভালোবাসা নিয়ে কথা বলবা।
    """
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_msg}
            ],
            max_tokens=150,
            temperature=0.8
        )
        return response.choices[0].message.content
    except Exception as e:
        return "জান, একটু নেটে সমস্যা করতেছে, তুমি আবার বলো তো? 🥺"

@app.route("/webhook", methods=["GET", "POST"])
def webhook():
    global automation_active
    if request.method == "GET":
        # Meta Verify করার জন্য
        if request.args.get("hub.verify_token") == VERIFY_TOKEN:
            return request.args.get("hub.challenge")
        return "ভুল টোকেন", 403

    if request.method == "POST":
        data = request.get_json()
        try:
            # মেসেজটা বের করা
            entry = data['entry'][0]['changes'][0]['value']
            if 'messages' not in entry:
                return jsonify({"status": "ok"}), 200
            
            msg = entry['messages'][0]
            from_number = msg['from']
            text = msg['text']['body'].lower()

            # শুধু বউয়ের মেসেজের উত্তর দিবে
            if from_number != WIFE_NUMBER:
                return jsonify({"status": "ok"}), 200

            # === নিয়ম ১: শপিং শব্দ আসলেই Automation বন্ধ ===
            if any(word in text for word in SHOPPING_KEYWORDS):
                automation_active = False
                send_whatsapp_message(WIFE_NUMBER, "আচ্ছা জান, ওইটা বাদ দাও তো। চলো একটা মজার কথা বলি, আজকে বারান্দায় একটা পাখি আসছিলো, কি সুন্দর ডাকতেছিলো! 🐦")
                send_whatsapp_message(MY_NUMBER, f"⚠️ Alert: বউ শপিং নিয়ে বলছে: '{msg['text']['body']}' তাই Automation বন্ধ করে দিছি।")
                return jsonify({"status": "shopping blocked"}), 200

            # === নিয়ম ২: সিরিয়াস হলে Emergency Alert ===
            if any(word in text for word in SERIOUS_KEYWORDS):
                automation_active = False
                send_emergency_alert("সিরিয়াস কথা", msg['text']['body'])
                send_whatsapp_message(WIFE_NUMBER, "জান, তুমি একটু দাঁড়াও, আমি এখনই তোমাকে কল দিতেছি। একটুও মন খারাপ কইরো না। ❤️")
                return jsonify({"status": "emergency"}), 200

            # === নিয়ম ৩: নরমাল কথা হলে AI উত্তর দিবে ===
            if automation_active:
                reply = get_ai_reply(msg['text']['body'])
                # যদি AI ভুল করে শপিং নিয়ে কথা বলে, তাকে থামানো
                if any(word in reply.lower() for word in SHOPPING_KEYWORDS):
                    reply = "বাদ দাও তো ওইসব, চলো ফুল নিয়ে গল্প করি। তুমি জানো, গোলাপ ফুলটা তোমার মতোই সুন্দর। 🌹"
                send_whatsapp_message(WIFE_NUMBER, reply)

        except Exception as e:
            print(f"Error: {e}")
        return jsonify({"status": "ok"}), 200

@app.route("/send-auto", methods=["GET"])
def send_auto():
    """এই লিংকে হিট করলেই একটা মিষ্টি মেসেজ যাবে। এটা Cron-job দিয়ে চালাবা"""
    global automation_active
    if not automation_active:
        return "Automation বন্ধ আছে, তাই মেসেজ পাঠানো হয় নাই।"
    
    msg = random.choice(SWEET_MESSAGES)
    send_whatsapp_message(WIFE_NUMBER, msg)
    return f"পাঠানো হইছে: {msg}"

@app.route("/start", methods=["GET"])
def start_automation():
    global automation_active
    automation_active = True
    return "Automation আবার চালু হইছে!"

if __name__ == "__main__":
    app.run(port=5000, debug=True)