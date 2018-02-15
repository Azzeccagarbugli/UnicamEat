"""
Unicam Eat! - Telegram Bot
Author: Azzeccagarbugli (f.coppola1998@gmail.com)
        Porchetta        (clarantonio98@gmail.com)
"""
#!/usr/bin/python3.6

import os
import sys
import filecmp
import random

import requests

import time
import datetime

import telepot
from telepot.namedtuple import ReplyKeyboardMarkup, ReplyKeyboardRemove, InlineKeyboardMarkup

from io import StringIO
#22
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfpage import PDFPage

from settings import *

# Days of the week (call me genius :3)
days_week = {
    "Lunedì"    : "lunedi",
    "Martedì"   : "martedi",
    "Mercoledì" : "mercoledi",
    "Giovedì"   : "giovedi",
    "Venerdì"   : "venerdi",
    "Sabato"    : "sabato",
    "Domenica"  : "domenica"
}

# Available canteen in Camerino
canteen_unicam = {
    "D'Avack"        : "Avack",
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
    try:    admin_role[chat_id]
    except: admin_role[chat_id] = False

    # User role setting
    try:    user_state[chat_id]
    except: user_state[chat_id] = 0

    # Check what type of content was sent
    try:
        if content_type == 'text':
            command_input = msg['text']
        else:
            bot.sendMessage(chat_id, "Il messaggio che hai inviato non è valido")
    except UnboundLocalError:
        bot.sendMessage(chat_id, "Il messaggio che hai inviato non è valido")

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
        bot.sendMessage(chat_id, help_msg, parse_mode = "Markdown")

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
            delete_files_infolder(logDir)
            bot.sendMessage(chat_id, "Ho ripulito le folders *pdfDir*, *txtDir* e *logDir*.", parse_mode = "Markdown")
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
                    [dict(text = 'Costo di un pasto completo', callback_data = 'notification_prices')]])
        bot.sendPhoto(chat_id, photo = "https://i.imgur.com/BlDDpAE.png", caption = prices_msg, reply_markup = keyboard)

    # Send the warnings written by the cateens
    elif command_input == "/avvertenze" or command_input == "/avvertenze" + bot_name:
        bot.sendMessage(chat_id, warning_msg, parse_mode = "HTML")

    # Settings status
    elif command_input == "/impostazioni" or command_input == "/impostazioni" + bot_name:
        language_bot = "English"

        not_txt_cp, not_txt_da = "", ""
        if user_in_users_notifications(chat_id, "cp"):
            not_txt_cp = "Disabilita"
        else:
            not_txt_cp = "Abilita"

        if user_in_users_notifications(chat_id, "da"):
            not_txt_da = "Disabilita"
        else:
            not_txt_da = "Abilita"

        markup = ReplyKeyboardMarkup(keyboard=[
                        ["Lingua: " + language_bot],
                        ["Notifiche Colle Paradiso: " + not_txt_cp],
                        ["Notifiche D'Avack: "        + not_txt_da]])
        bot.sendMessage(chat_id, settings_msg, parse_mode = "Markdown", reply_markup = markup)

        # Set user state
        user_state[chat_id] = 1

    elif user_state[chat_id] == 1:
        if "Lingua" in command_input:
            wanted_language = command_input.replace("Lingua: ", "")
            bot.sendMessage(chat_id, "Funzione ancora non implementata", reply_markup = ReplyKeyboardRemove(remove_keyboard = True))
        elif "Notifiche" in command_input:
            wanted_notification = command_input.replace("Notifiche ", "")
            if "Colle Paradiso" in wanted_notification:
                if "Abilita" in wanted_notification:
                    bot.sendMessage(chat_id, "Le notifiche per *Colle Paradiso* sono state *abilitate*", parse_mode = "Markdown", reply_markup = ReplyKeyboardRemove(remove_keyboard = True))
                    set_users_notifications(chat_id, "cp", True)
                else:
                    bot.sendMessage(chat_id, "Le notifiche per *Colle Paradiso* sono state *disabilitate*", parse_mode = "Markdown", reply_markup = ReplyKeyboardRemove(remove_keyboard = True))
                    set_users_notifications(chat_id, "cp", False)
            elif "D'Avack" in wanted_notification:
                if "Abilita" in wanted_notification:
                    bot.sendMessage(chat_id, "Le notifiche per *D'Avack* sono state *abilitate*", parse_mode = "Markdown", reply_markup = ReplyKeyboardRemove(remove_keyboard = True))
                    set_users_notifications(chat_id, "da", True)
                else:
                    bot.sendMessage(chat_id, "Le notifiche per *D'Avack* sono state *disabilitate*", parse_mode = "Markdown", reply_markup = ReplyKeyboardRemove(remove_keyboard = True))
                    set_users_notifications(chat_id, "da", False)
        else:
            bot.sendMessage(chat_id, "Sei uno stupido bamboccio, " + username, reply_markup = ReplyKeyboardRemove(remove_keyboard = True))
        
        # Set user state
        user_state[chat_id] = 0

    # Get canteen
    elif command_input == "/menu" or command_input == "/menu" + bot_name:
        markup = ReplyKeyboardMarkup(keyboard=[
                        ["D'Avack"],
                        ["Colle Paradiso"]])

        msg = "Selezionare la mensa"
        bot.sendMessage(chat_id, msg, reply_markup = markup)

        # Set user state
        user_state[chat_id] = 2

    # Get date
    elif user_state[chat_id] == 2:
        # Canteen's stuff
        user_server_canteen[chat_id] = canteen_unicam[command_input]

        msg = "Inserisci la data"

        if command_input == "D'Avack":
            # Get the date
            day_int = today_weekend()
            # Is Canteen closed?
            if (day_int == 4 or day_int == 5 or day_int == 6) and not admin_role[chat_id]:
                bot.sendMessage(chat_id, closed_msg, parse_mode = "HTML", reply_markup = ReplyKeyboardRemove(remove_keyboard = True))

                user_state[chat_id] = 0
            else:
                markup = set_markup_keyboard_davak(chat_id)
                bot.sendMessage(chat_id, msg, parse_mode = "Markdown", reply_markup = markup)

                user_state[chat_id] = 3
        elif command_input == "Colle Paradiso":
            markup = set_markup_keyboard_colleparadiso(chat_id)
            bot.sendMessage(chat_id, msg, parse_mode = "HTML", reply_markup = markup)

            user_state[chat_id] = 3
        else:
            bot.sendMessage(chat_id, "Inserisci una mensa valida")

    # Get launch or dinner
    elif user_state[chat_id] == 3:
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
            if (user_server_day[chat_id] == "venerdi" or user_server_day[chat_id] == "sabato" or user_server_day[chat_id] == "domenica" or command_input == "domenica" or command_input == "sabato" or command_input == "venerdì") and user_server_canteen[chat_id] == "Avack":
                bot.sendMessage(chat_id, closed_msg, parse_mode = "HTML", reply_markup = ReplyKeyboardRemove(remove_keyboard = True))
                user_state[chat_id] = 0
            else:
                # Directory where put the file, and name of the file itself
                directory = directory_fcopp + "/PDF/" + str(user_server_canteen[chat_id]) + '_' + str(user_server_day[chat_id]) + '.pdf'

                bot.sendChatAction(chat_id, "typing")

                # Check the existence of the files
                url_risolution = get_url(user_server_canteen[chat_id], user_server_day[chat_id])
                request = requests.get(url_risolution)

                # Try to ping the server
                response = os.system("ping -c 1 www.ersucam.it > /dev/null")

                if response == 0:
                    # Writing pdf
                    with open(directory, 'wb') as f:
                        f.write(request.content)
                else:
                    bot.sendMessage(chat_id, "*Il server dell'ERSU attualmente è down*, la preghiamo di riprovare più tardi", parse_mode = "Markdown", reply_markup = ReplyKeyboardRemove(remove_keyboard = True))
                    user_state[chat_id] = 0

            if user_state[chat_id] != 0:
                # Choose the right time for eat
                markup = set_markup_keyboard_launch_dinnner(chat_id, user_server_canteen[chat_id], user_server_day[chat_id])

                if (user_server_day[chat_id] == "sabato" or user_server_day[chat_id] == "domenica") and user_server_canteen[chat_id] == "ColleParadiso":
                    msg = "Ti ricordiamo che durante i giorni di *Sabato* e *Domenica*, la mensa di *Colle Paradiso* rimarrà aperta solo durante "\
                          "il turno del pranzo. \nPer maggiori dettagli riguardo gli orari effettivi delle mense puoi consultare il comando /orari e non scordarti "\
                          "di prendere anche la cena!"
                elif user_server_canteen[chat_id] == "Avack":
                    msg = "Ti ricordiamo che la mensa del *D'Avack* è aperta _escluisivamente_ per il turno del pranzo"
                else:
                    msg = "Seleziona dalla lista il menù desiderato"

                bot.sendMessage(chat_id, msg, parse_mode = "Markdown", reply_markup = markup)

                # Set user state
                user_state[chat_id] = 4

        except KeyError:
            bot.sendMessage(chat_id, "Inserisci un giorno della settimana valido")

    # Print menu
    elif user_state[chat_id] == 4:
        # Check the existence of the life (see line 22)
        if command_input == "Pranzo" or command_input == "Cena":

            bot.sendChatAction(chat_id, "upload_document")

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

                        os.remove(txtDir + pdfFileName + ".txt")
                        os.rename(txtDir + "converted.txt", txtDir + pdfFileName + ".txt")

            bot.sendMessage(chat_id, "_Stiamo processando la tua richiesta..._", parse_mode = "Markdown", reply_markup = ReplyKeyboardRemove(remove_keyboard = True))

            if get_bool() == True:
                # Name of the .txt file
                txtName = txtDir + str(user_server_canteen[chat_id]) + '_' + str(user_server_day[chat_id]) + ".pdf" + ".txt"

                # Convert in the right day and the right canteen, just for good appaerence
                right_canteen = clean_canteen(user_server_canteen[chat_id])
                right_day = clean_day(user_server_day[chat_id])

                msg_menu = "🗓 - *{}* - *{}* - *{}*\n\n".format(right_canteen, right_day, command_input)

                # Check choose between launch and dinner
                out_advanced_read = advanced_read_txt(txtName, command_input)

                # Try to see if there is a possible error
                if out_advanced_read == "Errore!":
                    msg_menu += "_Carissimo utente, ci dispiace che la conversione del menù non sia andata a buon fine. Segnala gentilmente l'errore agli sviluppatori "\
                                "che provederrano a risolvere quest'ultimo_"
                    callback_name = 'notification_developer ' + str(user_server_canteen[chat_id]) + '_' + str(user_server_day[chat_id]) + ".pdf" + ".txt"
                    keyboard  = InlineKeyboardMarkup(inline_keyboard=[
                                 [dict(text = 'PDF del menù del giorno', url = get_url(user_server_canteen[chat_id], user_server_day[chat_id]))],
                                 [dict(text = "Segnala l'errore ai developer", callback_data = callback_name)]])

                    # Prints the menu in a kawaii way
                    bot.sendMessage(chat_id, msg_menu, parse_mode = "Markdown", reply_markup = keyboard)
                else:
                    msg_menu += out_advanced_read
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
                bot.sendMessage(chat_id, "I menu non sono stati ancora aggiornati sul sito dell'ERSU, la preghiamo di riprovare più tardi", reply_markup = ReplyKeyboardRemove(remove_keyboard = True))

            # Set user state
            user_state[chat_id] = 0
        else:
            bot.sendMessage(chat_id, "Inserisci un parametro valido")

    elif command_input == "Questa mensa fa schifo" or command_input == "Che schifo" or command_input == "Siete inutili":
        bot.sendSticker(chat_id, "CAADBAADdwADzISpCY36P9nASV4cAg")
        bot.sendMessage(chat_id, "_Cikò non è d'accordo con te ma ti vuole bene lo stesso, perchè lui vuole bene a tutti_", parse_mode = "Markdown")

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

    # Check today
    if day == "Oggi":
        return days_week_int[day_int]

    # Other day of the week
    days_week_normal = days_week_int[day]

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

