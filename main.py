from flask import Flask, request, jsonify
import requests
import hmac
import hashlib
import random
import string
import asyncio
import threading

# ─────────── Telegram ───────────
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

BOT_TOKEN = "8238701006:AAEKoGbnw8iEgv9v3aaowEIWABXc2O9cfMA"

# ─────────── Flask ───────────
app = Flask(__name__)

def generate_custom_password(random_length=4):
    characters = string.ascii_letters + string.digits
    random_part = ''.join(random.choice(characters) for _ in range(random_length)).upper()
    return f"Harimods{random_part}"

def send_request(password):
    key = b"2ee44819e9b4598845141067b281621874d0d5d7af9d8f7e00c1e54715b7d1e3"
    data_str = f"password={password}&client_type=2&source=2&app_id=100067"
    data = data_str.encode()
    signature = hmac.new(key, data, hashlib.sha256).hexdigest()

    payload = {
        'password': password,
        'client_type': "2",
        'source': "2",
        'app_id': "100067"
    }
    url = "https://ffmconnect.live.gop.garenanow.com/oauth/guest/register"
    headers = {
        'User-Agent': "GarenaMSDK/4.0.19P9(Redmi Note 8 Pro ;Android 11;en;IN;)",
        'Connection': "Keep-Alive",
        'Accept-Encoding': "gzip",
        'Authorization': "Signature " + signature
    }

    resp = requests.post(url, data=payload, headers=headers, timeout=10)
    return {
        "password_used": password,
        "signature": signature,
        "response_status": resp.status_code,
        "response": resp.text
    }, resp.status_code

# ─────────── Flask Routes ───────────
@app.route("/register", methods=["GET"])
def register():
    password = generate_custom_password()
    return jsonify(*send_request(password))

@app.route("/custom", methods=["GET"])
def custom():
    raw_query = request.query_string.decode("utf-8")  # eg: /custom?Harimods1234
    if not raw_query:
        return jsonify({"error": "Provide password like /custom?YourPassword"}), 400
    return jsonify(*send_request(raw_query))

# ─────────── Telegram Commands ───────────
async def registerg(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Generate auto password and register"""
    password = generate_custom_password()
    result, _ = send_request(password)
    msg = (
        f"🔑 Password: {result['password_used']}\n"
       # f"🖊 Signature: {result['signature'][:20]}...\n"
        f"📡 Status: {result['response_status']}\n"
        f"📦 Response: {result['response']}"
    )
    await update.message.reply_text(msg)

async def customg(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Register with custom password"""
    if not context.args:
        await update.message.reply_text("❌ Usage: /custom <password>")
        return
    password = context.args[0]
    result, _ = send_request(password)
    msg = (
        f"🔑 Password: {result['password_used']}\n"
        #f"🖊 Signature: {result['signature'][:20]}...\n"
        f"📡 Status: {result['response_status']}\n"
        f"📦 Response: {result['response']}"
    )
    await update.message.reply_text(msg)

# ─────────── Start both Flask & Telegram ───────────
def run_flask():
    app.run(host="0.0.0.0", port=1080, debug=False)

def run_telegram():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    app_tg = ApplicationBuilder().token(BOT_TOKEN).build()
    app_tg.add_handler(CommandHandler("register", registerg))
    app_tg.add_handler(CommandHandler("custom", customg))

    loop.run_until_complete(app_tg.initialize())
    loop.run_until_complete(app_tg.start())
    loop.run_until_complete(app_tg.updater.start_polling())
    loop.run_forever()

if __name__ == "__main__":
    threading.Thread(target=run_flask, daemon=True).start()
    run_telegram()
