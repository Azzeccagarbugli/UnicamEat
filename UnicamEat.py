"""
Unicam Eat! - Telegram Bot
Author: Azzeccaggarbugli (f.coppola1998@gmail.com)
        Porchetta (clarantonio98@gmail.com)

TO DO:
- Ottimizzazioni varie al codice
- Pranzo e cena
"""
#!/usr/bin/python3.6

import os
import sys

import filecmp

import requests

import random
#22
import time
import datetime

import telepot
from telepot.namedtuple import ReplyKeyboardMarkup, ReplyKeyboardRemove, InlineKeyboardMarkup, InlineKeyboardButton

from io import StringIO
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfpage import PDFPage

from settings import *

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

# Admin role
admin_role = {}

# Message handle funtion
def handle(msg):
    """
    This function handle all incoming messages
    """
    content_type, chat_type, chat_id = telepot.glance(msg)

    # Admin role setting
    try: admin_role[chat_id]
    except: admin_role[chat_id] = True

    # User role setting
    try: user_state[chat_id]
    except: user_state[chat_id] = 0

    # Check what type of content was sent
    try:
        if content_type == 'text':
            command_input = msg['text']
        else:
            bot.sendMessage(chat_id, "Il messaggio che hai inviato non è valido.")
    except UnboundLocalError:
        bot.sendMessage(chat_id, "Il messaggio che hai inviato non è valido.")
        pass

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

    # Debug
    print("Msg from {}@{}{}[{}]: \t\"{}{}{}\"".format(color.BOLD, username, color.END, str(chat_id), color.ITALIC, command_input, color.END))

    # Send start message
    if command_input == "/start" or command_input == "/start" + bot_name:
        bot.sendMessage(chat_id, start_msg, parse_mode = "Markdown")

    # Send help message
    elif command_input == "/help" or command_input == "/help" + bot_name:
        bot.sendMessage(chat_id, help_msg)

    # Toggle/Untoggle admin role
    elif command_input == "/admin" or command_input == "/admin" + bot_name:
        if chat_id in admins_array:
            if admin_role[chat_id]:
                admin_role[chat_id] = False
                bot.sendMessage(chat_id, "Ruolo da admin disattivato")
            else:
                admin_role[chat_id] = True
                bot.sendMessage(chat_id, "Ruolo da admin attivato")
        else:
            bot.sendMessage(chat_id, "Non disponi dei permessi per usare questo comando")

    elif command_input == "/delfiles" or command_input == "/delfiles" + bot_name:
        if chat_id in admins_array and admin_role[chat_id]:
            delete_files_infolder(pdfDir)
            delete_files_infolder(txtDir)
            bot.sendMessage(chat_id, "Ho ripulito le folders *pdfDir* e *txtDir*.", parse_mode = "Markdown")
        else:
            bot.sendMessage(chat_id, "Non disponi dei permessi per usare questo comando")

    elif command_input == "/bool" or command_input == "/bool" + bot_name:
        if chat_id in admins_array and admin_role[chat_id]:
            msg = "Il valore attuale della booleana è: *{}*".format(str(get_bool())) 
            bot.sendMessage(chat_id, msg, parse_mode = "Markdown")
        else:
            bot.sendMessage(chat_id, "Non disponi dei permessi per usare questo comando")

    # Send opening time
    elif command_input == "/orari" or command_input == "/orari" + bot_name:
        bot.sendMessage(chat_id, opening_msg, parse_mode = "HTML")

    # Send the position of the Colleparadiso's canteen
    elif command_input == "/posizione_colleparadiso" or command_input == "/posizione_colleparadiso" + bot_name:
        bot.sendLocation(chat_id, "4    3.1437097", "13.0822057")

    # Send the position of the D'Avack's canteen
    elif command_input == "/posizione_avak" or command_input == "/posizione_avak" + bot_name:
        bot.sendLocation(chat_id, "43.137908","13.0688287")

    # Send the info about the bot
    elif command_input == "/info" or command_input == "/info" + bot_name or command_input == bot_name:
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
                     [dict(text = 'GitHub', url = 'https://github.com/Azzeccagarbugli/UnicamEat'), dict(text = 'Developer', url = 'https://t.me/azzeccagarbugli')],
                     [dict(text = 'Dona una birra!', url = 'https://www.paypal.me/azzeccagarbugli')]])
        bot.sendMessage(chat_id, info_msg, parse_mode = "Markdown", reply_markup = keyboard)

    # Send the list of allergens
    elif command_input == "/allergeni" or command_input == "/allergeni" + bot_name:
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
                     [dict(text = 'PDF del Regolamento Europeo', url = 'http://www.sviluppoeconomico.gov.it/images/stories/documenti/Reg%201169-2011-UE_Etichettatura.pdf')]])
        bot.sendPhoto(chat_id, photo = "https://i.imgur.com/OfURcFz.png", caption = allergeni_msg, reply_markup = keyboard)

    # Send the list of the prices
    elif command_input == "/prezzi" or command_input == "/prezzi" + bot_name:
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
                    [dict(text = 'Costo di un pasto completo', callback_data = 'notification')]])
        bot.sendPhoto(chat_id, photo = "https://i.imgur.com/BlDDpAE.png", caption = prices_msg, reply_markup = keyboard)

    # Settings status
    elif command_input == "/impostazioni" or command_input == "/impostazioni" + bot_name:
        language_bot = "Inglese"
        notification_bot = "Abilita"
        visualiz_bot = "Minimal"

        markup = ReplyKeyboardMarkup(keyboard=[
                        ["Lingua: " + language_bot],
                        ["Notifiche: " + notification_bot],
                        ["Visualizzazione giorni: " + visualiz_bot]])
        bot.sendMessage(chat_id, settings_msg, parse_mode = "Markdown", reply_markup = markup)

    # Get canteen
    elif command_input == "/menu" or command_input == "/menu" + bot_name:
        markup = ReplyKeyboardMarkup(keyboard=[
                        ["D'Avack"],
                        ["Colle Paradiso"]])

        msg = "Selezionare la mensa"
        bot.sendMessage(chat_id, msg, reply_markup = markup)

        # Set user state
        user_state[chat_id] = 1

    # Get date
    elif user_state[chat_id] == 1:
        try:
            # Canteen's stuff
            user_server_canteen[chat_id] = canteen_unicam[command_input]

            msg = "Inserisci la data"

            if command_input == "D'Avack":
                # Check the day
                day_int = today_weekend()

                # Is Canteen closed?
                if (day_int == 4 or day_int == 5 or day_int == 6) and not admin_role[chat_id]:
                    bot.sendMessage(chat_id, closed_msg, parse_mode = "HTML", reply_markup = ReplyKeyboardRemove(remove_keyboard = True))

                    user_state[chat_id] = 0
                else:
                    # Set Markup Keyboard layout and send the message
                    markup = set_markup_keyboard_davak(chat_id, command_input)
                    bot.sendMessage(chat_id, msg, parse_mode = "HTML", reply_markup = markup)

                    # Set user state
                    user_state[chat_id] = 2
            else:
                # Set Markup Keyboard layout and send the message
                markup = set_markup_keyboard_colleparadiso(chat_id, command_input)
                bot.sendMessage(chat_id, msg, parse_mode = "HTML", reply_markup = markup)

                # Set user state
                user_state[chat_id] = 2

        except KeyError:
            bot.sendMessage(chat_id, "Inserisci una mensa valida")
            pass

    # Get launch or dinner
    elif user_state[chat_id] == 2:
        try:
            # Setting day
            if command_input == "Oggi":
                if not admin_role[chat_id]:
                    current_day = get_day(command_input)
                    user_server_day[chat_id] = days_week[current_day]
                else:
                    user_server_day[chat_id] = "lunedi"
            else:
                user_server_day[chat_id] = days_week[command_input]

            # Is D'Avack closed?
            if (user_server_day[chat_id] == "venerdi" or user_server_day[chat_id] == "sabato" or user_server_day[chat_id] == "domenica") and user_server_canteen[chat_id] == "Avack":
                bot.sendMessage(chat_id, closed_msg, parse_mode = "HTML", reply_markup = ReplyKeyboardRemove(remove_keyboard = True))
                user_state[chat_id] = 0
            else:
                # Directory where put the file, and name of the file itself
                directory = directory_fcopp + "/PDF/" + str(user_server_canteen[chat_id]) + '_' + str(user_server_day[chat_id]) + '.pdf'

                # Check the existence of the file
                url_risolution = get_url(user_server_canteen[chat_id], user_server_day[chat_id])
                request = requests.get(url_risolution)

                # Writing pdf
                with open(directory, 'wb') as f:
                    f.write(request.content)

            if user_state[chat_id] != 0:
                # Choose the right time for eat
                markup = set_markup_keyboard_launch_dinnner(chat_id, user_server_canteen[chat_id], user_server_day[chat_id])

                if (user_server_day[chat_id] == "sabato" or user_server_day[chat_id] == "domenica") and user_server_canteen[chat_id] == "ColleParadiso":
                    msg = "Ti ricordiamo che durante i giorni di *Sabato* e *Domenica*, la mensa di *Colle Paradiso* rimarrà aperta solo durante "\
                          "il turno del pranzo. \nPer maggiori dettagli riguardo gli orari effettivi delle mense puoi consultare il comando /orari e non scordarti "\
                          "di prendere anche la cena!"
                else:
                    msg = "Seleziona dalla lista il menù desiderato"

                bot.sendMessage(chat_id, msg, parse_mode = "Markdown", reply_markup = markup)

                # Set user state
                user_state[chat_id] = 3

        except KeyError:
            bot.sendMessage(chat_id, "Inserisci un giorno della settimana valido")

    # Print menu
    elif user_state[chat_id] == 3:
        # Check the existence of the life (see line 22)
        '''
        - CASO BASE [V]: zero pdf e zero txt
            - scarica il pdf
            - converte in txt
            - ottiene la stringa di testo formattata

        - CASO PRIMO [V]: c'è il pdf e ci sono i txt e non è lunedì mattina
            - scarica il pdf e lo sovrascrive
            - si salva in una stringa il nome del pdf scaricato
            - lo converte in txt rinominandolo temp
            - confronta temp con stringa.pdf.txt
                - se sono uguali non fa niente
                - se sono diversi sovrascrive

        - CASO SECONDO [V]: è lunedì mattina
            - scarica il pdf e lo sovrascrive
            - si salva in una stringa il nome del pdf scaricato
            - lo converte in txt rinominandolo temp
            - confronta temp con stringa.pdf.txt
                - se sono uguali dice che non è ancora disponibile il menù aggiornato
                - se sono diversi sovrascrive e vissero tutti felice e contenti
                    - si tiene da conto che ora sono disponibili i menù aggiornati
                    - 23:55 della domenica sera condizione ritorna falsa
        '''
        if command_input == "Pranzo" or command_input == "Cena":
            # Start the conversion
            pdfFileName = str(user_server_canteen[chat_id]) + '_' + str(user_server_day[chat_id]) + ".pdf"
            convert_in_txt(pdfFileName)

            # Check the day
            day_int = today_weekend()

            if not os.path.isfile(txtDir + pdfFileName + ".txt"):
                print(color.CYAN + "Ho aggiunto un nuovo file convertito in .txt" + color.END)

                os.rename(txtDir + "converted.txt", txtDir + pdfFileName + ".txt")
            elif day_int != 0:
                if filecmp.cmp(txtDir + "converted.txt", txtDir + pdfFileName + ".txt"):
                    print(color.CYAN + "I due file erano identici, ho cestinato converted.txt" + color.END)

                    os.remove(txtDir + "converted.txt")
                else:
                    print(color.CYAN + "I due file erano diversi ed ho voluto aggiornare con l'ultimo scaricato" + color.END)

                    os.remove(txtDir + pdfFileName + ".txt")
                    os.rename(txtDir + "converted.txt", txtDir + pdfFileName + ".txt")
            else:
                print(color.CYAN + "Controllo se ho i file aggiornati o meno..." + color.END)

                if get_bool() == False:
                    if filecmp.cmp(txtDir + "converted.txt", txtDir + pdfFileName + ".txt"):
                        print(color.CYAN + "I due file sono ancora uguali, inviato un msg di errore." + color.END)
                    else:
                        print(color.CYAN + "Ho trovato un aggiornamento ed ho sostituito il file con quello più recente" + color.END)

                        os.remove(txtDir + pdfFileName + ".txt")
                        os.rename(txtDir + "converted.txt", txtDir + pdfFileName + ".txt")

                        bool_write(True)
                else:
                    print(color.CYAN + "Dovrei avere i file aggiornati online, la booleana era True." + color.END)

                    if filecmp.cmp(txtDir + "converted.txt", txtDir + pdfFileName + ".txt"):
                        print(color.CYAN + "I due file erano identici, ho cestinato converted.txt" + color.END)

                        os.remove(txtDir + "converted.txt")
                    else:
                        print(color.CYAN + "I due file erano diversi ed ho voluto aggiornare con l'ultimo scaricato" + color.END)

                        os.remove(txtDir + "converted.txt")
                        os.rename(txtDir + "converted.txt", txtDir + pdfFileName + ".txt")

            bot.sendMessage(chat_id, "_Stiamo processando la tua richiesta..._", parse_mode = "Markdown", reply_markup = ReplyKeyboardRemove(remove_keyboard = True))

            if get_bool() == True:
                # Name of the .txt file
                txtName = txtDir + str(user_server_canteen[chat_id]) + '_' + str(user_server_day[chat_id]) + ".pdf" + ".txt"

                # Convert in the right day and the right canteen, just for good appaerence
                right_canteen = clean_canteen(user_server_canteen[chat_id])
                right_day = clean_day(user_server_day[chat_id])

                msg_menu = "*{}* - *{}* - *{}*\n\n".format(right_canteen, right_day, command_input)
                msg_menu += advanced_read_txt(txtName)

                random_donation = random.randint(0, 5)

                if random_donation:
                    keyboard = InlineKeyboardMarkup(inline_keyboard=[
                                [dict(text = 'PDF del menù del giorno', url = get_url(user_server_canteen[chat_id], user_server_day[chat_id]))]])
                else:
                    keyboard = InlineKeyboardMarkup(inline_keyboard=[
                                [dict(text = 'PDF del menù del giorno', url = get_url(user_server_canteen[chat_id], user_server_day[chat_id]))],
                                [dict(text = 'Offrici una birra!', url = "https://www.paypal.me/azzeccagarbugli")]])

                # Prints the menu in a kawaii way
                bot.sendMessage(chat_id, msg_menu, parse_mode = "Markdown", reply_markup = keyboard)
            else:
                bot.sendMessage(chat_id, "I menu non sono stati ancora aggiornati sul sito dell'ERSU, la preghiamo di riprovare più tardi.", reply_markup = ReplyKeyboardRemove(remove_keyboard = True))

            # Set user state
            user_state[chat_id] = 0
        else:
            bot.sendMessage(chat_id, "Inserisci un parametro valido")

    else:
        bot.sendMessage(chat_id, "Il messaggio che hai inviato non è valido, prova inserendo un comando disponibile nella lista")

