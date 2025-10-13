import threading
import os
from flask import Flask
import asyncio
import credenciales as crd
import peticiones_gel
import telebot
import json

# Tu clase NKbot tal cual
class NKbot:
    def __init__(self):

        self.bot = telebot.TeleBot(crd.bot_api)
        
        self.datos_comandos = self.comandos_json()
        self.comandos = [cmd['comando'] for cmd in self.datos_comandos]

        lst_comandos = [
            telebot.types.BotCommand(cmd["comando"].lower().strip().replace("/", ""), cmd["descripcion"].strip())
            for cmd in self.datos_comandos
        ]

        self.bot.set_my_commands(lst_comandos)
        self.bot.register_message_handler(self.telegram_bot, commands=self.comandos, chat_types=['private', 'group', 'supergroup'])
        self.bot.register_message_handler(self.send_file, commands=["glbr","glbr_s", "glbr_q", "glbr_x"], chat_types=['private', 'group', 'supergroup'])
        
    def comandos_json(self):
        with open('files/comandos_db.json', 'r', encoding="utf-8") as file:
            comandos = json.load(file)
        return comandos
    
    def send_file(self, message):
        mensaje = message.text.split(' ')
        comando = mensaje[0][1:]
        tags = mensaje[1:]
        
        if comando == 'glbr':
            pass

        elif comando == 'glbr_s':
            tags.append('rating:safe')

        elif comando == 'glbr_q':
            tags.append('rating:questionable')

        elif comando == 'glbr_x':
            tags.append('rating:explicit')

        else:
            self.bot.reply_to(message, "Comando inválido.")
            return
        
        contador = 1
        
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            url_file = loop.run_until_complete(peticiones_gel.main(tags))
            loop.close()

            if not url_file:
                self.bot.reply_to(message, "[!] No se encontró ninguna imagen")
                return
            
            file = url_file[0][0].lower()

            caption = f"<a href='{url_file[1][0]}'>Source</a>"
            if url_file[2][0] != '':
                caption = f"{caption} - <a href='{url_file[2][0]}'>Original Source</a>"

            if file.endswith(('.jpg', '.jpeg', '.png')):
            
                self.bot.send_photo(chat_id=message.chat.id, photo=file, caption=caption, parse_mode="HTML")
            elif file.endswith(('.gif', '.webp')):
                self.bot.send_animation(chat_id=message.chat.id, animation=file , caption=caption, parse_mode="HTML")
            elif file.endswith(('.mp4', '.webm')):
                self.bot.send_video(chat_id=message.chat.id, video=file , caption=caption , parse_mode="HTML")
            else:
                self.bot.reply_to(message, f"[!] archivo no reconocido\n{file}")

        except Exception as e:
            contador +=5
            print(f"[X] Error: {e}")
            self.bot.send_message(chat_id=message.chat.id, text=f"[X] no se puede obtener el archivo\n\nerror: {e}\n\ntags: {", ".join(tags)}")
    
    def telegram_bot(self, message):
        mensaje = message.text.split()
        comando = mensaje[0][1:]
        data = next((d for d in self.datos_comandos if d["comando"] == comando), None)
        if data:
            self.bot.send_message(chat_id=message.chat.id, text=f"{data['respuesta']}")
        

app = Flask(__name__)

def start_bot():
    while True:
        try:
            bot_instance = NKbot()
            print("[+] Bot iniciado correctamente")
            bot_instance.bot.infinity_polling(timeout=60, long_polling_timeout=5)
        except Exception as e:
            print(f"[X] Error en el bot: {e}")
            print("[!] Reiniciando bot en 5 segundos...")
            import time; time.sleep(5)

bot_thread = threading.Thread(target=start_bot, daemon=True)
bot_thread.start()

if not bot_thread.is_alive():
    bot_thread.start()

@app.route("/")
def home():
    return "[+] Bot corriendo"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