def set_markup_keyboard_colleparadiso(chat_id):
    """
    Return the custom markup for the keyboard, based on the day of the week
    """
    # Get the day
    days_week_normal = get_day(today_weekend())

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

def set_markup_keyboard_davak(chat_id):
    """
    Return the custom markup for the keyboard, based on the day of the week
    """
    # Get the day
    days_week_normal = get_day(today_weekend())

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
    # Launch or supper based on the choose of the user
    if canteen == "ColleParadiso":
        if (day != "sabato" and day != "domenica") or admin_role[chat_id]:
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

def advanced_read_txt(textFile, launch_or_dinner = "Pranzo"):
    # Getting ready to work
    my_file = open(textFile, "r")
    out = my_file.readlines()
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

    del current_sec

    # Deletes today date
    days = ["lunedì", "martedì", "mercoledì", "giovedì", "venerdì", "sabato", "domenica"]
    for i, sec in enumerate(secs):
        for line in sec:
            for day in days:
                if day in line.lower():
                    secs.pop(i)
                    break

    # Searches for foods and prices
    secs_foods     = []
    secs_prices    = []

    for sec in secs:
        if sec[0][0].isdigit() and sec[0] != "1 Formaggino":
            secs_prices.append(sec)
        else:
            secs_foods.append(sec)

    del secs

    # IMPORTANT: This will try to understand the structure of the sections produced before
    if not foods_prices_are_ordered(secs_prices, secs_foods):
        c_secs_foods  = secs_foods[:]
        c_secs_prices = secs_prices[:]

        i1, i2 = 0, 0
        for i, (prices, foods) in enumerate(zip(c_secs_prices, c_secs_foods)):
            if len(prices) != len(foods):
                i1 = i
                break

        for i, (prices, foods) in enumerate(zip(c_secs_prices, c_secs_foods)):
            if len(prices) != len(foods) and i != i1 and i != i1+1 and i!= i1+2:
                i2 = i
                break

        if i1 != 0 and i2 != 0:
            c_secs_prices[i1:i1+3], c_secs_prices[i2:i2+3] = c_secs_prices[i2:i2+3], c_secs_prices[i1:i1+3]
        else:
            print("Nice Shit Bro x1000000")

        if not foods_prices_are_ordered(c_secs_prices, c_secs_foods):
            print(color.CYAN + "ESITO 1: False" + color.END)

            c_secs_foods  = secs_foods[:]
            c_secs_prices = secs_prices[:]

            # Checks if we have pizza/panini at launch
            if '1,00€' in c_secs_prices[5] or '0,80€' in c_secs_prices[5]:
                # Checks if we don't have pizza/panini at dinner
                if '1,00€' in c_secs_prices[10] or '0,80€' in c_secs_prices[10]:
                    c_secs_prices[3:5], c_secs_prices[6:8] = c_secs_prices[6:8], c_secs_prices[3:5]
                    c_secs_prices[5],   c_secs_prices[6]   = c_secs_prices[6],   c_secs_prices[5]
                    c_secs_prices[6],   c_secs_prices[7]   = c_secs_prices[7],   c_secs_prices[6]

                    c_secs_foods = secs_foods[0], secs_foods[2], secs_foods[4], secs_foods[1], secs_foods[3], secs_foods[5], secs_foods[6], secs_foods[7], secs_foods[8], secs_foods[9], secs_foods[10]
                else:
                    c_secs_prices[3:6], c_secs_prices[6:8] = c_secs_prices[6:9], c_secs_prices[3:5]
                    c_secs_foods = secs_foods[0], secs_foods[2], secs_foods[4], secs_foods[1], secs_foods[3], secs_foods[5], secs_foods[6], secs_foods[7], secs_foods[8], secs_foods[9], secs_foods[10], secs_foods[11]

            # Checks if we don't have pizza/panini at dinner
            elif '1,00€' in c_secs_prices[9] or '0,80€' in c_secs_prices[9]:
                print("No pizza no party")
                c_secs_prices[2:4], c_secs_prices[5:7] = c_secs_prices[5:7], c_secs_prices[2:4]
                c_secs_prices[4],   c_secs_prices[5]   = c_secs_prices[5],   c_secs_prices[4]
                c_secs_prices[5],   c_secs_prices[6]   = c_secs_prices[6],   c_secs_prices[5]

                c_secs_foods = secs_foods[0], secs_foods[2], secs_foods[1], secs_foods[3], secs_foods[4], secs_foods[5], secs_foods[6], secs_foods[7], secs_foods[8], secs_foods[9]
            else:
                c_secs_prices[2:5], c_secs_prices[5:8] = c_secs_prices[5:8], c_secs_prices[2:5]
                c_secs_foods = secs_foods[0], secs_foods[2], secs_foods[1], secs_foods[3], secs_foods[4], secs_foods[5], secs_foods[6], secs_foods[7], secs_foods[8], secs_foods[9], secs_foods[10]

            if not foods_prices_are_ordered(c_secs_prices, c_secs_foods, more_info = True):
                print(color.CYAN + "ESITO 2: False" + color.END)
                print(color.RED + "ERRORE!!! - Non è stato possibile riordinare correttamente la lista" + color.END)

                return "Errore!"
            else:
                print(color.CYAN + "ESITO 2: True" + color.END)

                secs_foods, secs_prices = from_menu_lord(launch_or_dinner, c_secs_foods, c_secs_prices)
        else:
            print(color.CYAN + "ESITO 1: True" + color.END)

            secs_foods, secs_prices = from_menu_lord(launch_or_dinner, c_secs_foods, c_secs_prices)

    else:
        print("La lista è ordinata, strano...")

    # Creates a sorted menu without repetitions with prices and foods together
    # Tries to create a menu for launch and another for dinner
    myList = []
    for food, price in zip(secs_foods, secs_prices):
        for x, y in zip(food, price):
            if "The" in x:
                x = x.replace("The", "Tè")
            myStr = x + " - " + y
            myList.append(" ".join(myStr.split()))

    myList = sorted(list(set(myList)))

    # Freeing resources
    del secs_foods, secs_prices

    # Splits the menu into the current courses
    courses = append_courses(myList)

    # Formatting menu
    msg_menu = ""
    for course_text, course in zip(courses_texts, courses):
        msg_menu += course_text
        for el in course:
            msg_menu += "• " + el + "\n"
        msg_menu += "\n"
    msg_menu += "_Il menù potrebbe subire variazioni_"

    return msg_menu

