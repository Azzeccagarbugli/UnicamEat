#!/usr/bin/python3.6
# -*- coding: utf-8 -*-
"""
Unicam Eat! - Telegram Bot (Main file)
Authors: Azzeccagarbugli (f.coppola1998@gmail.com)
         Porchetta       (clarantonio98@gmail.com)

TO DO:
- Implementazione di FireBase                                                              [V]
    - Modificare funzione Update()
- Modificare il codice affinché non utilizzi più la variabile admin_role                   [V]
- Migliorare gestione colori                                                               [V]
- Rendere più sensati gli user_state                                                       [V]
- Richiesta tramite query dei vari files .xml per la lettura dei menù                      []
- Implementazione della gestione generica di una mensa, for the future                     []
"""

import os
import sys
import random
import time
import datetime

import colorama
from colorama import Fore, Style

import telepot
from telepot.namedtuple import ReplyKeyboardMarkup, ReplyKeyboardRemove, InlineKeyboardMarkup

from firebase_db import Firebase
from functions import *
from settings import TOKEN, BOT_NAME, Dirs, notification_lunch, notification_dinner

# Days of the week
days_week = {
    "Lunedì": "lunedi",
    "Martedì": "martedi",
    "Mercoledì": "mercoledi",
    "Giovedì": "giovedi",
    "Venerdì": "venerdi",
    "Sabato": "sabato",
    "Domenica": "domenica"
}

# Available canteen in Camerino
canteen_unicam = {
    "D'Avack": "Avack",
    "Colle Paradiso": "ColleParadiso"
}

# State for user
user_state = {}

# User server state
user_server_day = {}
user_server_canteen = {}
user_server_lunch_dinner = {}

# Bool to check if we want to close canteens or not
canteen_closed_da = False
canteen_closed_cp = False


