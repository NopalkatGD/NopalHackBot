import telebot
import corrupt_text
import credenciales
import comandos_xml
import peticiones_gelbooru
import asyncio
import random


class TelegramConfig:
    def __init__(self):
        self.bot = telebot.TeleBot(credenciales.bot_token)
        self.comandos = comandos_xml.ComandosXML()

        self.tags_censuradas = self.comandos.lst_valor_por_ruta('.//tags_censuradas/')
        self.tags_baneadas = self.comandos.lst_valor_por_ruta('.//tags_baneadas/')

        comandos_default = self.comandos.dict_comandos('.//bot_comands/default_comands/')
        comandos_gelbooru = self.comandos.dict_comandos('.//bot_comands/gelbooru_comands/')
        comandos_msg_mngr = self.comandos.dict_comandos('.//bot_comands/message_manager/')

        #implementar cuando vea que todo funcione
        #comandos_blackwall = self.comandos.dict_comandos('.//bot_comands/dialogs_comands/')

        chat_types = ['private', 'group', 'supergroup']

        #comandos por defecto
        self.bot.register_message_handler(self.default_messages, commands=comandos_default, chat_types=chat_types)
        self.bot.register_message_handler(self.senfile, commands=comandos_gelbooru,chat_types=chat_types)
        self.bot.register_message_handler(self.dlt_message, commands=comandos_msg_mngr, chat_types=chat_types)

        #registrar comandos en telegram
        self.mk_comandos('.//bot_comands/default_comands/')
        self.mk_comandos('.//bot_comands/gelbooru_comands/')
        self.mk_comandos('.//bot_comands/message_manager/')

    def default_messages(self, message):
        self.bot.send_message(chat_id=message.chat.id, text='Inicializando bot')

        if random.randint(1, 100) < 18:
            bot_dialog = self.comandos.lst_valor_por_ruta('.//dialogs/Init_script/')[0]
            blackwall_text = corrupt_text.corrupt_text(bot_dialog)
            self.bot.send_message(chat_id=message.chat.id, text=f'{blackwall_text}')
        


    def search_gel_file(self, parametros:list[str]):
        loop = asyncio.new_event_loop()
        file_url, post_gel_url, source_url, tags_lst = loop.run_until_complete(peticiones_gelbooru.PeticionesGelbooru().main(parametros))
        loop.close()
        if not file_url:
            return None, None, None, None
        return file_url, post_gel_url, source_url, tags_lst
    
    def senfile(self, message):

        #tratar entradas del usuario
        comando, parametros = self.usr_input(message)
        tags = parametros
        censurar=False
        negar=False

        #comprobar si hay tags  baneadas en el parametro
        for tag in tags:
            if tag in self.tags_baneadas:
                self.bot.reply_to(message, '[X] ha introducido una tag baneada, por su seguridad, se ha negado buscar el archivo en Gelbooru')
                return

        
        #filtrar por rating
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
            
            for _ in range(5):
                file_url, post_gel_url, source_url, tags_lst = self.search_gel_file(tags)
                ultimo_post = post_gel_url
                
                if not file_url:
                    self.bot.reply_to(message, "No se encontraron resultados para los tags proporcionados.")
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

    #tratar entradas del usuario
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

    

    def mk_comandos(self, xml_xpath:str):
        datos_comandos = self.comandos.dict_comandos(xml_xpath)
        
        
        comandos_telegram = []
        comandos_lst = []
        for comando, atributos in datos_comandos.items():
            #test print
            #print(f"{comando} | {atributos}")
            #"comando" | {"descripcion":"desc", "respuesta":"resp"}
            comandos_telegram.append(telebot.types.BotCommand(comando.lower().strip().replace("/", ""), atributos["descripcion"].strip()))
            comandos_lst.append(comando.lower().strip().replace("/", ""))
        self.bot.set_my_commands(comandos_telegram)
        return comandos_lst