def get_url(canteen, day):
    """
    Return the URL of the PDF
    """
    # Stuff for ERSU's Website
    URL = "http://www.ersucam.it/wp-content/uploads/mensa/menu"
    return (URL + "/" + canteen + "/" + day + ".pdf")

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
    day_int = today_weekend()

    # This fucking day
    current_day = ""

    # Check today
    if day == "Oggi":
        return days_week_int[day_int]

    # Other day of the week
    days_week_normal = days_week_int[day_int]

    return days_week_normal

def clean_canteen(canteen):
    # Available canteen in Camerino
    canteen_unicam = {
        "Avack" : "D'Avack",
        "ColleParadiso" : "Colle Paradiso"
    }

    return (canteen_unicam[canteen])

def clean_day(day):
    # Days of the week (call me genius :3)
    days_week = {
        "lunedi" : "Lunedì",
        "martedi" : "Martedì",
        "mercoledi" : "Mercoledì",
        "giovedi" : "Giovedì",
        "venerdi" : "Venerdì",
        "sabato" : "Sabato",
        "domenica" : "Domenica"
    }

    return days_week[day]

def set_markup_keyboard_colleparadiso(chat_id, day):
    """
    Return the custom markup for the keyboard, based on the day of the week
    """
    # Get the day
    days_week_normal = get_day(day)

    # Check which day is today and so set the right keyboard
    if admin_role[chat_id]:
        markup = ReplyKeyboardMarkup(keyboard=[
                        ["Lunedì"],
                        ["Martedì", "Mercoledì", "Giovedì"],
                        ["Venerdì", "Sabato", "Domenica"]])
    elif days_week_normal == "Lunedì":
        markup = ReplyKeyboardMarkup(keyboard=[
                        ["Oggi"],
                        ["Martedì", "Mercoledì", "Giovedì"],
                        ["Venerdì", "Sabato", "Domenica"]])
    elif days_week_normal == "Martedì":
        markup = ReplyKeyboardMarkup(keyboard=[
                        ["Oggi"],
                        ["Mercoledì", "Giovedì", "Venerdì"],
                        ["Sabato", "Domenica"]])
    elif days_week_normal == "Mercoledì":
        markup = ReplyKeyboardMarkup(keyboard=[
                        ["Oggi"],
                        ["Giovedì", "Venerdì"],
                        ["Sabato", "Domenica"]])
    elif days_week_normal == "Giovedì":
        markup = ReplyKeyboardMarkup(keyboard=[
                        ["Oggi"],
                        ["Venerdì", "Sabato", "Domenica"]])
    elif days_week_normal == "Venerdì":
        markup = ReplyKeyboardMarkup(keyboard=[
                        ["Oggi"],
                        ["Sabato", "Domenica"]])
    elif days_week_normal == "Sabato":
        markup = ReplyKeyboardMarkup(keyboard=[
                        ["Oggi"],
                        ["Domenica"]])
    elif days_week_normal == "Domenica":
        markup = ReplyKeyboardMarkup(keyboard=[
                        ["Oggi"]])
    else:
        print(color.RED + "Nice shit bro :)" + color.END)

    return markup