def handle(msg):
    """
    This function handle all incoming messages
    """
    content_type, chat_type, chat_id = telepot.glance(msg)

    # User daily utilization
    db.update_daily_users(chat_id)

    try:  # Check what type of content was sent
        if content_type == 'text':
            command_input = msg['text']
        else:
            bot.sendMessage(chat_id, "Il messaggio che hai inviato non è valido")
    except UnboundLocalError:
        bot.sendMessage(chat_id, "Il messaggio che hai inviato non è valido")

    try:  # User role setting
        user_state[chat_id]
    except KeyError:
        user_state[chat_id] = 0

    try:  # Attempting to save username and full name
        username = msg['from']['username']
    except KeyError:
        username = "Not defined"

    # Take instant of the message
    now = datetime.datetime.now()

    # Debug
    print("[UNICAM EAT BOT][{}] - Msg from {}@{}{}[{}]: \"{}{}\"".format(now.strftime("%d/%m %H:%M"), Style.BRIGHT, username.ljust(20), Style.RESET_ALL, str(chat_id), Style.DIM, command_input))

    if basic_cmds(chat_id, command_input) is True:
        pass

    # Settings status
    elif command_input == "/impostazioni" or command_input == "/impostazioni" + BOT_NAME:
        language_bot = "English"
        user_info = db.get_user(chat_id)

        not_txt_cp_l = "Abilita"
        if user_info["preferences"]["notif_cp_l"]:
            not_txt_cp_l = "Disabilita"

        not_txt_cp_d = "Abilita"
        if user_info["preferences"]["notif_cp_d"]:
            not_txt_cp_d = "Disabilita"

        not_txt_da = "Abilita"
        if user_info["preferences"]["notif_da"]:
            not_txt_da = "Disabilita"

        markup = ReplyKeyboardMarkup(keyboard=[
                        ["Lingua: " + language_bot],
                        ["Notifiche Colle Paradiso - Pranzo: " + not_txt_cp_l],
                        ["Notifiche Colle Paradiso - Cena: " + not_txt_cp_d],
                        ["Notifiche D'Avack: " + not_txt_da]])

        settings_msg = "Attraverso le impostazioni potrai cambiare diversi parametri all'interno del bot: "\
                       "\n• *Lingua*: passa dalla lingua italiana a quella inglese, o viceversa"\
                       "\n• *Notifiche*: abilita le notifiche per il menù del giorno"

        bot.sendMessage(chat_id, settings_msg, parse_mode="Markdown", reply_markup=markup)

        # Set user state
        user_state[chat_id] = 1

    elif user_state[chat_id] == 1:
        if "Lingua" in command_input:
            # Work in Progress
            # wanted_language = command_input.replace("Lingua: ", "")
            bot.sendMessage(chat_id, "Funzione ancora non implementata", reply_markup=ReplyKeyboardRemove(remove_keyboard=True))
        elif "Notifiche" in command_input:
            wanted_notification = command_input.replace("Notifiche ", "")
            if "Colle Paradiso" in wanted_notification:
                if "Pranzo" in wanted_notification:
                    if "Abilita" in wanted_notification:
                        bot.sendMessage(chat_id, "Le notifiche per *Colle Paradiso* per il turno del pranzo sono state *abilitate*", parse_mode="Markdown", reply_markup=ReplyKeyboardRemove(remove_keyboard=True))
                        db.edit_user(chat_id, "preferences/notif_cp_l", True)
                    else:
                        bot.sendMessage(chat_id, "Le notifiche per *Colle Paradiso* per il turno del pranzo sono state *disabilitate*", parse_mode="Markdown", reply_markup=ReplyKeyboardRemove(remove_keyboard=True))
                        db.edit_user(chat_id, "preferences/notif_cp_l", False)
                else:
                    if "Abilita" in wanted_notification:
                        bot.sendMessage(chat_id, "Le notifiche per *Colle Paradiso* per il turno della cena sono state *abilitate*", parse_mode="Markdown", reply_markup=ReplyKeyboardRemove(remove_keyboard=True))
                        db.edit_user(chat_id, "preferences/notif_cp_d", True)
                    else:
                        bot.sendMessage(chat_id, "Le notifiche per *Colle Paradiso* per il turno della cena sono state *disabilitate*", parse_mode="Markdown", reply_markup=ReplyKeyboardRemove(remove_keyboard=True))
                        db.edit_user(chat_id, "preferences/notif_cp_d", False)
            elif "D'Avack" in wanted_notification:
                if "Abilita" in wanted_notification:
                    bot.sendMessage(chat_id, "Le notifiche per *D'Avack* sono state *abilitate*", parse_mode="Markdown", reply_markup=ReplyKeyboardRemove(remove_keyboard=True))
                    db.edit_user(chat_id, "preferences/notif_da", True)
                else:
                    bot.sendMessage(chat_id, "Le notifiche per *D'Avack* sono state *disabilitate*", parse_mode="Markdown", reply_markup=ReplyKeyboardRemove(remove_keyboard=True))
                    db.edit_user(chat_id, "preferences/notif_da", False)
        else:
            bot.sendMessage(chat_id, "Sei uno stupido bamboccio " + username + "!", reply_markup=ReplyKeyboardRemove(remove_keyboard=True))

        # Set user state
        user_state[chat_id] = 0
    # Toggle/Untoggle admin role
    elif command_input == "/admin" or command_input == "/admin" + BOT_NAME:
        if db.get_user(chat_id)['role'] == 1:
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                         [dict(text="Invia messaggio", callback_data="cmd_send_msg"), dict(text="Chiudi mensa", callback_data="cmd_close_canteen")],
                         [dict(text="Boolean", callback_data="cmd_bool"), dict(text="Pulisci cartelle", callback_data="cmd_clean_folders")],
                         [dict(text="Grafico", callback_data="cmd_graph")]])
            bot.sendMessage(chat_id, "Seleziona un comando", parse_mode="Markdown", reply_markup=keyboard)
        else:
            bot.sendMessage(chat_id, "Non disponi dei permessi per usare questo comando")

    # Send message function
    elif user_state[chat_id] == 11:
        try:
            bot.sendMessage(chat_id, "Il testo che mi hai inviato è:\n\n" + command_input + "\n\nsta per essere inviato...", parse_mode="Markdown")

            # Tries to send the message
            for user_chat_id in db.get_all_users_id():
                bot.sendMessage(user_chat_id, command_input, parse_mode="Markdown")

            bot.sendMessage(chat_id, "_Ho inoltrato il messaggio che mi hai inviato a tutti gli utenti con successo_", parse_mode="Markdown")

            # Set user state
            user_state[chat_id] = 0
        except telepot.exception.TelegramError:
            bot.sendMessage(chat_id, "Il testo che hai inviato non è formattato bene, riprova")

    # Get canteen
    elif command_input == "/menu" or command_input == "/menu" + BOT_NAME:
        markup = ReplyKeyboardMarkup(keyboard=[
                        ["D'Avack"],
                        ["Colle Paradiso"]])

        msg = "Selezionare la mensa"
        bot.sendMessage(chat_id, msg, reply_markup=markup)

        # Set user state
        user_state[chat_id] = 21

    # Get date
    elif user_state[chat_id] == 21:
        # Canteen's stuff
        user_server_canteen[chat_id] = canteen_unicam[command_input]

        msg = "Inserisci la data"
        canteen_closed_holiday_msg = "Attualmente la mensa che hai selezionato è *chiusa*, ti preghiamo di attendere fino ad eventuali aggiornamenti"

        if command_input == "D'Avack":
            if canteen_closed_da:
                keyboard = InlineKeyboardMarkup(inline_keyboard=[
                             [dict(text="Controlla eventuali aggiornamenti", url='http://www.ersucam.it/')]])
                bot.sendMessage(chat_id, "_Stiamo controllando lo stato della mensa_", parse_mode="Markdown", reply_markup=ReplyKeyboardRemove(remove_keyboard=True))
                bot.sendMessage(chat_id, canteen_closed_holiday_msg, parse_mode="Markdown", reply_markup=keyboard)

                # Set user state
                user_state[chat_id] = 0
            else:
                # Get the date
                day_int = today_weekend()
                # Is Canteen closed?
                if day_int >= 4:
                    closed_msg = "La mensa del D'Avack nei giorni <b>Venerdì</b>, <b>Sabato</b> e <b>Domenica</b> rimane chiusa sia "\
                                 "per pranzo che per cena. Riprova a inserire il comando /menu e controlla la mensa "\
                                 "di <b>Colle Pardiso</b> per ottenere i menù da te desiderati"

                    bot.sendMessage(chat_id, closed_msg, parse_mode="HTML", reply_markup=ReplyKeyboardRemove(remove_keyboard=True))

                    user_state[chat_id] = 0
                else:
                    markup = ReplyKeyboardMarkup(keyboard=get_da_keyboard())
                    bot.sendMessage(chat_id, msg, parse_mode="Markdown", reply_markup=markup)

                    user_state[chat_id] = 22

        elif command_input == "Colle Paradiso":
            if canteen_closed_cp:
                keyboard = InlineKeyboardMarkup(inline_keyboard=[
                             [dict(text="Controlla eventuali aggiornamenti", url='http://www.ersucam.it/')]])
                bot.sendMessage(chat_id, "_Stiamo controllando lo stato della mensa_", parse_mode="Markdown", reply_markup=ReplyKeyboardRemove(remove_keyboard=True))
                bot.sendMessage(chat_id, canteen_closed_holiday_msg, parse_mode="Markdown", reply_markup=keyboard)

                # Set user state
                user_state[chat_id] = 0
            else:
                markup = ReplyKeyboardMarkup(keyboard=get_cp_keyboard())
                bot.sendMessage(chat_id, msg, parse_mode="HTML", reply_markup=markup)

                user_state[chat_id] = 22
        else:
            bot.sendMessage(chat_id, "Inserisci una mensa valida")

    # Get lunch or dinner
    elif user_state[chat_id] == 22:
        try:
            # Setting day
            if command_input == "Oggi":
                current_day = get_day(command_input)
                user_server_day[chat_id] = days_week[current_day]
            else:
                user_server_day[chat_id] = days_week[command_input]

            # Is D'Avack closed?
            if (user_server_day[chat_id] == "venerdi" or user_server_day[chat_id] == "sabato" or user_server_day[chat_id] == "domenica" or command_input == "domenica" or command_input == "sabato" or command_input == "venerdì") and user_server_canteen[chat_id] == "Avack":
                closed_msg = "La mensa del D'Avack nei giorni <b>Venerdì</b>, <b>Sabato</b> e <b>Domenica</b> rimane chiusa sia "\
                             "per pranzo che per cena. Riprova a inserire il comando /menu e controlla la mensa "\
                             "di <b>Colle Pardiso</b> per ottenere i menù da te desiderati"

                bot.sendMessage(chat_id, closed_msg, parse_mode="HTML", reply_markup=ReplyKeyboardRemove(remove_keyboard=True))
                user_state[chat_id] = 0
            else:
                # Bot send activity for nice appearence
                bot.sendChatAction(chat_id, "typing")

                if not dl_updated_pdf(str(user_server_canteen[chat_id]), str(user_server_day[chat_id])):
                    bot.sendMessage(chat_id, "*Il server dell'ERSU attualmente è down*, la preghiamo di riprovare più tardi", parse_mode="Markdown", reply_markup=ReplyKeyboardRemove(remove_keyboard=True))
                    user_state[chat_id] = 0

            if user_state[chat_id] != 0:
                # Choose the right time for eat
                markup = ReplyKeyboardMarkup(keyboard=get_launch_dinner_keyboard(user_server_canteen[chat_id], user_server_day[chat_id]))

                if (user_server_day[chat_id] == "sabato" or user_server_day[chat_id] == "domenica") and user_server_canteen[chat_id] == "ColleParadiso":
                    msg = "Ti ricordiamo che durante i giorni di *Sabato* e *Domenica*, la mensa di *Colle Paradiso* rimarrà aperta solo durante "\
                          "il turno del pranzo. \nPer maggiori dettagli riguardo gli orari effettivi delle mense puoi consultare il comando /orari e non scordarti "\
                          "di prendere anche la cena!"
                elif user_server_canteen[chat_id] == "Avack":
                    msg = "Ti ricordiamo che la mensa del *D'Avack* è aperta _esclusivamente_ per il turno del pranzo.\n"\
                          "Per maggiori dettagli riguardo gli orari effettivi delle mense puoi consultare il comando /orari"
                else:
                    msg = "Seleziona dalla lista il menù desiderato"

                bot.sendMessage(chat_id, msg, parse_mode="Markdown", reply_markup=markup)

                # Set user state
                user_state[chat_id] = 23

        except KeyError:
            bot.sendMessage(chat_id, "Inserisci un giorno della settimana valido")

    # Print menu
    elif user_state[chat_id] == 23:
        # Check the existence of the life (see line 22)
        if command_input == "Pranzo" or command_input == "Cena":
            # Bot send activity for nice appaerence
            bot.sendChatAction(chat_id, "upload_document")

            # Start the conversion
            pdfFileName = str(user_server_canteen[chat_id]) + '_' + str(user_server_day[chat_id]) + ".pdf"

            # Convert the PDF
            convert_in_txt(pdfFileName)

            bot.sendMessage(chat_id, "_Stiamo processando la tua richiesta..._", parse_mode="Markdown", reply_markup=ReplyKeyboardRemove(remove_keyboard=True))

            if check_updated_txt(pdfFileName) is True:
                # Send the message that contain the meaning of the life
                msg_menu = advanced_read_txt(str(user_server_canteen[chat_id]), str(user_server_day[chat_id]), command_input)

                # Try to see if there is a possible error
                if "Errore!" in msg_menu:
                    fail_conversion_msg = "Carissimo utente, ci dispiace che la conversione del menù non sia andata a buon fine. \n\n_Segnala gentilmente l'errore agli sviluppatori "\
                                          "che provederrano a risolvere quest'ultimo_"
                    msg_menu = msg_menu.replace("Errore!", fail_conversion_msg)

                    callback_name = 'notification_developer ' + str(user_server_canteen[chat_id]) + '_' + str(user_server_day[chat_id]) + ".pdf" + ".txt"

                    keyboard = InlineKeyboardMarkup(inline_keyboard=[
                                 [dict(text='PDF del menù del giorno', url=get_url(user_server_canteen[chat_id], user_server_day[chat_id]))],
                                 [dict(text="Segnala l'errore ai developer", callback_data=callback_name)]])

                    # Prints the menu in a kawaii way
                    bot.sendMessage(chat_id, msg_menu, parse_mode="Markdown", reply_markup=keyboard)
                else:
                    # Take random number for the donation
                    random_donation = random.randint(0, 5)

                    # qrcode_filename never used, do we need it?
                    qrcode_filename = generate_qr_code(chat_id, msg_menu, Dirs.QRCODE, str(now.strftime("%d/%m %H:%M")), str(user_server_canteen[chat_id]), command_input)

                    if random_donation and db.get_user(chat_id)['role'] == 1:
                        keyboard = InlineKeyboardMarkup(inline_keyboard=[
                                    [dict(text='Prenota con il QR Code!', callback_data='qrcode')],
                                    [dict(text='PDF del menù del giorno', url=get_url(user_server_canteen[chat_id], user_server_day[chat_id]))]])
                    elif random_donation:
                        keyboard = InlineKeyboardMarkup(inline_keyboard=[
                                    [dict(text='PDF del menù del giorno', url=get_url(user_server_canteen[chat_id], user_server_day[chat_id]))]])
                    else:
                        keyboard = InlineKeyboardMarkup(inline_keyboard=[
                                    [dict(text='PDF del menù del giorno', url=get_url(user_server_canteen[chat_id], user_server_day[chat_id]))],
                                    [dict(text='Offrici una birra!', url="https://www.paypal.me/azzeccagarbugli")]])

                    # Prints the menu in a kawaii way
                    bot.sendMessage(chat_id, msg_menu, parse_mode="Markdown", reply_markup=keyboard)
            else:
                bot.sendMessage(chat_id, "*I menu non sono stati ancora aggiornati sul sito dell'ERSU*, riprova più tardi", parse_mode="Markdown", reply_markup=ReplyKeyboardRemove(remove_keyboard=True))

            # Set user state
            user_state[chat_id] = 0
        else:
            bot.sendMessage(chat_id, "Inserisci un parametro valido")

    # Fun messages
    elif command_input.lower() == "questa mensa fa schifo" or command_input.lower() == "che schifo" or command_input.lower() == "siete inutili":
        bot.sendSticker(chat_id, "CAADBAADdwADzISpCY36P9nASV4cAg")
        bot.sendMessage(chat_id, "_Cikò non è d'accordo con te ma ti vuole bene lo stesso, perchè lui vuole bene a tutti_", parse_mode="Markdown")

    elif command_input.lower() == "cotoletta plz" or command_input.lower() == "i want cotoletta" or command_input.lower() == "give me my cotoletta":
        bot.sendSticker(chat_id, "CAADBAADegADzISpCVjpXErTcu75Ag")
        bot.sendMessage(chat_id, "_You will have your cotoletta maybe the next time, don't be offended_", parse_mode="Markdown")

    # Default message
    else:
        bot.sendMessage(chat_id, "Il messaggio che hai inviato non è valido, prova inserendo un comando disponibile nella lista")


