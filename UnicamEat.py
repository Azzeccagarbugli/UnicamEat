"""
Unicam Eat! - Telegram Bot
Author: Azzeccaggarbugli (f.coppola1998@gmail.com)
        Porchetta (clarantonio98@gmail.com)

TO DO:
- Ottimizzazioni varie al codice
- Pranzo e cena
- Confronto tra i file per download
- Creazione di folder output per migliore
"""
#!/usr/bin/python3.6

import os
import sys

import filecmp

import requests

import random

import time
import datetime

import telepot
from telepot.namedtuple import ReplyKeyboardMarkup, ReplyKeyboardRemove, InlineKeyboardMarkup, InlineKeyboardButton

from io import StringIO
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfpage import PDFPage

from settings import TOKEN, start_msg, help_msg, directory_fcopp, closed_msg, opening_msg, info_msg, allergeni_msg, settings_msg, prices_msg, pdfDir, txtDir

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
user_server_launch_dinner = {}
user_server_boolean = {}

# Message handle funtion
def handle(msg):
    """
    This function handle all incoming messages
    """
    content_type, chat_type, chat_id = telepot.glance(msg)

    # Get the chat_id
    chat_id = msg['chat']['id']

    # Check what type of content was sent
    if content_type == 'text':
        command_input = msg['text']
    else:
        bot.sendMessage(chat_id, "Il messaggio che hai inviato non è valido, prego riprovare")

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

    # Send start message
    if command_input == "/start" or command_input == "/start@UnicamEatBot":
        bot.sendMessage(chat_id, start_msg, parse_mode = "Markdown")

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
                     [dict(text = 'Dona', url = 'https://github.com')]])
        bot.sendMessage(chat_id, info_msg, reply_markup = keyboard)

    # Send the list of allergens
    elif command_input == "/allergeni" or command_input == "/allergeni@UnicamEatBot":
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
                     [dict(text = 'PDF del Regolamento Europeo', url = 'http://www.sviluppoeconomico.gov.it/images/stories/documenti/Reg%201169-2011-UE_Etichettatura.pdf')]])
        bot.sendPhoto(chat_id, photo = "https://i.imgur.com/OfURcFz.png", caption = allergeni_msg, reply_markup = keyboard)

    # Send the list of the prices
    elif command_input == "/prezzi" or command_input == "/prezzi@UnicamEatBot":
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
                    [dict(text = 'Costo di un pasto completo', callback_data = 'notification')]])
        bot.sendPhoto(chat_id, photo = "https://i.imgur.com/BlDDpAE.png", caption = prices_msg, reply_markup = keyboard)

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
    elif command_input == "/menu" or command_input == "/menu@UnicamEatBot":
        markup = ReplyKeyboardMarkup(keyboard=[
                        ["D'Avack"],
                        ["Colle Paradiso"],
                    ])

        msg = "Selezionare la mensa"

        bot.sendMessage(chat_id, msg, reply_markup = markup)

        # Set user state
        user_state[chat_id] = 1

    # Get date
    elif user_state[chat_id] == 1:
        # Check right canteen
        try:
            # Canteen's stuff
            user_server_canteen[chat_id] = canteen_unicam[command_input]

            msg = "Inserisci la data"

            # Markup of the keyboard
            markup = ""

            if command_input == "D'Avack":
                # Check the day
                day_int = datetime.datetime.today().weekday()

                if day_int == 4 or day_int == 5 or day_int == 6:
                    # Closed Canteen
                    bot.sendMessage(chat_id, closed_msg, parse_mode = "HTML", reply_markup = ReplyKeyboardRemove(remove_keyboard = True))
                else:
                    # Use the function set_markup_keyboard
                    markup = set_markup_keyboard_davak(command_input)

                    # Debug
                    print(user_server_canteen[chat_id]+ " - " + str(chat_id) + " - " +full_name)

                    # Set Markup Keyboard layout and send the message
                    bot.sendMessage(chat_id, msg, parse_mode = "HTML", reply_markup = markup)

                    # Set user state
                    user_state[chat_id] = 2
            else:
                # Use the function set_markup_keyboard
                markup = set_markup_keyboard_colleparadiso(command_input)

                # Debug
                print(user_server_canteen[chat_id]+ " - " + str(chat_id) + " - " +full_name)

                # Set Markup Keyboard layout and send the message
                bot.sendMessage(chat_id, msg, parse_mode = "HTML", reply_markup = markup)

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
            if (user_server_day[chat_id] == "venerdi" or user_server_day[chat_id] == "sabato" or user_server_day[chat_id] == "domenica") and user_server_canteen[chat_id] == "Avack":
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
                directory = directory_fcopp + "/PDF/" + str(user_server_canteen[chat_id]) + '_' + str(user_server_day[chat_id]) + '.pdf'

                # Check the existence of the file
                request = requests.get(url_risolution)
                with open(directory, 'wb') as f:
                    f.write(request.content)

            # Choose the right time for eat
            markup = set_markup_keyboard_launch_dinnner(user_server_canteen[chat_id])

            msg = "Seleziona dalla lista il menù desiderato"

            bot.sendMessage(chat_id, msg, reply_markup = markup)

            # Set user state
            user_state[chat_id] = 3

        except KeyError:
            bot.sendMessage(chat_id, "Inserisci un giorno della settimana valido")
            pass

    elif user_state[chat_id] == 3:
        # A lot of things
        try:
            if command_input == "Pranzo" or command_input == "Cena":
                # Convert PDF into txt fileExtension
                # -------------------------------------
                # Start the conversion
                pdfFileName = str(user_server_canteen[chat_id]) + '_' + str(user_server_day[chat_id]) + ".pdf"
                convert(pdfFileName)
                # -------------------------------------

                # Check the day
                #day_int = datetime.datetime.today().weekday()
                day_int = 0
                # Check the existence of the life
                # -------------------------------------

                user_server_boolean[chat_id] = False

                if(os.path.isfile(txtDir + pdfFileName + ".txt") == False):
                    print("Ho aggiunto un nuovo file convertito in txt")
                    os.rename(txtDir + "converted.txt", txtDir + pdfFileName + ".txt")
                elif day_int != 0:
                    if filecmp.cmp(txtDir + "converted.txt", txtDir + pdfFileName + ".txt"):
                        # Remove file
                        print("I due file erano identici, ho cestinato converted.txt")
                        os.remove(txtDir + "converted.txt")
                    else:
                        print("I due file erano diversi ed ho voluto aggiornare con l'ultimo scaricato")
                        # Remove file
                        os.remove(txtDir + "converted.txt")
                        # Convert the name of the file
                        os.rename(txtDir + "converted.txt", txtDir + pdfFileName + ".txt")
                else:
                    print("Controllo se ho i file aggiornati o meno")
                    if get_bool_update_menu(directory_fcopp + "/Boolean/update_menu.txt") == False:
                        if filecmp.cmp(txtDir + "converted.txt", txtDir + pdfFileName + ".txt"):
                            print("Messaggio di errore all'utente")
                            bot.sendMessage(chat_id, "I menu non sono stati aggiornati, la preghiamo di riprovare più tardi", reply_markup = ReplyKeyboardRemove(remove_keyboard = True))
                            user_server_boolean[chat_id] = True
                        else:
                            print("Ho trovato un aggiornamento ed ho sostituito il file")
                            # Remove file
                            os.remove(txtDir + "converted.txt")
                            # Convert the name of the file
                            os.rename(txtDir + "converted.txt", txtDir + pdfFileName + ".txt")

                            # Updating boolean value
                            with open(directory_fcopp + "/Boolean/update_menu.txt", 'w') as file:
                                file.writelines("1")
                    else:
                        if filecmp.cmp(txtDir + "converted.txt", txtDir + pdfFileName + ".txt"):
                            # Remove file
                            print("I due file erano identici, ho cestinato converted.txt")
                            os.remove(txtDir + "converted.txt")
                        else:
                            print("I due file erano diversi ed ho voluto aggiornare con l'ultimo scaricato")
                            # Remove file
                            os.remove(txtDir + "converted.txt")
                            # Convert the name of the file
                            os.rename(txtDir + "converted.txt", txtDir + pdfFileName + ".txt")

                if user_server_boolean[chat_id] == False:
                    # -------------------------------------
                    # Name of the .txt file
                    txtName = txtDir + str(user_server_canteen[chat_id]) + '_' + str(user_server_day[chat_id]) + ".pdf" + ".txt"

                    # Use the function advanced_read_txt() for get the menu
                    msg_menu = advanced_read_txt(txtName)

                    bot.sendMessage(chat_id, "_Stiamo processando la tua richiesta..._", parse_mode = "Markdown", reply_markup = ReplyKeyboardRemove(remove_keyboard = True))

                    # Random donation into the body of the message
                    # -------------------------------------
                    # Create the variable
                    random_var = random.randint(0, 5)
                    # -------------------------------------

                    keyboard = ""

                    if random_var:
                        keyboard = InlineKeyboardMarkup(inline_keyboard=[
                                    [dict(text = 'PDF del menù del giorno', url = get_url(user_server_canteen[chat_id], user_server_day[chat_id]))]])
                    else:
                        keyboard = InlineKeyboardMarkup(inline_keyboard=[
                                    [dict(text = 'PDF del menù del giorno', url = get_url(user_server_canteen[chat_id], user_server_day[chat_id]))],
                                    [dict(text = 'Offrici una birra!', url = "www.google.it")]])

                    # Prints the menu in a kawaii way
                    msg = bot.sendMessage(chat_id, msg_menu, parse_mode = "Markdown", reply_markup = keyboard)

                    # Set user state
                    #user_state[chat_id] = 4
            else:
                bot.sendMessage(chat_id, "Inserisci un parametro valido")

        except KeyError:
            bot.sendMessage(chat_id, "Inserisci un parametro valido")
            pass

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