def foods_prices_are_ordered(secs_prices, secs_foods, more_info = False):
    for i, (price, food) in enumerate(zip(secs_prices, secs_foods)):
        if len(price) != len(food):
            if more_info:
                print(color.CYAN + "C'è ancora un errore. A: " + str(i) + color.END)
                print(color.CYAN + "Dettagli:\n" + str(price) + " - " + str(food) + color.END)
            return False
    return True

# from menu get launch or dinner
def from_menu_lord(launch_or_dinner, secs_foods, secs_prices):
    moment_foods, moment_prices = [], []
    if launch_or_dinner == "Pranzo":
        if is_course(secs_foods[2]) == "Primi":
            moment_foods.extend(secs_foods[0:2])
            moment_prices.extend(secs_prices[0:2])
        else:
            moment_foods.extend(secs_foods[0:3])
            moment_prices.extend(secs_prices[0:3])

        moment_foods.extend(secs_foods[-6:-3])
        moment_prices.extend(secs_prices[-6:-3])
    else:
        if is_course(secs_foods[2]) == "Primi":
            if is_course(secs_foods[4]) == "Altro":
                moment_foods.extend(secs_foods[2:4])
                moment_prices.extend(secs_prices[2:4])
            else:
                moment_foods.extend(secs_foods[2:5])
                moment_prices.extend(secs_prices[2:5])
        else:
            if is_course(secs_foods[4]) == "Altro":
                moment_foods.extend(secs_foods[3:5])
                moment_prices.extend(secs_prices[3:5])
            else:
                moment_foods.extend(secs_foods[3:6])
                moment_prices.extend(secs_prices[3:6])

        moment_foods.extend(secs_foods[-4:-1])
        moment_prices.extend(secs_prices[-4:-1])

    return moment_foods[:], moment_prices[:]

