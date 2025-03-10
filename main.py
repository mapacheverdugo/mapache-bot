import os
import threading
import time

import schedule
from dotenv import load_dotenv

from database import *
from libs.solotodo.solotodo import SoloTodo
from messager import TeleBotMessager
from models.process_step import ProcessStep
from models.user import User

load_dotenv()

messager = TeleBotMessager(os.getenv('TELEGRAM_BOT_API_KEY'))
solotodo = SoloTodo(messager)

@messager.message_handler(commands=['exit', 'cancel'])
def exit(message):
    chat_id = message.chat.id
    
    user = get_or_create_user(chat_id)
    user.current_step = ProcessStep.INITIAL.value
    user.save()

    messager.send_message(chat_id, "Si necesitas otra cosa, ¡aquí estaré! Recuerda que siempre puedes escribir /help para ver los comandos disponibles")


@messager.message_handler(commands=['start', 'help'])
def start(message):
    chat_id = message.chat.id

    user = get_or_create_user(chat_id)
    user.current_step = ProcessStep.INITIAL.value
    user.save()


    msgLines = [
        "¡Hola\! Soy el Mapache Bot, estos son mis comandos",
        "",
        "*Tracker precios SoloTodo*",
        "/solotodo\_add \- Añade un producto a la lista de seguimiento",
        "/solotodo\_list \- Muestra la lista de productos en seguimiento",
        "/solotodo\_remove \- Elimina un producto de la lista de seguimiento",
    ]

    messager.send_message(chat_id, "\n".join(msgLines), parse_mode='MarkdownV2')
        

@messager.message_handler(commands=['solotodo_add'])
def add(message):
    chat_id = message.chat.id
    user = get_or_create_user(chat_id)
    
    solotodo.add_start(user)

@messager.message_handler(func=lambda message: True)
def everything_else(message):
    chat_id = message.chat.id
    user = get_or_create_user(chat_id)

    if user.current_step == ProcessStep.INITIAL.value:
        start(message)
        return 

    step_first_digit = int(str(user.current_step)[:1])

    if step_first_digit == 1:
        solotodo.middle_step(message.text, user)
        

def main():
    os.system('cls' if os.name == 'nt' else 'clear')

    print("Starting bot...")

    db.close()
    db.connect()
    db.create_tables([User])

    def run_schedule():
        while True:
            schedule.run_pending()
            time.sleep(1)

    def run_messager():
        messager.poll()

    schedule_thread = threading.Thread(target=run_schedule)
    messager_thread = threading.Thread(target=run_messager)

    schedule_thread.start()
    messager_thread.start()

    schedule_thread.join()
    messager_thread.join()

    

def get_or_create_user(user_id):
    user = User.get_or_none(User.user_id == user_id)

    if user is not None:
        return user

    user = User(user_id=user_id, current_step=ProcessStep.INITIAL.value)
    user.save()
    return user
    

        


if __name__ == '__main__':
    main()