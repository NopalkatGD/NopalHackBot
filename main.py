from flask import Flask
import time
import telegram_config as NHbot
import os

#Usar flask para mantener el servicio activo en render
app = Flask(__name__)
def start_bot():
    while True:
        try:
            bot_instance = NHbot.TelegramConfig()
            print('[+] Inicializando Bot')
            bot_instance.bot.polling(timeout=50, long_polling_timeout=5)
        except Exception as e:
            print(f"[X] Error en el bot: {e}")
            print("[!] Reiniciando bot en 5 segundos...")
            time.sleep(5)

start_bot()
@app.route("/")
def home():
    return "[+] Bot corriendo"

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, use_reloader=False)