def set_markup_keyboard_davak(chat_id, day):
    """
    Return the custom markup for the keyboard, based on the day of the week
    """
    # Get the day
    days_week_normal = get_day(day)

    # Check which day is today and so set the right keyboard
    if admin_role[chat_id]:
        markup = ReplyKeyboardMarkup(keyboard=[
                        ["Lunedì"],
                        ["Martedì", "Mercoledì", "Giovedì"]])
    elif days_week_normal == "Lunedì":
        markup = ReplyKeyboardMarkup(keyboard=[
                        ["Oggi"],
                        ["Martedì", "Mercoledì", "Giovedì"]])
    elif days_week_normal == "Martedì":
        markup = ReplyKeyboardMarkup(keyboard=[
                        ["Oggi"],
                        ["Mercoledì", "Giovedì"]])
    elif days_week_normal == "Mercoledì":
        markup = ReplyKeyboardMarkup(keyboard=[
                        ["Oggi"],
                        ["Giovedì"]])
    elif days_week_normal == "Giovedì":
        markup = ReplyKeyboardMarkup(keyboard=[
                        ["Oggi"]])
    else:
        print(color.RED + "Nice shit bro :)" + color.END)

    return markup

def set_markup_keyboard_launch_dinnner(chat_id, canteen, day):
    """
    Return the custom markup for the launch and the dinner
    """
    # Day of the week
    current_day = get_day(day)

    # Check the right canteen
    # Check which day is today and so set the right keyboard
    if canteen == "ColleParadiso":
        if current_day != "sabato" and current_day != "domenica" and admin_role[chat_id]:
            markup = ReplyKeyboardMarkup(keyboard=[
                            ["Pranzo"],
                            ["Cena"]])
        else:
            markup = ReplyKeyboardMarkup(keyboard=[
                            ["Pranzo"]])
    elif canteen == "Avack":
        markup = ReplyKeyboardMarkup(keyboard=[
                        ["Pranzo"]])
    else:
        print(color.RED + "Nice shit bro :)" + color.END)

    return markup