def append_courses(my_list, dictionary = courses_dictionaries):
    courses = [[],[],[],[],[],[]]

    for el in my_list:
        for ci, course_dictionary in enumerate(dictionary):
            for word in course_dictionary:
                if word.lower() in el.lower() and "pizzaiola" not in el.lower() and el not in courses[0] and el not in courses[1] and el not in courses[2] and el not in courses[3] and el not in courses[4] and el not in courses[5]:
                    if ci >= 1: courses[ci+1].append(el)
                    else:       courses[ci].append(el)

    for el in my_list:
        if el not in courses[0] and el not in courses[1] and el not in courses[2] and el not in courses[3] and el not in courses[4] and el not in courses[5]:
            courses[1].append(el)

    return courses


def is_course(my_list, dictionary = courses_dictionaries):
    """
    LISTA:  ["past", "zupp"]
    OUT:    "Primi"
    """
    for el in my_list:
        for ci, course_dictionary in enumerate(dictionary):
            for word in course_dictionary:
                if word.lower() in el.lower():
                    if ci == 0:
                        return "Primi"
                    elif ci == 1:
                        return "Pizza/Panini"
                    elif ci == 2:
                        return "Altro"
                    elif ci == 3:
                        return "Extra"
                    elif ci == 4:
                        return "Bevande"
                    else:
                        return "Secondi"

