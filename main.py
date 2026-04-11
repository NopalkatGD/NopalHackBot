from flask import Flask, request, Response
import time
import telegram_config as NHbot
import os
import telebot.types

app = Flask(__name__)

bot_instance = NHbot.TelegramConfig()
bot = bot_instance.bot

WEBHOOK_URL = os.environ.get("WEBHOOK_URL", "https://nopalhackbot.onrender.com")
WEBHOOK_PATH = os.environ.get("WEBHOOK_PATH", "/webhook")

if WEBHOOK_URL:
    bot.remove_webhook()
    time.sleep(1)
    bot.set_webhook(url=WEBHOOK_URL + WEBHOOK_PATH)
    print(f"[+] Webhook configurado: {WEBHOOK_URL + WEBHOOK_PATH}")

@app.route(WEBHOOK_PATH, methods=["POST"])
def webhook():
    update = telebot.types.Update.de_json(request.get_json())
    bot.process_new_updates([update])
    return Response("OK", status=200)

@app.route("/")
def home():
    return "[+] Bot corriendo con webhook"

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, use_reloader=False)