def set_markup_keyboard_colleparadiso(day):
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

def set_markup_keyboard_davak(day):
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
                        ["Martedì", "Mercoledì", "Giovedì"]
                    ])
    elif days_week_normal == "Martedì":
        markup = ReplyKeyboardMarkup(keyboard=[
                        ["Oggi"],
                        ["Mercoledì", "Giovedì"]
                    ])
    elif days_week_normal == "Mercoledì":
        markup = ReplyKeyboardMarkup(keyboard=[
                        ["Oggi"],
                        ["Giovedì"]
                    ])
    elif days_week_normal == "Giovedì":
        markup = ReplyKeyboardMarkup(keyboard=[
                        ["Oggi"],
                    ])
    else:
        print("Nice shit bro :)")

    return markup

def set_markup_keyboard_launch_dinnner(canteen):
    """
    Return the custom markup for the launch and the dinner
    """
    # Markup for the custom keyboard
    markup = ""

    # Check the right canteen
    if canteen == "ColleParadiso":
        markup = ReplyKeyboardMarkup(keyboard=[
                        ["Pranzo"],
                        ["Cena"]
                    ])
    elif canteen == "Avack":
        markup = ReplyKeyboardMarkup(keyboard=[
                        ["Pranzo"]
                    ])
    else:
        # Debug
        print("Nice shit bro :)")

    return markup

