"""
Unicam Eat! - Telegram Bot
Author: Azzeccaggarbugli (f.coppola1998@gmail.com)

"""
#!/usr/bin/python3.6

import os
import sys

import requests

import time
import datetime

import telepot
from telepot.namedtuple import ReplyKeyboardMarkup, ReplyKeyboardRemove, InlineKeyboardMarkup, InlineKeyboardButton

from io import StringIO
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfpage import PDFPage

from settings import TOKEN, start_msg, help_msg, directory_fcopp, closed_msg, opening_msg, info_msg, allergeni_msg, settings_msg

# Days of the week (call me genius :3)
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

        # Try to save username and name
        try:
            try:
                username = msg['chat']['username']
            except:
                username = ""

            full_name = msg['chat']['first_name']
            full_name += ' ' + msg['chat']['last_name']
        except KeyError:
            pass
    else:
        bot.sendMessage(chat_id, "Il messaggio che hai inviato non è valido, prego riprovare")

    # Send start message
    if command_input == "/start" or command_input == "/start@UnicamEatBot":
        bot.sendMessage(chat_id, start_msg)

    # Send help message
    elif command_input == "/help" or command_input == "/help@UnicamEatBot":
        bot.sendMessage(chat_id, help_msg)

    # Send opening time
    elif command_input == "/orari" or command_input == "/orari@UnicamEatBot":
        bot.sendMessage(chat_id, opening_msg, parse_mode = "HTML")

    # Send the position of the Colleparadiso's canteen
    elif command_input == "/posizione_colleparadiso" or command_input == "/posizione_colleparadiso@UnicamEatBot":
        bot.sendLocation(chat_id, "43.1437097", "13.0822057")

    # Send the position of the D'Avack's canteen
    elif command_input == "/posizione_avak" or command_input == "/posizione_avak@UnicamEatBot":
        bot.sendLocation(chat_id, "43.137908","13.0688287")

    # Send the info about the bot
    elif command_input == "/info" or command_input == "/info@UnicamEatBot":
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
                     [dict(text='Dona', url='https://github.com')]])
        bot.sendMessage(chat_id, info_msg, reply_markup = keyboard)

    # Send the list of allergens
    elif command_input == "/allergeni" or command_input == "/allergeni@UnicamEatBot":
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
                     [dict(text='PDF del Regolamento Europeo', url='http://www.sviluppoeconomico.gov.it/images/stories/documenti/Reg%201169-2011-UE_Etichettatura.pdf')]])
        bot.sendPhoto(chat_id, photo = "https://i.imgur.com/OfURcFz.png", caption = allergeni_msg, reply_markup = keyboard)

    # Settings status
    elif command_input == "/impostazioni" or command_input == "/impostazioni@UnicamEatBot":
        # A lot of strange stuff
        language_bot = "Inglese"
        notification_bot = "Abilita"
        visualiz_bot = "Minimal"

        # Other strange stuff
        markup = ReplyKeyboardMarkup(keyboard=[
                        ["Lingua: " + language_bot],
                        ["Notifiche: " + notification_bot],
                        ["Visualizzazione giorni: " + visualiz_bot]    
                    ])
        bot.sendMessage(chat_id, settings_msg, parse_mode = "Markdown", reply_markup = markup)
        
    # Get canteen
    elif command_input == "/seleziona_mensa" or command_input == "/seleziona_mensa@UnicamEatBot":
        markup = ReplyKeyboardMarkup(keyboard=[
                        ["D'Avack"],
                        ["Colle Paradiso"],
                    ])

        msg = "Seleziona la mensa"

        bot.sendMessage(chat_id, msg, reply_markup = markup)
        
        # Set user state
        user_state[chat_id] = 1

    elif user_state[chat_id] == 1:
        # Check right canteen 
        try:
            # Canteen's stuff
            user_server_canteen[chat_id] = canteen_unicam[command_input]

            # Use the function set_markup_keyboard
            markup = set_markup_keyboard(command_input)

            msg = "Inserisci la data"

            # Remove markup keyboard
            bot.sendMessage(chat_id, msg, parse_mode = "HTML", reply_markup = markup)

            # Debug
            print(user_server_canteen[chat_id]+ " - " + str(chat_id) + " - " +full_name)

            # Set user state
            user_state[chat_id] = 2

        except KeyError:
            bot.sendMessage(chat_id, "Inserisci una mensa valida")
            pass
        
    elif user_state[chat_id] == 2:
        # Check day correct
        try:
            if command_input == "Oggi":
                # Current Day
                current_day = get_day(command_input)
                
                # Day's stuff
                user_server_day[chat_id] = days_week[current_day]
            else:
                # Day's stuff
                user_server_day[chat_id] = days_week[command_input]

            # D'Avack canteen is closed the friday, saturday and the sunday
            if user_server_day[chat_id] == "venerdi" and user_server_canteen[chat_id] == "Avack":
                # Debug
                print("OK! Canteen of D'Avak is closed during " + command_input + ", so don't panic")
                
                bot.sendMessage(chat_id, closed_msg, parse_mode = "HTML", reply_markup = ReplyKeyboardRemove(remove_keyboard = True))
            elif user_server_day[chat_id] == "sabato" and user_server_canteen[chat_id] == "Avack":
                # Debug
                print("OK! Canteen of D'Avak is closed during " + command_input + ", so don't panic")            
                
                bot.sendMessage(chat_id, closed_msg, parse_mode = "HTML", reply_markup = ReplyKeyboardRemove(remove_keyboard = True))
            elif user_server_day[chat_id] == "domenica" and user_server_canteen[chat_id] == "Avack":
                # Debug
                print("OK! Canteen of D'Avak is closed during " + command_input + ", so don't panic")
                
                bot.sendMessage(chat_id, closed_msg, parse_mode = "HTML", reply_markup = ReplyKeyboardRemove(remove_keyboard = True))
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

                bot.sendMessage(chat_id, url_risolution, reply_markup = ReplyKeyboardRemove(remove_keyboard = True))

                # Set user state
                user_state[chat_id] = 3
            
        except KeyError:
            bot.sendMessage(chat_id, "Inserisci un giorno della settimana valido")
            pass
    
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

