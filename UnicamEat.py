"""
Unicam Eat! - Telegram Bot
Author: Azzeccaggarbugli (f.coppola1998@gmail.com)

"""
#!/usr/bin/python3.6

import os
import sys

import time
from datetime import datetime, timedelta

import telepot
from telepot.namedtuple import ReplyKeyboardMarkup, ReplyKeyboardRemove, InlineKeyboardMarkup, InlineKeyboardButton

from settings import TOKEN, start_msg, help_msg

# Days of the week
days_week = { 
    "Lunedì" : 0,
    "Martedì" : 1,
    "Mercoledì" : 2,
    "Giovedì" : 3,
    "Venerdì" : 4,
    "Sabato" : 5,
    "Domenica" : 6
}

# State for user
user_state = {}

url_risolution = ""

# Message handle funtion
def handle(msg):
    """
    This function handle all incoming messages
    """
    content_type, chat_type, chat_id = telepot.glance(msg)

    chat_id = msg['chat']['id']
    
    # Stuff for ERSU's Website
    global url_risolution
    URL = "http://www.ersucam.it/wp-content/uploads/mensa/menu"

     # Check what type of content was sent
    if content_type == 'text':
        command_input = msg['text']
    else:
        bot.sendMessage(chat_id, "Il messaggio che hai inviato non è valido, prego riprovare")

    # Send start message
    if command_input == "/start" or command_input == "/start@UnicamEatBot":
        bot.sendMessage(chat_id, start_msg)

    # Send help message
    elif command_input == "/help" or command_input == "/help@UnicamEatBot":
        bot.sendMessage(chat_id, help_msg)

    # Get canteen
    elif command_input == "/seleziona_mensa" or command_input == "/seleziona_mensa@UnicamEatBot":
        markup = ReplyKeyboardMarkup(keyboard=[
                        ["D'Avack"],
                        ["Colle Paradiso"],
                    ])

        msg = "Seleziona la mensa"

        bot.sendMessage(chat_id, msg, reply_markup=markup)
        
        # Set user state
        user_state[chat_id] = 1

    elif user_state[chat_id] == 1:
        if command_input == "D'Avack":
            url_risolution = URL + "/Avack"
        elif command_input == "Colle Paradiso":
            url_risolution = URL + "/ColleParadiso"
        else:
            url_risolution = "Errore nella risoluzione dell'URL"

        markup = ReplyKeyboardMarkup(keyboard=[
                        ["Lunedì"],
                        ["Martedì"],
                        ["Mercoledì"],
                        ["Giovedì"],
                        ["Venerdì"],
                        ["Sabato"],
                        ["Domenica"]
                    ])
            
        msg = "Inserisci la data"

        # Remove markup keyboard
        bot.sendMessage(chat_id, msg, parse_mode="Markdown", reply_markup=markup)

        # Set user state
        user_state[chat_id] = 2

    elif user_state[chat_id] == 2:
        if command_input == "Lunedì":
            url_risolution = "".join([url_risolution, "/lunedi"]) 
        elif command_input == "Martedì":
            url_risolution = "".join([url_risolution, "/martedi"]) 
        elif command_input == "Mercoledì":
            url_risolution = "".join([url_risolution, "/mercoledi"]) 
        elif command_input == "Giovedi":
            url_risolution = "".join([url_risolution, "/giovedi"])
        elif command_input == "Venerdì":
            url_risolution = "".join([url_risolution, "/venerdi"])
        elif command_input == "Sabato":
            url_risolution = "".join([url_risolution, "/sabato"])
        elif command_input == "Domenica":
             url_risolution = "".join([url_risolution, "/domenica"])
        else:
            msg = "Errore nella risoluzione dell'URL"
            bot.sendMessage(chat_id, msg, reply_markup=markup)

        print(url_risolution+ " - "+str(chat_id))

        # Set user state
        user_state[chat_id] = 3

    else:
        bot.sendMessage(chat_id, "Il messaggio che hai inviato non è valido")


# Main
print("Starting Unicam Eat!...")

# PID file
pid = str(os.getpid())
pidfile = "/tmp/unicameat.pid"

# Check if PID exist
if os.path.isfile(pidfile):
    print("%s already exists, exiting!" % pidfile)
    sys.exit()

# Create PID file
f = open(pidfile, 'w')
f.write(pid)

# Start working

try:
    bot = telepot.Bot(TOKEN)
    bot.message_loop(handle)

    print('Da grandi poteri derivano grandi responsabilità...')

    while(1):
        time.sleep(10)
finally:
    os.unlink(pidfile)