'''
- Caso base: zero pdf e zero txt [V]
    - scarica il pdf
    - converte in txt
    - ottiene la stringa di testo formattata

- Secondo caso: c'è il pdf e ci sono i txt e non è lunedì mattina [ ]
    - scarica il pdf e lo sovrascrive
    - si salva in una stringa il nome del pdf scaricato
    - lo converte in txt rinominandolo temp
    - confronta temp con stringa.pdf.txt
        - se sono uguali non fa niente
        - se sono diversi sovrascrive

- Terzo caso: è lunedì mattina [ ]
    - scarica il pdf e lo sovrascrive
    - si salva in una stringa il nome del pdf scaricato
    - lo converte in txt rinominandolo temp
    - confronta temp con stringa.pdf.txt
        - se sono uguali dice che non è ancora disponibile il menù aggiornato
        - se sono diversi sovrascrive e vissero tutti felice e contenti
            - si tiene da conto che ora sono disponibili i menù aggiornati
            - 23:55 della domenica sera condizione ritorna falsa
'''
def convert(fname, pages = None):
    """
    Convert a .PDF file in a .txt file
    """
    if not pages:
        pagenums = set()
    else:
        pagenums = set(pages)

    output = StringIO()
    manager = PDFResourceManager()
    converter = TextConverter(manager, output, laparams = LAParams())
    interpreter = PDFPageInterpreter(manager, converter)

    infile = open(pdfDir+fname, 'rb')
    for page in PDFPage.get_pages(infile, pagenums):
        interpreter.process_page(page)
    infile.close()
    converter.close()
    text = output.getvalue()
    output.close()

    #textFilename = txtDir + fname + ".txt"
    textFilename = txtDir + "converted.txt"
    textFile = open(textFilename, "w")
    textFile.write(text)
    textFile.close()

