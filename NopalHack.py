#librerias
import json
from Bot_Config import *
import telebot
import threading

#Token
bot = telebot.TeleBot(Telegram_Token)
##############################################################################
###########################| Lista de omandos |###############################
##############################################################################
with open("DB_json/comandosDB.json","r",encoding="utf-8") as file:
    comando_datos = json.load(file)
lista_de_comandos=[
    telebot.types.BotCommand(data["NombreC"],data["DescripC"]) for data in comando_datos
]
nombres_de_comandos = [data["NombreC"] for data in comando_datos]
bot.set_my_commands(lista_de_comandos)
##############################################################################
###############################| Comandos |###################################
##############################################################################
@bot.message_handler(commands=nombres_de_comandos)
def send_command(message):
    comando = message.text[1:]
    if comando in nombres_de_comandos:
        Responder = next(data["Respuesta"] for data in comando_datos if data["NombreC"]==comando)
        bot.send_message(chat_id=message.chat.id, text=Responder,disable_web_page_preview=True)
    else:
        bot.send_message(chat_id==message.chat.id, text="comando invalido. Consulta la lista de comandos.")
##############################################################################
###############################| vucle |######################################
##############################################################################
def recibir_mensajes():
    bot.infinity_polling()
if __name__ == '__main__':
    print('Bot iniciado')
    hilo_bot = threading.Thread(name="hilo bot", target=recibir_mensajes)
    hilo_bot.start()
