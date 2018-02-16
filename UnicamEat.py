"""
Unicam Eat! - Telegram Bot
Author: Azzeccagarbugli (f.coppola1998@gmail.com)
        Porchetta       (clarantonio98@gmail.com)
"""
#!/usr/bin/python3.6

import os
import sys
import random
import time
import datetime

import telepot
from telepot.namedtuple import ReplyKeyboardMarkup, ReplyKeyboardRemove, InlineKeyboardMarkup

from functions import *
from settings  import *

# Days of the week
days_week = {
    # 22 is the new 42
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

    # Take instant of the message
    now = datetime.datetime.now()

    # Debug
    print("{} - Msg from {}@{}{}[{}]: \"{}{}{}\"".format(now.strftime("%d/%m %H:%M"), color.BOLD, username, color.END, str(chat_id), color.ITALIC, command_input, color.END))

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
                markup = ReplyKeyboardMarkup(keyboard = set_markup_keyboard_davak(admin_role[chat_id]))
                bot.sendMessage(chat_id, msg, parse_mode = "Markdown", reply_markup = markup)

                user_state[chat_id] = 3
        elif command_input == "Colle Paradiso":
            markup = ReplyKeyboardMarkup(keyboard = set_markup_keyboard_colleparadiso(admin_role[chat_id]))
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
                # Bot send activity for nice appaerence
                bot.sendChatAction(chat_id, "typing")

                if not dl_updated_pdf(str(user_server_canteen[chat_id]), str(user_server_day[chat_id])):
                    bot.sendMessage(chat_id, "*Il server dell'ERSU attualmente è down*, la preghiamo di riprovare più tardi", parse_mode = "Markdown", reply_markup = ReplyKeyboardRemove(remove_keyboard = True))
                    user_state[chat_id] = 0

            if user_state[chat_id] != 0:
                # Choose the right time for eat
                markup = ReplyKeyboardMarkup(keyboard = set_markup_keyboard_launch_dinnner(admin_role[chat_id], user_server_canteen[chat_id], user_server_day[chat_id]))

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
            # Bot send activity for nice appaerence
            bot.sendChatAction(chat_id, "upload_document")

            # Start the conversion
            pdfFileName = str(user_server_canteen[chat_id]) + '_' + str(user_server_day[chat_id]) + ".pdf"

            # Convert the PDF
            convert_in_txt(pdfFileName)

            bot.sendMessage(chat_id, "_Stiamo processando la tua richiesta..._", parse_mode = "Markdown", reply_markup = ReplyKeyboardRemove(remove_keyboard = True))

            if check_updated_txt(pdfFileName) == True:
                # Send the message that contain the meaning of the life
                msg_menu = advanced_read_txt(str(user_server_canteen[chat_id]), str(user_server_day[chat_id]), command_input)

                # Try to see if there is a possible error
                if "Errore!" in msg_menu:
                    msg_menu = msg_menu.replace("Errore!", fail_conversion_msg)
                    callback_name = 'notification_developer ' + str(user_server_canteen[chat_id]) + '_' + str(user_server_day[chat_id]) + ".pdf" + ".txt"
                    keyboard  = InlineKeyboardMarkup(inline_keyboard=[
                                 [dict(text = 'PDF del menù del giorno', url = get_url(user_server_canteen[chat_id], user_server_day[chat_id]))],
                                 [dict(text = "Segnala l'errore ai developer", callback_data = callback_name)]])

                    # Prints the menu in a kawaii way
                    bot.sendMessage(chat_id, msg_menu, parse_mode = "Markdown", reply_markup = keyboard)
                else:
                    # Take random number for the donation
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

    elif command_input.lower() == "questa mensa fa schifo" or command_input.lower() == "che schifo" or command_input.lower() == "siete inutili":
        bot.sendSticker(chat_id, "CAADBAADdwADzISpCY36P9nASV4cAg")
        bot.sendMessage(chat_id, "_Cikò non è d'accordo con te ma ti vuole bene lo stesso, perchè lui vuole bene a tutti_", parse_mode = "Markdown")

    else:
        bot.sendMessage(chat_id, "Il messaggio che hai inviato non è valido, prova inserendo un comando disponibile nella lista")

def on_callback_query(msg):
    """
    Return the price of a complete launch/dinner
    """
    query_id, from_id, data = telepot.glance(msg, flavor = 'callback_query')

    # Debug
    print(color.PURPLE + '[CALLBACK QUERY] Callback query:', query_id, from_id, data, color.END)

    msg_text_prices = "Studenti: 5,50€ - Non studenti: 8,00€"
    msg_text_warn = "Una segnalazione è stata inviata ai developer, grazie mille"

    if data == 'notification_prices':
        bot.answerCallbackQuery(query_id, text = msg_text_prices)
    elif 'notification_developer' in data:
        txtname = data.replace("notification_developer ", "")
        report_error(txtDir + txtname, query_id, from_id)
        bot.answerCallbackQuery(query_id, text = msg_text_warn)

def update():
    """
    Send the notification to the users
    """
    curr_time = {datetime.datetime.now().time().hour, datetime.datetime.now().time().minute}

    if today_weekend() != 0:
        write_bool("#22")
    elif get_bool() != "True":
        write_bool("False")

    # Supper or launch
    have_to_send = ""

    if curr_time == notification_launch:
        have_to_send = "Pranzo"
    elif curr_time == notification_dinner:
        have_to_send = "Cena"

    print(have_to_send)

    if have_to_send:
        #############################################
        # Controllare comunque se il server è up!!! #
        #############################################
        day = days_week[get_day(today_weekend())]

        if day != "venerdi" and day != "sabato" and day != "domenica":
            canteen = "Avack"
            msg_menu = get_menu_updated(canteen, day, have_to_send)

            if msg_menu == "Errore":
                for chat_id in admins_array:
                    bot.sendMessage(chat_id, "Si è verificato un errore all'interno di UnicamEatBot, il menù non è stato convertito correttamente", parse_mode = "Markdown")
            else:
                for chat_id in get_users_notifications(usNoDir + "user_notification_da.txt"):
                    print(color.YELLOW + "[SENDING AVACK] Sto inviando un messaggio a: " + chat_id + color.END)
                    keyboard = InlineKeyboardMarkup(inline_keyboard=[
                                [dict(text = 'PDF del menù del giorno', url = get_url(canteen, day))],
                                [dict(text = 'Offrici una birra!', url = "https://www.paypal.me/azzeccagarbugli")]])

                    # Prints the menu in a kawaii way
                    bot.sendMessage(chat_id, msg_menu, parse_mode = "Markdown", reply_markup = keyboard)

        if (day == "sabato" or day == "domenica") and have_to_send == "Cena":
            pass
        else:
            canteen = "ColleParadiso"
            msg_menu = get_menu_updated(canteen, day, have_to_send)

            if msg_menu == "Errore":
                for chat_id in admins_array:
                    bot.sendMessage(chat_id, "Si è verficato un errore all'interno di UnicamEat, prego controllare la funzione relativa delle notifiche", parse_mode = "Markdown")
            else:
                for chat_id in get_users_notifications(usNoDir + "user_notification_cp.txt"):
                    print(color.YELLOW + "[SENDING COLLEPARADISO] Sto inviando un messaggio a: " + chat_id + color.END)
                    keyboard = InlineKeyboardMarkup(inline_keyboard=[
                                [dict(text = 'PDF del menù del giorno', url = get_url(canteen, day))],
                                [dict(text = 'Offrici una birra!', url = "https://www.paypal.me/azzeccagarbugli")]])

                    # Prints the menu in a kawaii way
                    bot.sendMessage(chat_id, msg_menu, parse_mode = "Markdown", reply_markup = keyboard)

    time.sleep(60)

# Main
print(color.BOLD + "Starting Unicam Eat!...\n", color.END)

# PID file
pid = str(os.getpid())
pidfile = "/tmp/unicameat.pid"

# Check if PID exist
if os.path.isfile(pidfile):
    print(("{}[PID PROCESS] {} already exists, exiting!{}").format(color.RED, pidfile, color.END))
    sys.exit()

# Create PID file
f = open(pidfile, 'w')
f.write(pid)

# Create the directory if it dosen't exist
if not os.path.exists(pdfDir):
    print(color.DARKCYAN + "[DIRECTORY] I'm creating this folder of the PDF for you. Stupid human." + color.END)
    os.makedirs(pdfDir)
if not os.path.exists(txtDir):
    print(color.DARKCYAN + "[DIRECTORY] I'm creating this folder of the Text Output for you. Stupid human." + color.END)
    os.makedirs(txtDir)
if not os.path.exists(boolDir):
    print(color.DARKCYAN + "[DIRECTORY] I'm creating this folder of the Boolean Value for you. Stupid human." + color.END)
    os.makedirs(boolDir)
if not os.path.exists(logDir):
    print(color.DARKCYAN + "[DIRECTORY] I'm creating this folder of the Log Info for you. Stupid human." + color.END)
    os.makedirs(logDir)
if not os.path.exists(usNoDir):
    print(color.DARKCYAN + "[DIRECTORY] I'm creating this folder of the User Notification for you. Stupid human." + color.END)
    os.makedirs(usNoDir)

# Create the file for the notification
if not os.path.isfile(usNoDir + "user_notification_cp.txt"):
    f = open(usNoDir + "user_notification_cp.txt", "w")
    f.close()

if not os.path.isfile(usNoDir + "user_notification_da.txt"):
    f = open(usNoDir + "user_notification_da.txt", "w")
    f.close()

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

    # Notification system
    while(1):
        update()
finally:
    os.unlink(pidfile)