def advanced_read_txt(textFile):
    # DICTIONARIES CONFIGURATION
    # Primi piatti
    dic1 = ["pasta", "zuppa", "passato", "tagliatelle", "riso", "chicche", "minestrone", "penne"]
    # Pizza/Panini
    dic2 = ["panino", "pizza", "crostini", "piadina"]
    # Altro
    dic3 = ["frutta", "yogurt", "contorno", "dolce", "pane", "salse"]
    # Extra
    dic4 = ["porzionati", "formaggi", "olio", "confettura", "cioccolat", "asporto"]
    # Bevande
    dic5 = ["lattina", "brick", "acqua"]

    # Assembling the full diciontary
    dictionaries = [dic1, dic2, dic3, dic4, dic5]


    # Opens the file .txt
    my_file = open(textFile, "r")

    # Reads lines in the .txt
    out = my_file.readlines()

    # Closes .txt
    my_file.close()

    # Divides by sections the .txt
    my_char = '\n'.encode("unicode_escape").decode("utf-8")
    secs = []
    current_sec = []

    for line in out:
        line = line.replace("\n", "\\n")
        if line.startswith(my_char) and current_sec:
            secs.append(current_sec[:])
            current_sec = []
        if not line.startswith(my_char):
            line = line.replace("\\n", "\n")
            current_sec.append(line.rstrip())

    # Deletes today date
    days = ["lunedì", "martedì", "mercoledì", "giovedì", "venerdì", "sabato", "domenica"]

    i = 0
    for sec in secs:
        for line in sec:
            for day in days:
                if day in line:
                    secs.pop(i)
                    break
        i = i + 1

    # Searches for foods and prices
    foods     = []
    prices    = []

    for sec in secs:
        if sec[0][0].isdigit() and sec[0] != "1 Formaggino":
            prices.append(sec)
        else:
            foods.append(sec)

    # Freeing resources
    del secs, current_sec

    # IMPORTANT: This will try to understand the structure of the sections produced before
    for price, food in zip(prices, foods):
        if len(price) != len(food):
            if len(prices) == 11: # CASO 1
                print("Caso 1 di disordine trovato.")
                prices[2], prices[3], prices[4], prices[5], prices[6], prices[7] = prices[5], prices[6], prices[7], prices[2], prices[3], prices[4]
                break
            elif len(prices) == 12:
                print("Caso 2 di disordine trovato.")
                prices[0], prices[1], prices[2], prices[6], prices[7], prices[8] = prices[6], prices[7], prices[8], prices[0], prices[1], prices[2]
                break

    # Checks if it has really managed to reorder the list, printing an error message in case of fail
    found = True
    i = 0
    for price, food in zip(prices, foods):
        if len(price) != len(food):
            print("C'è ancora un errore. A: " + str(i))
            found = False
            break
        i = i+1

    # Creates a sorted menu without repetitions with prices and foods together
    if found == True:
        myList = []
        for food, price in zip(foods, prices):
            for x, y in zip(food, price):
                if "The" in x:
                    x = x.replace("The", "Tè")
                myStr = x + " - " + y
                myList.append(" ".join(myStr.split()))

        myList = sorted(list(set(myList)))
    else:
        print("ERRORE! Non è stato possibile riordinare correttamente la lista.")

    # Freeing resources
    del foods, prices

    # Splits the menu into the current courses
    courses = [[],[],[],[],[],[]]
    i = 0
    for el in myList:
        for dictionary in dictionaries:
            for word in dictionary:
                if word.lower() in el.lower() and el not in courses[0] and el not in courses[1] and el not in courses[2] and el not in courses[3] and el not in courses[4] and el not in courses[5]:
                    courses[i].append(el)
            i = i+1
        i = 0
    for el in myList:
        if el not in courses[0] and el not in courses[1] and el not in courses[2] and el not in courses[3] and el not in courses[4] and el not in courses[5]:
            courses[5].append(el)

    # Correcting mistake
    courses[1], courses[2], courses[3], courses[4], courses[5] = courses[5], courses[1], courses[2], courses[3], courses[4]

    # Freeing resources
    del dictionaries

    msg_menu = ""

    courses_texts = ["*Primi:*\n", "*Secondi:*\n", "*Pizza/Panini:*\n", "*Altro:*\n", "*Extra:*\n", "*Bevande:*\n"]

    # Printing
    for course_text, course in zip(courses_texts, courses):
        msg_menu += course_text
        for el in course:
            msg_menu += "• " + el + "\n"

        msg_menu += "\n"

    msg_menu += "_Il menù potrebbe subire variazioni_"

    return msg_menu

# Boolean function
def get_bool_update_menu(fileName):
    with open(fileName, 'r') as file:
        if int(file.readline()) == 1:
            return True
        else:
            return False

def on_callback_query(msg):
    """
    Return the price of a complete launch/dinner
    """
    query_id, from_id, data = telepot.glance(msg, flavor = 'callback_query')

    # Debug
    print('Callback query:', query_id, from_id, data)

    msg_text = "Studenti: 5,50€ - Non studenti: 8,00€"

    if data == 'notification':
        bot.answerCallbackQuery(query_id, text = msg_text)

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

current_day = datetime.datetime.today().weekday()

# Setting boolean file
if current_day == 0:
    with open(directory_fcopp + "/Boolean/update_menu.txt", 'w') as file:
        file.writelines("0")
else:
    with open(directory_fcopp + "/Boolean/update_menu.txt", 'w') as file:
        file.writelines("1")

print(current_day)

# Start working
try:
    bot = telepot.Bot(TOKEN)
    bot.message_loop({'chat': handle,
                      'callback_query': on_callback_query})

    print('Da grandi poteri derivano grandi responsabilità...')

    while(1):
        time.sleep(10)
finally:
    os.unlink(pidfile)