def convert_in_txt(fname, pages = None):
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
    dic1 = ["past", "zupp", "passat", "tagliatell", "ris", "chicche", "minestron", "penn"]
    # Pizza/Panini
    dic2 = ["panin", "pizz", "crostin", "piadin"]
    # Altro
    dic3 = ["frutt", "yogurt", "contorn", "dolc", "pan", "sals"]
    # Extra
    dic4 = ["porzionat", "formaggi", "olio", "confettur", "cioccolat", "asport"]
    # Bevande
    dic5 = ["lattin", "brick", "acqua"]

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
                print(color.CYAN + "Caso 1 di disordine trovato." + color.END)
                prices[2], prices[3], prices[4], prices[5], prices[6], prices[7] = prices[5], prices[6], prices[7], prices[2], prices[3], prices[4]
                break
            elif len(prices) == 12:
                print(color.CYAN + "Caso 2 di disordine trovato." + color.END)
                prices[0], prices[1], prices[2], prices[6], prices[7], prices[8] = prices[6], prices[7], prices[8], prices[0], prices[1], prices[2]
                break

    # Checks if it has really managed to reorder the list, printing an error message in case of fail
    found = True
    i = 0
    for price, food in zip(prices, foods):
        if len(price) != len(food):
            print(color.CYAN + "C'è ancora un errore. A: " + str(i) + color.END)
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
        print(color.RED + "ERRORE!!! - Non è stato possibile riordinare correttamente la lista." + color.END)

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