def get_day(day):
    """
    Return the current day
    
    Notes:
    0 - MONDAY
    1 - TUESDAY
    2 - WEDNESDAY
    3 - THURSDAY
    4 - FRIDAY
    5 - SATURDAY
    6 - SUNDAY
    """
    # Days of the week but in numeric format
    days_week_int = {
        0 : "Lunedì",
        1 : "Martedì",
        2 : "Mercoledì",
        3 : "Giovedì",
        4 : "Venerdì",
        5 : "Sabato",
        6 : "Domenica"
    }

    # Get the day
    day_int = datetime.datetime.today().weekday()

    # This fucking day
    current_day = ""

    # Check today
    if day == "Oggi":
        current_day = days_week_int[day_int]
        return current_day
    
     # Not more int format
    days_week_normal = days_week_int[day_int]

    return days_week_normal
    
def set_markup_keyboard(day):
    """
    Return the custom markup for the keyboard, based on the day of the week
    """
    # Get the day
    days_week_normal = get_day(day)
    
    # Markup for the custom keyboard
    markup = ""

    # Check which day is today and so set the right keyboard
    if days_week_normal == "Lunedì":
        markup = ReplyKeyboardMarkup(keyboard=[
                        ["Oggi"],
                        ["Martedì", "Mercoledì", "Giovedì"],
                        ["Venerdì", "Sabato", "Domenica"]    
                    ])
    elif days_week_normal == "Martedì":
        markup = ReplyKeyboardMarkup(keyboard=[
                        ["Oggi"],
                        ["Mercoledì", "Giovedì", "Venerdì"],
                        ["Sabato", "Domenica"]
                    ])
    elif days_week_normal == "Mercoledì":
        markup = ReplyKeyboardMarkup(keyboard=[
                        ["Oggi"],
                        ["Giovedì", "Venerdì"],
                        ["Sabato", "Domenica"]
                    ])
    elif days_week_normal == "Giovedì":
        markup = ReplyKeyboardMarkup(keyboard=[
                        ["Oggi"],
                        ["Venerdì", "Sabato", "Domenica"]
                    ])
    elif days_week_normal == "Venerdì":
        markup = ReplyKeyboardMarkup(keyboard=[
                        ["Oggi"],
                        ["Sabato", "Domenica"]
                    ])
    elif days_week_normal == "Sabato":
        markup = ReplyKeyboardMarkup(keyboard=[
                        ["Oggi"],
                        ["Domenica"]
                    ])
    elif days_week_normal == "Domenica":
        markup = ReplyKeyboardMarkup(keyboard=[
                        ["Oggi"]
                    ])
    else:
        print("Nice shit bro :)")

    return markup

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

def convert_multiple(pdfDir, txtDir):
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