def on_callback_query(msg):
    """
    Return the price of a complete lunch/dinner
    """
    query_id, from_id, data = telepot.glance(msg, flavor='callback_query')

    # Debug
    print(Fore.GREEN + '[CALLBACK QUERY] Callback query: ' + Fore.RESET + Style.BRIGHT + query_id, from_id, data)

    msg_text_prices = "Studenti: 5,50€ - Non studenti: 8,00€"
    msg_text_warn = "La segnalazione è stata inviata ai developer"

    if data == 'notification_prices':
        bot.answerCallbackQuery(query_id, text=msg_text_prices)

    elif 'notification_developer' in data:
        txtname = data.replace("notification_developer ", "")
        report_error(Dirs.TXT + txtname, query_id, from_id)
        bot.answerCallbackQuery(query_id, text=msg_text_warn)

    elif data == 'qrcode':
        bot.sendPhoto(from_id, photo=open(qrCodeDir + str(from_id) + "_" + "QRCode.png", 'rb'), caption="In allegato il tuo *QR Code* contenente i pasti da te selezionati", parse_mode="Markdown")
        bot.answerCallbackQuery(query_id)

    elif data == 'cmd_send_msg':
        bot.sendMessage(from_id, "Digita il testo che vorresti inoltrare a tutti gli utenti usufruitori di questo bot")

        bot.answerCallbackQuery(query_id)
        user_state[from_id] = 22

    elif data == 'cmd_close_canteen':
        global canteen_closed_da, canteen_closed_cp

        keyboard = InlineKeyboardMarkup(inline_keyboard=[
                    [dict(text="D'Avack", callback_data="cmd_close_canteen_da")],
                    [dict(text="Colle Paradiso", callback_data="cmd_close_canteen_cp")]])

        bot.editMessageText(msg_identifier=(from_id, msg['message']['message_id']), text="Seleziona la mensa", reply_markup=keyboard)
        bot.answerCallbackQuery(query_id)

    elif data == "cmd_close_canteen_da":
        global canteen_closed_da

        if canteen_closed_da:
            msg_to_admin = "Ho aperto la mensa D'Avack"
            canteen_closed_da = False
        else:
            msg_to_admin = "Ho chiuso la mensa D'Avack"
            canteen_closed_da = True

        bot.answerCallbackQuery(query_id, text=msg_to_admin)

    elif data == "cmd_close_canteen_cp":
        global canteen_closed_cp

        if canteen_closed_cp:
            msg_to_admin = "Ho aperto la mensa Colle Paradiso"
            canteen_closed_cp = False
        else:
            msg_to_admin = "Ho chiuso la mensa Colle Paradiso"
            canteen_closed_cp = True

        bot.answerCallbackQuery(query_id, text=msg_to_admin)

    elif data == 'cmd_bool':
        bot.answerCallbackQuery(query_id, text="Il valore attuale della booleana è: {}".format(str(get_bool())))

    elif data == 'cmd_clean_folders':
        delete_files_infolder(Dirs.PDF)
        delete_files_infolder(Dirs.TXT)
        delete_files_infolder(Dirs.LOG)
        bot.answerCallbackQuery(query_id, text="Ho ripulito le folders \"pdfDir\", \"txtDir\" e \"logDir\".")

    elif data == 'cmd_graph':
        bot.sendChatAction(from_id, "upload_photo")

        # Creation of the png photo to send
        graph_name = "temp_graph.png"
        create_graph(db, 31, graph_name)

        number_total_user = len(db.get_all_users_id())

        try:
            bot.sendPhoto(from_id, photo=open("temp_graph.png", 'rb'), caption="Il numero totale di utenti è: *{}*".format(str(number_total_user)), parse_mode="Markdown")
        except TypeError:
            bot.sendMessage(from_id, "Per inviare correttamente l'immagine è necessario aggiornare Telepot ad una versione maggiore della 12.6")

        os.remove(graph_name)
        bot.answerCallbackQuery(query_id)