# Function for deletion of files in a folder
def delete_files_infolder(folder_dir):
    for the_file in os.listdir(folder_dir):
        the_file_path = os.path.join(folder_dir, the_file)
        try:
            if os.path.isfile(the_file_path):
                os.unlink(the_file_path)
        except Exception as e:
            print(color.RED + "Errore nella funzione delete_files_infolder: " + e + color.END)

# Get Boolean values stored in boolFile (see settings.py)
def get_bool():
    with open(boolFile, 'r') as f:
        if f.readline() == "True":
            return True
        else:
            return False

def bool_write(bool_value):
    with open(boolFile, 'w') as f:
        f.writelines(bool_value)

def today_weekend():
    """
    Return the number of the week
    """
    return datetime.datetime.today().weekday()

def report_error(textFile, query_id, from_id):
    """
    Create error file based on this type of syntax: - log_CP_lunedi_21_febbraio_2018.txt
                                                    - log_DA_lunedi_14_febbraio_2018.txt
    """
    # Getting ready to work
    my_file = open(textFile, "r")
    out = my_file.readlines()
    my_file.close()

    # Take today date
    days = ["lunedì", "martedì", "mercoledì", "giovedì", "venerdì", "sabato", "domenica"]

    # String for the canteen and date of the error
    logname = ""
    if "Avack" in textFile:
        logname = "DA"
    else:
        logname = "CP"

    for line in out:
        for day in days:
            if day in line.lower():
                logname += "_" + line
                break

    file_name_error = "log_" + str(logname.replace(" ", "_"))

    f = open(logDir + file_name_error + ".txt", "w")
    f.write("ID della query: " + str(query_id) + "\nCHAT_ID dell'utente: " + str(from_id))
    f.close()


