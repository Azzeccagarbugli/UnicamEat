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

# State for user
user_state = {}

# Message handle funtion
def handle(msg):
    """
    This function handle all incoming messages
    """
    content_type, chat_type, chat_id = telepot.glance(msg)

    chat_id = msg['chat']['id']
    command_input = msg['text']

    if command_input == "/start" or command_input == "/start@UnicamEatBot":
        bot.sendMessage(chat_id, start_msg)

    elif command_input == "/help" or command_input == "/help@UnicamEatBot":
        bot.sendMessage(chat_id, help_msg)

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
        msg = "Inserisci la data"

        # Remove markup keyboard
        bot.sendMessage(chat_id, msg, parse_mode="Markdown", reply_markup=ReplyKeyboardRemove(remove_keyboard=True))

        # Set user state
        user_state[chat_id] = 2

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