def update():
    """
    Send the notification to the users
    """
    curr_time = {datetime.datetime.now().time().hour, datetime.datetime.now().time().minute}

    if today_weekend() != 0:
        write_bool("#22")
    elif get_bool() != "True":
        write_bool("False")

    # Supper or lunch
    have_to_send = ""

    # Error message
    err_msg = "Si è verificato un errore all'interno di UnicamEatBot, il menù non è stato convertito correttamente"

    if curr_time == notification_lunch:
        have_to_send = "Pranzo"
    elif curr_time == notification_dinner:
        have_to_send = "Cena"

    if have_to_send:
        # Get the day
        day = days_week[get_day(today_weekend())]

        # Sending to Avack users
        if (day == "lunedi" or day == "martedi" or day == "mercoledi" or day == "giovedi") and have_to_send == "Pranzo":
            canteen = "Avack"
            msg_menu = get_menu_updated(canteen, day, have_to_send)

            if msg_menu == "Errore":
                for chat_id in db.get_admins():
                    bot.sendMessage(chat_id, err_msg, parse_mode="Markdown")
            else:
                for chat_id in db.get_users_with_pref("notif_da", True):
                    print(Fore.YELLOW + "[SENDING AVACK] Sto inviando un messaggio a: " + chat_id)
                    keyboard = InlineKeyboardMarkup(inline_keyboard=[
                                [dict(text='PDF del menù del giorno', url=get_url(canteen, day))],
                                [dict(text='Offrici una birra!', url="https://www.paypal.me/azzeccagarbugli")]])

                    # Prints the menu in a kawaii way
                    bot.sendMessage(chat_id, msg_menu, parse_mode="Markdown", reply_markup=keyboard)

        # Sending to ColleParadiso users
        if (day == "sabato" or day == "domenica") and have_to_send == "Cena":
            pass
        else:
            canteen = "ColleParadiso"
            msg_menu = get_menu_updated(canteen, day, have_to_send)

            if msg_menu == "Errore":
                for chat_id in db.get_admins():
                    bot.sendMessage(chat_id, err_msg, parse_mode="Markdown")
            else:
                if have_to_send == "Pranzo":
                    l_or_d = "l"
                elif have_to_send == "Cena":
                    l_or_d = "d"

                for chat_id in db.get_users_with_pref("notif_cp_" + l_or_d, True):
                    print(Fore.YELLOW + "[SENDING COLLEPARADISO] Sto inviando un messaggio a: " + chat_id)
                    keyboard = InlineKeyboardMarkup(inline_keyboard=[
                                [dict(text='PDF del menù del giorno', url=get_url(canteen, day))],
                                [dict(text='Offrici una birra!', url="https://www.paypal.me/azzeccagarbugli")]])

                    # Prints the menu in a kawaii way
                    bot.sendMessage(chat_id, msg_menu, parse_mode="Markdown", reply_markup=keyboard)

    time.sleep(60)