# chat_id, "da", "cp"
def user_in_users_notifications(chat_id, canteen):
    """
    Return the value of the boolean for the presence of the user in the text file
    """
    found = False

    for user in get_users_notifications(usNoDir + "user_notification_" + canteen + ".txt"):
        if str(chat_id) == user.replace("\n", ""):
            found = True
            break

    return found

def get_users_notifications(path):
    """
    Retrun the user that are inside the file for the notification
    """
    f = open(path, "r")
    out = f.readlines()
    f.close()

    return out

def set_users_notifications(chat_id, canteen, value):
    """
    Add or remove the chat_id of theuser from the file of the notification
    """
    if value:
        f = open(usNoDir + "user_notification_" + canteen + ".txt", "a")
        f.write(str(chat_id) + "\n")
    else:
        # Remove the chat_id from the file
        f = open(usNoDir + "user_notification_" + canteen + ".txt", "r")
        out = f.readlines()
        f.close()
        f = open(usNoDir + "user_notification_" + canteen + ".txt", "w")
        for line in out:
            if str(chat_id) + "\n" != line:
                f.write(line)
    f.close()

def on_callback_query(msg):
    """
    Return the price of a complete launch/dinner
    """
    query_id, from_id, data = telepot.glance(msg, flavor = 'callback_query')

    # Debug
    print(color.PURPLE + 'Callback query:', query_id, from_id, data, color.END)

    msg_text_prices = "Studenti: 5,50€ - Non studenti: 8,00€"
    msg_text_warn = "Una segnalazione è stata inviata ai developer, grazie mille"

    print(data)

    if data == 'notification_prices':
        bot.answerCallbackQuery(query_id, text = msg_text_prices)
    elif 'notification_developer' in data:
        txtname = data.replace("notification_developer ", "")
        report_error(txtDir + txtname, query_id, from_id)
        bot.answerCallbackQuery(query_id, text = msg_text_warn)

