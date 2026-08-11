import os
import telebot
import time
import random
import requests

from py_src import xml_files, corrupt_text
from apis import gelbooru_api

class TelegramBot:
    def __init__(self, token_key:str):

        #crear bot
        self.bot = telebot.TeleBot(token_key)
        xml_path = os.path.normpath(os.path.join(os.path.dirname(__file__), '..', 'src', 'bot_opts.xml'))
        if not os.path.exists(xml_path):
            xml_path = os.path.normpath(os.path.join(os.path.dirname(__file__), '..', 'bot_opts.xml'))
        self.xml_data = xml_files.XMLdata(xml_path)

        #filtrar tags
        self.tags_censuradas = self.xml_data.lst_valor_por_ruta('.//tags_censuradas/')
        self.tags_baneadas = self.xml_data.lst_valor_por_ruta('.//tags_baneadas/')

        #declarar comandos
        comandos_default = list(self.xml_data.dict_comandos('.//bot_comands/default_comands/').keys())
        comandos_gelbooru = list(self.xml_data.dict_comandos('.//bot_comands/gelbooru_comands/').keys())
        comandos_msg_mngr = list(self.xml_data.dict_comandos('.//bot_comands/message_manager/').keys())


        chat_types = ['private', 'group', 'supergroup']

        #agregar manejadores de comandos
        self.bot.register_message_handler(self.default_messages, commands=comandos_default, chat_types=chat_types)
        self.bot.register_message_handler(self.senfile, commands=comandos_gelbooru, chat_types=chat_types)
        self.bot.register_message_handler(self.dlt_message, commands=comandos_msg_mngr, chat_types=chat_types)

        #agregar comandos al bot
        comandos_telegram = []
        for xpath in [
            './/bot_comands/default_comands/',
            './/bot_comands/gelbooru_comands/',
            './/bot_comands/message_manager/'
        ]:
            datos_comandos = self.xml_data.dict_comandos(xpath)
            for comando, atributos in datos_comandos.items():
                comandos_telegram.append(
                    telebot.types.BotCommand(
                        comando.lower().strip().replace("/", ""), 
                        atributos["descripcion"].strip()
                    )
                )   
        self.bot.set_my_commands(comandos_telegram)
    
    def default_messages(self, message):
        self.bot.send_message(chat_id=message.chat.id, text='Inicializando bot')
        if random.randint(1, 100) < 18:
            bot_dialog = self.comandos.lst_valor_por_ruta('.//dialogs/Init_script/')[0]
            blackwall_text = corrupt_text.corrupt_text(bot_dialog)
            self.bot.send_message(chat_id=message.chat.id, text=f'{blackwall_text}')

    def usr_input(self, message):
        message_split = message.text.split(' ')
        comando = message_split[0][1:]
        parametros = message_split[1:]

        return comando, parametros

    #eliminar mensajes del bot
    def dlt_message(self, message):
        if not message.reply_to_message:
            self.bot.reply_to(message, "Por favor, responde a un mensaje del bot para eliminarlo.")
            return
        
        replied = message.reply_to_message
        if not replied.from_user or not replied.from_user.is_bot:
            self.bot.reply_to(message, "Solo puedes eliminar mensajes del bot.")
            return
        try:
            self.bot.delete_message(
                chat_id=message.chat.id,
                message_id=replied.message_id
            )
            self.bot.delete_message(
                chat_id=message.chat.id,
                message_id=message.message_id
            )
        except Exception as e:
            self.bot.reply_to(message, f"No se pudo borrar el mensaje.\nError: {e}")

    def senfile(self, message):
        comando, parametros = self.usr_input(message)

        censurar=False

        for tag in parametros:
            if tag in self.tags_baneadas:
                self.bot.reply_to(message, '[X] ha introducido una tag baneada, por su seguridad, se ha negado buscar el archivo en Gelbooru')
                return

        tags = parametros
        if comando == 'glbr':
            pass
        if comando == 'glbr_s':
            tags.append('-rating:explicit')
            tags.append('-rating:questionable')
        if comando == 'glbr_q':
            tags.append('rating:questionable')
        if comando == 'glbr_x':
            tags.append('rating:explicit')

        try:
            ultimo_post = None
            
            for attempt in range(5):
                time.sleep(0.3)

                gelbooru = gelbooru_api.GelbooruAPI()
                data = gelbooru.get_json(tags_lst=parametros, limit=1)

                file_url = data[0]
                post_gel_url = data[1]
                source_url = data[2]
                tags_lst = data[3]


                ultimo_post = post_gel_url
                
                if not file_url:
                    self.bot.reply_to(message, f"No se encontraron resultados para los tags proporcionados. {tags}\n{file_url}, \n{post_gel_url}, \n{source_url}, \n{tags_lst}, \n{respuesta}")
                    return
                
                tags_lst = tags_lst or []

                if any(tag in self.tags_baneadas for tag in tags_lst):
                    continue

                censurar = any(tag in self.tags_censuradas for tag in tags_lst)
                
                caption = f"<a href='{post_gel_url}'>Source</a>"
                if source_url:
                    caption += f" | <a href='{source_url}'>Original Source</a>"
                
                dict_file_types = {
                    'imagen': ['.jpg', '.jpeg', '.png'],
                    'video': ['.mp4', '.webm'],
                    'animacion': ['.gif', '.webp']
                    }
                
                try:
                    respuesta = requests.get(file_url, timeout=30)
                    if respuesta.headers.get('Content-Type').startswith('text/html'):
                        self.bot.reply_to(message, f"Gelbooru está fastidiando.\nno sé cuando van a arreglar esta mrd\n\n> Salsa: {source_url}\n> Post en Gelbooru: {post_gel_url}")
                        return

                    if file_url.endswith(tuple(dict_file_types['imagen'])):
                        self.bot.send_photo(chat_id=message.chat.id, photo=file_url, caption=caption, parse_mode="HTML", has_spoiler=censurar)
                    elif file_url.endswith(tuple(dict_file_types['video'])):
                        self.bot.send_video(chat_id=message.chat.id, video=file_url, caption=caption, parse_mode="HTML", has_spoiler=censurar)
                    elif file_url.endswith(tuple(dict_file_types['animacion'])):
                        self.bot.send_animation(chat_id=message.chat.id, animation=file_url, caption=caption, parse_mode="HTML", has_spoiler=censurar)
                    else:
                        self.bot.reply_to(message, f"El archivo encontrado no es un formato compatible.\nPost en Gelbooru: {post_gel_url}")
                    return
                except Exception as e:
                    print("=" * 50)
                    print(type(e))
                    print(e)

                    if "wrong type of the web page content" not in str(e):
                        self.bot.reply_to(message, f"Error al enviar: {e}")
                        return
                    continue
            self.bot.reply_to(message, f"No se encontró una imagen válida después de varios intentos. Intenta con otros tags.\nÚltimo post: {ultimo_post}")
            return
        
        except KeyError as e:
            self.bot.reply_to(message, f"Error al buscar la imagen: \ntags: {", ".join(parametros)}\nerror: {e}")
            return
        except Exception as e:
            self.bot.reply_to(message, f"Error inesperado: {e}")
            return

    def configurar_webhook(self, webhook_url: str):
        from telebot import types
        self.bot.remove_webhook()
        self.bot.set_webhook(url=webhook_url)
        print(f"[+] Webhook configurado: {webhook_url}")