def basic_cmds(chat_id, command_input):
    if command_input == "/start" or command_input == "/start" + BOT_NAME:
        start_msg = "*Benvenuto su @UnicamEatBot!*\nQui troverai il menù del giorno offerto dall'ERSU, per gli studenti di Unicam, per le mense di Colle Paradiso e del D'Avack. "\
                    "\nInizia digitando il comando /menu per accedere al menu o prova altri comandi per scoprire maggiori informazioni riguardo al bot. "\
                    "Se hai qualche dubbio o perplessità prova il comando /help per ulteriori dettagli."\
                    "\n\n_Il bot e' stato creato in modo non ufficiale, né ERSU Camerino né Unicam sono responsabili in alcun modo._"

        bot.sendMessage(chat_id, start_msg, parse_mode="Markdown")
        db.add_user(chat_id, bot.getChat(chat_id))
        return True

    elif command_input == "/help" or command_input == "/help" + BOT_NAME:
        help_msg = "Il servizio offerto da *Unicam Eat!* permette di accedere a diversi contenuti, raggiungibili attraverso determinati comandi tra cui:\n\n"\
                   "*/info*: fornisce ulteriori informazioni sul bot e sui suoi creatori\n\n"\
                   "*/menu*: mediante questo comando è possibile ottenere il menù del giorno, selezionando in primo luogo la *mensa* in cui si desidera mangiare, "\
                   "succesivamente il *giorno* e infine il parametro *pranzo* o *cena* in base alle proprie esigenze\n\n"\
                   "*/orari*: visualizza gli orari delle mense disponibili nel bot\n\n"\
                   "*/prezzi*: inoltra una foto contenente il listino dei prezzi e, in particolar modo, la tabella di conversione di quest'ultimi\n\n"\
                   "*/avvertenze*: inoltra all'utente delle avvertenze predisposte dalla mensa operante\n\n"\
                   "*/allergeni*: vengono visualizzati gli alimenti _o i loro componenti_ che possono scatenare reazioni immuno-mediate\n\n"\
                   "*/impostazioni*: comando che permette di modificare alcuni settaggi del bot secondo le proprie necessità"

        bot.sendMessage(chat_id, help_msg, parse_mode="Markdown")
        return True

    elif command_input == "/orari" or command_input == "/orari" + BOT_NAME:
        opening_msg = "*• D'Avack*\n"\
                    "Aperta tutti i giorni della settimana durante il pranzo, esclusi *Venerdì*, *Sabato* e *Domenica*, dalle ore *12:30* alle ore *14:15*. "\
                    "\n_Posizione:_ /posizione\_avak\n"\
                    "\n*• Colle Paradiso*\n"\
                    "Aperta tutti i giorni della settimana dalle ore *12:30* alle ore *14:15* e dalle ore *19:30* alle ore *21:15*."\
                    "\nDurante il week-end la mensa, invece, rimarrà aperta *esclusivamente* per pranzo dalle ore *12:30* alle ore *13:30*."\
                    "\n_Posizione:_ /posizione\_colleparadiso"

        bot.sendMessage(chat_id, opening_msg, parse_mode="Markdown")
        return True

    elif command_input == "/posizione_colleparadiso" or command_input == "/posizione_colleparadiso" + BOT_NAME:
        bot.sendLocation(chat_id, "4    3.1437097", "13.0822057")
        return True

    elif command_input == "/posizione_avak" or command_input == "/posizione_avak" + BOT_NAME:
        bot.sendLocation(chat_id, "43.137908", "13.0688287")
        return True

    elif command_input == "/info" or command_input == "/info" + BOT_NAME or command_input == BOT_NAME:
        bot.sendPhoto(chat_id, photo="https://i.imgur.com/6d6Sdtx.png")
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
                     [dict(text='GitHub', url='https://github.com/Azzeccagarbugli/UnicamEat'), dict(text='Developer', url='https://t.me/azzeccagarbugli')],
                     [dict(text='Offrici una birra!', url='https://www.paypal.me/azzeccagarbugli')]])

        info_msg = "*Unicam Eat!* nasce con l'idea di aiutare tutti gli studenti di Unicam nella visualizzazione dei menù "\
                   "offerti dal servizio di ristorazione dell'Ersu, presso le mense di *Colle Paradiso* e *D'Avack*. "\
                   "\nÈ possibile utilizzare i pulsanti disponibili di seguito per ottenere informazioni riguardo il codice sorgente del Bot e "\
                   "per segnalare direttamente un problema di malfunzionamento al team di sviluppo. "\
                   "\n\nInfine, se sei soddisfatto del servizio messo a dispozione e della qualità di quest'ultimo puoi donare una birra agli sviluppatori, "\
                   "ne saremmo davvero felici"

        bot.sendMessage(chat_id, info_msg, parse_mode="Markdown", reply_markup=keyboard)
        return True

    elif command_input == "/allergeni" or command_input == "/allergeni" + BOT_NAME:
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
                     [dict(text='PDF del Regolamento Europeo', url='http://www.sviluppoeconomico.gov.it/images/stories/documenti/Reg%201169-2011-UE_Etichettatura.pdf')]])

        allergeni_msg = "In allegato la lista degli allergeni approvata dal Regolamento Europeo n.1169/2011"
        bot.sendPhoto(chat_id, photo="https://i.imgur.com/OfURcFz.png", caption=allergeni_msg, reply_markup=keyboard)
        return True

    elif command_input == "/prezzi" or command_input == "/prezzi" + BOT_NAME:
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
                    [dict(text='Costo di un pasto completo', callback_data='notification_prices')]])

        prices_msg = "In allegato la lista dei prezzi con annessa tabella di corrispondenza"
        bot.sendPhoto(chat_id, photo="https://i.imgur.com/BlDDpAE.png", caption=prices_msg, reply_markup=keyboard)
        return True

    elif command_input == "/avvertenze" or command_input == "/avvertenze" + BOT_NAME:
        warning_msg = "Si avvisano gli utenti che, nel personalizzare il proprio pasto, è consentito ritirare *al massimo 2 porzioni di ciascuna pietanza o prodotto*, "\
                      "nel modo indicato: \n"\
                      "• *Max n. 2* - Primi piatti\n"\
                      "• *Max n. 2* - Secondi piatti\n"\
                      "• *Max n. 2* - Contorni\n"\
                      "• *Max n. 2* - Panini\n"\
                      "• *Max n. 2* - Prodotti confezionati\n"\
                      "• *Max n. 2* - Prodotti a scelta fra Frutta, Yogurt e Dolce\n\n"\
                      "_È severamente vietato_, *agli utenti in attesa del ritiro del pasto, toccare piatti e pietanze disponibili sul bancone self-service, senza ritirarli. "\
                      "Qualora venissero ritirati non sarà più possibile riconsegnarli.*\n\n"\
                      "_È possibile _*riconsegnare il pasto durante il percorso self-service, solamente prodotti confezionati.*\n\n"\
                      "_È altresì assolutamente vietato_ *prelevare più di tre tovaglioli ed un bicchiere, a pasto.*"

        bot.sendMessage(chat_id, warning_msg, parse_mode="HTML")
        return True

    else:
        return False