def update():
    """
    Send the notificationto the users
    """
    curr_time = {datetime.datetime.now().time().hour, datetime.datetime.now().time().minute}

    have_to_send = 0

    if curr_time == notification_launch:
        have_to_send = 1
    elif curr_time == notification_dinner:
        have_to_send = 2

    if have_to_send:
        for user in get_users_notifications(usNoDir + "user_notification_cp.txt"):
            bot.sendMessage(user, "Bravi paradisiani")
        for user in get_users_notifications(usNoDir + "user_notification_da.txt"):
            bot.sendMessage(user, "Bravi davacchini")

    time.sleep(60)

# Main
print(color.BOLD + "Starting Unicam Eat!...\n", color.END)

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
    print(color.DARKCYAN + "I'm creating this folder of the PDF for you. Stupid human." + color.END)
    os.makedirs(pdfDir)
if not os.path.exists(txtDir):
    print(color.DARKCYAN + "I'm creating this folder of the Text Output for you. Stupid human." + color.END)
    os.makedirs(txtDir)
if not os.path.exists(boolDir):
    print(color.DARKCYAN + "I'm creating this folder of the Boolean Value for you. Stupid human." + color.END)
    os.makedirs(boolDir)
if not os.path.exists(logDir):
    print(color.DARKCYAN + "I'm creating this folder of the Log Info for you. Stupid human." + color.END)
    os.makedirs(logDir)
if not os.path.exists(usNoDir):
    print(color.DARKCYAN + "I'm creating this folder of the User Notification for you. Stupid human." + color.END)
    os.makedirs(usNoDir)

# Create the file for the notification
if not os.path.isfile(usNoDir + "user_notification_cp.txt"):
    f = open(usNoDir + "user_notification_cp.txt", "w")
    f.close()

if not os.path.isfile(usNoDir + "user_notification_da.txt"):
    f = open(usNoDir + "user_notification_da.txt", "w")
    f.close()

# Take the current day
current_day = today_weekend()

# Setting boolean file
if current_day == 0:
    bool_write("True")
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

    print(color.ITALIC + '\nDa grandi poteri derivano grandi responsabilità...\n' + color.END)

    while(1):
        update()
finally:
    os.unlink(pidfile)
