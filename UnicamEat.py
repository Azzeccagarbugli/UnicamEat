import os
import sys
import time
import telepot
from telepot.namedtuple import ReplyKeyboardMarkup, ReplyKeyboardRemove, InlineKeyboardMarkup, InlineKeyboardButton
from settings import TOKEN, start_msg

# State for user
user_state = {}

def handle(msg):
    content_type, chat_type, chat_id = telepot.glance(msg)

    chat_id = msg['chat']['id']
    command_input = msg['text']

    if command_input == "/start" or command_input == "/start@UnicamEatBot":
        bot.sendMessage(chat_id, start_msg)

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
    bot = telepot.Bot('529147082:AAGBGqhIlRetNTszKmfPNeISYFhfRkvNEwE')
    bot.message_loop(handle)

    print('Da grandi poteri derivano grandi responsabilità...')

    while(1):
        time.sleep(10)
finally:
    os.unlink(pidfile)