# Initializing Colorama utility
colorama.init(autoreset=True)

# Main
print(Style.BRIGHT + "Starting Unicam Eat! ...\n")

# Creation of PID file
if not os.path.exists("/tmp/"):
    pidfile = os.path.expanduser("~") + "\\AppData\\Local\\Temp\\unicameat.pid"
else:
    pidfile = "/tmp/unicameat.pid"

if os.path.isfile(pidfile):
    print(Fore.RED + "[PID PROCESS] {} already exists, exiting!".format(pidfile))
    sys.exit()

with open(pidfile, 'w') as f:
    f.write(str(os.getpid()))

# Start working
try:
    # Checks if all the files and folders exist
    check_dir_files()

    # Initializing the DB
    db = Firebase("credentials_db.json")
    db.initialize_sdk()

    bot = telepot.Bot(TOKEN)

    # Checking if some messages has been sent to the bot
    updates = bot.getUpdates()
    if updates:
        last_update_id = updates[-1]['update_id']
        bot.getUpdates(offset=last_update_id + 1)

    # Starting message_loop
    bot.message_loop({'chat': handle,
                      'callback_query': on_callback_query})

    print(Style.DIM + "\nDa grandi poteri derivano grandi responsabilità...\n")

    # Notification system
    while(1):
        update()
finally:
    os.unlink(pidfile)
    print("Done")