# Function for deletion of files in a folder
def delete_files_infolder(dir):
    for the_file in os.listdir(dir):
        the_file_path = os.path.join(dir, the_file)
        try:
            if os.path.isfile(the_file_path):
                os.unlink(the_file_path)
        except Exception as e:
            print("Errore nella funzione delete_files_infolder: " + e)

# Get Boolean values stored in boolFile (see settings.py)
def get_bool():
    with open(boolFile, 'r') as file:
        if file.readline() == "True":
            return True
        else:
            return False

def bool_write(bool_value):
    with open(boolFile, 'w') as file:
        file.writelines(bool_value)

def today_weekend():
    """
    Return the number of the week
    """
    return datetime.datetime.today().weekday()

def on_callback_query(msg):
    """
    Return the price of a complete launch/dinner
    """
    query_id, from_id, data = telepot.glance(msg, flavor = 'callback_query')

    # Debug
    print(color.PURPLE + 'Callback query:', query_id, from_id, data, color.END)

    msg_text = "Studenti: 5,50€ - Non studenti: 8,00€"

    if data == 'notification':
        bot.answerCallbackQuery(query_id, text = msg_text)

# Main
print(color.BOLD + "Starting Unicam Eat!...", color.END)

# PID file
pid = str(os.getpid())
pidfile = "/tmp/unicameat.pid"

