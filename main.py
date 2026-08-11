from flask import Flask, request, Response
import time
import os
import dotenv
import threading
import logging
from bot import telegram_bot
import telebot.types

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)

dotenv.load_dotenv()

app = Flask(__name__)

bot_instance = telegram_bot.TelegramBot(os.environ.get("BOT_API_TOKEN"))
bot = bot_instance.bot

WEBHOOK_URL = os.environ.get("WEBHOOK_URL", "")
WEBHOOK_PATH = os.environ.get("WEBHOOK_PATH", "/webhook")

if WEBHOOK_URL:
    bot.remove_webhook()
    time.sleep(1)
    bot.set_webhook(url=WEBHOOK_URL + WEBHOOK_PATH)
    print(f"[+] Webhook configurado: {WEBHOOK_URL + WEBHOOK_PATH}")
    webhook_info = bot.get_webhook_info()
    print(f"[i] Webhook info: url={webhook_info.url}, pending_update_count={webhook_info.pending_update_count}")
else:
    print("[i] WEBHOOK_URL no definida. Usando polling local.")
    bot.remove_webhook()
    time.sleep(1)
    flask_thread = threading.Thread(target=lambda: app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), use_reloader=False), daemon=True)
    flask_thread.start()
    bot.infinity_polling()

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
    if WEBHOOK_URL:
        app.run(host="0.0.0.0", port=port, use_reloader=False)
