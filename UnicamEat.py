"""
Unicam Eat! - Telegram Bot
Author: Azzeccaggarbugli (f.coppola1998@gmail.com)

"""
#!/usr/bin/python3.6

import os
import sys

import requests

import time
from datetime import datetime, timedelta

import telepot
from telepot.namedtuple import ReplyKeyboardMarkup, ReplyKeyboardRemove, InlineKeyboardMarkup, InlineKeyboardButton

from io import StringIO
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfpage import PDFPage

from settings import TOKEN, start_msg, help_msg, directory_fcopp, closed_msg

# Days of the week
days_week = { 
    "Lunedì" : "lunedi",
    "Martedì" : "martedi",
    "Mercoledì" : "mercoledi",
    "Giovedì" : "giovedi",
    "Venerdì" : "venerdi",
    "Sabato" : "sabato",
    "Domenica" : "domenica"
}

# Available canteen in Camerino
canteen_unicam = {
    "D'Avack" : "Avack",
    "Colle Paradiso" : "ColleParadiso"
}

# State for user
user_state = {}

# User server state
user_server_day = {}
user_server_canteen = {}

# Message handle funtion
def handle(msg):
    """
    This function handle all incoming messages
    """
    content_type, chat_type, chat_id = telepot.glance(msg)

    chat_id = msg['chat']['id']
    
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
        user_server_canteen[chat_id] = canteen_unicam[command_input]
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

        # Debug
        print(user_server_canteen[chat_id]+ " - " + str(chat_id))

        # Set user state
        user_state[chat_id] = 2

    elif user_state[chat_id] == 2:
        user_server_day[chat_id] = days_week[command_input]

        # D'Avack canteen is closed the friday, saturday and the sunday
        if user_server_day[chat_id] == "venerdi" and user_server_canteen[chat_id] == "Avack":
            # Debug
            print("OK! Canteen of D'Avak is closed during " + command_input + ", so don't panic")
            
            bot.sendMessage(chat_id, closed_msg,  parse_mode = "HTML", reply_markup = ReplyKeyboardRemove(remove_keyboard=True))
        elif user_server_day[chat_id] == "sabato" and user_server_canteen[chat_id] == "Avack":
            # Debug
            print("OK! Canteen of D'Avak is closed during " + command_input + ", so don't panic")            
            
            bot.sendMessage(chat_id, closed_msg, parse_mode = "HTML", reply_markup = ReplyKeyboardRemove(remove_keyboard=True))
        elif user_server_day[chat_id] == "domenica" and user_server_canteen[chat_id] == "Avack":
            # Debug
            print("OK! Canteen of D'Avak is closed during " + command_input + ", so don't panic")
            
            bot.sendMessage(chat_id, closed_msg, parse_mode = "HTML", reply_markup = ReplyKeyboardRemove(remove_keyboard=True))
        else:
            # Debug
            print(user_server_day[chat_id] + " - " + str(chat_id))

            # URL's stuff
            url_risolution = get_url(user_server_canteen[chat_id], user_server_day[chat_id])
            request = ""

            # Directory where put the file, and name of the file itself
            directory = directory_fcopp + str(user_server_canteen[chat_id]) + '_' + str(user_server_day[chat_id]) + '.pdf'

            # Check the existence of the file
            if(os.path.isfile(directory) == False):
                # Download the file if is not present
                request = requests.get(url_risolution)
                with open(directory, 'wb') as f:  
                    f.write(request.content)
            else:
                print("The file already exist!")

            bot.sendMessage(chat_id, url_risolution, reply_markup = ReplyKeyboardRemove(remove_keyboard=True))

            # Set user state
            user_state[chat_id] = 3
        
    elif user_state[chat_id] == 3:
        print("LOL")
        # pdfDir = "/mnt/c/Users/fcopp/Documents/Progetti/UnicamEat/PDF/"  #mettere il percorso dove deve prendere i pdf
        # txtDir = "/mnt/c/Users/fcopp/Documents/Progetti/UnicamEat/Text/"  #mettere il percorso dove deve mettere il file txt
        # convertMultiple(pdfDir, txtDir)


    else:
        bot.sendMessage(chat_id, "Il messaggio che hai inviato non è valido")

def get_url(canteen, day):
    """
    Return the URL of the PDF
    """
    # Stuff for ERSU's Website
    URL = "http://www.ersucam.it/wp-content/uploads/mensa/menu" 
    url_risolution = URL + "/" + canteen + "/" + day + ".pdf"

    return url_risolution

def convert(fname, pages=None):
    """
    Convert a .PDF file in a .txt file
    """
    if not pages:
        pagenums = set()
    else:
        pagenums = set(pages)

    output = StringIO()
    manager = PDFResourceManager()
    converter = TextConverter(manager, output, laparams=LAParams())
    interpreter = PDFPageInterpreter(manager, converter)

    infile = open(fname, 'rb')
    for page in PDFPage.get_pages(infile, pagenums):
        interpreter.process_page(page)
    infile.close()
    converter.close()
    text = output.getvalue()
    output.close
    
    return text

def convertMultiple(pdfDir, txtDir):
    """
    Open a directory and convert, .PDF files in .txt files, inside it using convert()
    """
    if pdfDir == "": pdfDir = os.getcwd() + "\\" 
    for pdf in os.listdir(pdfDir): 
        fileExtension = pdf.split(".")[-1]
        if fileExtension == "pdf":
            pdfFilename = pdfDir + pdf
            text = convert(pdfFilename)
            textFilename = txtDir + pdf + ".txt"
            textFile = open(textFilename, "w") 
            textFile.write(text)

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