# Check if PID exist
if os.path.isfile(pidfile):
    print(("{}{} already exists, exiting!{}").format(color.RED, pidfile, color.END))
    sys.exit()

# Create PID file
f = open(pidfile, 'w')
f.write(pid)

# Create the directory if it dosen't exist 
if not os.path.exists(pdfDir):
    print(color.DARKCYAN + "\nI'm creating this folder of the PDF fo you. Stupid human.\n" + color.END)
    os.makedirs(pdfDir)
elif not os.path.exists(txtDir):
    print(color.DARKCYAN + "\nI'm creating this folder of the Text Output fo you. Stupid human.\n" + color.END)
    os.makedirs(txtDir)
elif not os.path.exists(boolFile):
    print(color.DARKCYAN + "\nI'm creating this folder of the Boolean Value fo you. Stupid human.\n" + color.END)    
    os.makedirs(boolFile)
else:
    print(color.DARKCYAN + "\nYou're lucky man, I will not diss you this time because all these folder are present :)\n" + color.END)

# Take the current day
current_day = today_weekend()

# Setting boolean file
if current_day == 0:
    bool_write("False")
else:
    bool_write("True")

# Start working
try:
    bot = telepot.Bot(TOKEN)

    # Checking if some messages has been sent to the bot
    updates = bot.getUpdates()
    if updates:
        last_update_id = updates[-1]['update_id']
        bot.getUpdates(offset=last_update_id+1)

    # Starting message_loop
    bot.message_loop({'chat': handle,
                      'callback_query': on_callback_query})

    print(color.ITALIC + 'Da grandi poteri derivano grandi responsabilità...\n' + color.END)

    while(1):
        time.sleep(10)
finally:
    os.unlink(pidfile)
