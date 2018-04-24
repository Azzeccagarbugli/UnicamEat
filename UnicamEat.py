#!/usr/bin/python3.6
# -*- coding: utf-8 -*-
"""
Unicam Eat! - Telegram Bot (Main file)
Authors: Azzeccagarbugli (f.coppola1998@gmail.com)
         Porchetta       (clarantonio98@gmail.com)

TO DO:
- Espandere l'utilizzo del comando /admin per il db in Firebase                                  []
- Modificare funzione invia messaggio, vorrei che:
    - permetta di scegliere un'ora di pubblicazione
    - permetta di scegliere se inviare con notifica all'utente o no
    - controllo errore più figo (basandosi sull'offset)
- Spostare parametri di servizio (chiusura mense, booleana) all'interno di una nuova sezione
- Implementazione della gestione generica di una mensa, for the future                           []
    Cosa deve avere una mensa?
    - Posizione
    - Informazioni
    - Orari/Giorni di apertura
    - Chiusura forzata
    - Indirizzo da dove reperire i menù (privato)
"""

import os
import random
import time
import datetime
from urllib3 import exceptions as urllib3_exceptions
import xml.etree.ElementTree as ET

import colorama
from colorama import Fore, Style

import logging
import telepot
from telepot.loop import MessageLoop
from telepot.namedtuple import ReplyKeyboardMarkup, ReplyKeyboardRemove, InlineKeyboardMarkup, ForceReply
from telepot.delegate import per_chat_id, include_callback_query_chat_id, create_open, pave_event_space

from firebase_db import Firebase
from functions import *
from settings import TOKEN, BOT_NAME, Dirs, updating_time, notification_lunch, notification_dinner

# Bool to check if we want to close canteens or not
canteen_closed_da = False
canteen_closed_cp = False


class UnicamEat(telepot.helper.ChatHandler):
    def __init__(self, *args, **kwargs):
        super(UnicamEat, self).__init__(*args, **kwargs)

        self._user_state = 0
        self._report_texts = {'title': "", 'text': ""}
        self._day_menu = {'canteen': "", 'day': "", 'meal': ""}

        # Updating daily users for graph construction
        db.update_daily_users(self.bot.getChat(args[0][-1]))

    def on__idle(self, event):
        """
        Resetting user due to inactivity, deleting the thread
        """
        msg = self.sender.sendMessage(
            "...", disable_notification=True,
            reply_markup=ReplyKeyboardRemove(remove_keyboard=True))

        self.bot.deleteMessage(telepot.message_identifier(msg))
        self.close()

    def on_close(self, ex):
        """
        Override to silence one useless logging msg printed by telepot to the console
        """
        if type(ex).__name__ != "StopListening":
            logging.error('on_close() called due to %s: %s', type(ex).__name__, ex)

    def on_chat_message(self, msg):
        """
        This function handle all incoming messages
        """
        content_type, chat_type, chat_id = telepot.glance(msg, flavor='chat')

        # Checks content type of the message to assure that we're recieving a msg
        if content_type == 'text':
            command_input = msg['text']
        else:
            command_input = "Error"

        try:  # Attempting to save username and full name
            username = msg['from']['username']
        except KeyError:
            username = "Not defined"

        try:  # Attempting to save username
            username = msg['from']['username']
        except KeyError:
            username = "Not defined"

        # Updating console
        print(Fore.BLUE + "[ CHAT MESSAGE ][{}]{} - From {}@{}{}[{}]: \"{}{}\"".format(
            datetime.datetime.now().strftime("%d/%m %H:%M"),
            Style.RESET_ALL,
            Style.BRIGHT,
            username.ljust(20),
            Style.RESET_ALL,
            str(chat_id),
            Style.DIM,
            command_input))

        # Checking for basic commands
        if self.basic_cmds(command_input) is True:
            pass

        # Settings status
        elif command_input == "/settings" or command_input == "/settings" + BOT_NAME:
            settings_msg = "Attraverso le impostazioni potrai cambiare diversi parametri all'interno del *Bot*:\n"\
                           "\n• *Lingua*: passa dalla lingua attuale ad un'altra desiderata"\
                           "\n• *Notifiche*: abilita le notifiche per il menù del giorno"

            markup = InlineKeyboardMarkup(inline_keyboard=[
                         [dict(text="Lingua", callback_data="cmd_change_lng")],
                         [dict(text="Notifiche D'Avack", callback_data="cmd_notif_da")],
                         [dict(text="Notifiche Colle Paradiso", callback_data="cmd_notif_cp")]])

            self.sender.sendMessage(settings_msg, parse_mode="Markdown", reply_markup=markup)

        # Toggle/Untoggle admin role
        elif command_input == "/admin" or command_input == "/admin" + BOT_NAME:
            if db.get_user(chat_id)['role'] == 5:
                keyboard = InlineKeyboardMarkup(inline_keyboard=[
                             [dict(text="⚠️ Segnalazioni", callback_data="cmd_reports")],
                             [dict(text="✉️ Invia messaggio", callback_data="cmd_send_msg"), dict(text="🔒 Chiudi mensa", callback_data="cmd_close_canteen")],
                             [dict(text="🔍 Boolean", callback_data="cmd_bool"), dict(text="🗑 Pulisci cartelle", callback_data="cmd_clean_folders")],
                             [dict(text="📈 Grafico", callback_data="cmd_graph")]])
                self.sender.sendMessage("*PANNELLO ADMIN*\n\nSeleziona un _comando_ dalla lista sottostante", parse_mode="Markdown", reply_markup=keyboard)
            else:
                self.sender.sendMessage("Non disponi dei permessi per usare questo comando")

        # Send message function
        elif self._user_state == 11:
            text_approved = True
            try:
                self.sender.sendMessage("*ANTEPRIMA DEL TESTO:*\n----------\n" + command_input + "\n----------\n_Invio in corso, attendere..._", parse_mode="Markdown")
            except telepot.exception.TelegramError:
                self.sender.sendMessage("Il testo che hai inviato non è formattato correttamente, riprova")
                text_approved = False

            if text_approved:
                # Tries to send the message
                for user_chat_id in db.get_all_users_id():
                    if str(user_chat_id) != str(chat_id):
                        try:
                            self.bot.sendMessage(user_chat_id, command_input, parse_mode="Markdown")
                        except telepot.exception.TelegramError as e:
                            if e.error_code == 400:
                                print(Fore.YELLOW + "[WARNING] Non sono riuscito ad inviare il messaggio a: " + user_chat_id)

                self.sender.sendMessage("_Ho inoltrato il messaggio che mi hai inviato a tutti gli utenti con successo_", parse_mode="Markdown")

                # Set user state
                self._user_state = 0

        # Get canteen
        elif command_input == "/menu" or command_input == "/menu" + BOT_NAME:
            markup = ReplyKeyboardMarkup(keyboard=[
                            ["D'Avack"],
                            ["Colle Paradiso"]])

            msg = "Selezionare la mensa"
            self.sender.sendMessage(msg, reply_markup=markup)

            # Set user state
            self._user_state = 21

        # Get date
        elif self._user_state == 21:
            # Canteen's stuff
            self._day_menu['canteen'] = command_input

            msg = "Inserisci la data"
            canteen_closed_holiday_msg = "Attualmente la mensa che hai selezionato è *chiusa*, ti preghiamo di attendere fino ad eventuali aggiornamenti"

            if command_input == "D'Avack":
                self._day_menu['canteen'] = "D'Avack"
                if canteen_closed_da:
                    keyboard = InlineKeyboardMarkup(inline_keyboard=[
                                 [dict(text="Controlla eventuali aggiornamenti", url='http://www.ersucam.it/')]])
                    self.sender.sendMessage("_Stiamo controllando lo stato della mensa_", parse_mode="Markdown", reply_markup=ReplyKeyboardRemove(remove_keyboard=True))
                    self.sender.sendMessage(canteen_closed_holiday_msg, parse_mode="Markdown", reply_markup=keyboard)

                    # Set user state
                    self._user_state = 0
                else:
                    # Get the date
                    day_int = datetime.datetime.today().weekday()
                    # Is Canteen closed?
                    if day_int >= 4:
                        closed_msg = "La mensa del D'Avack nei giorni *Venerdì*, *Sabato* e *Domenica* rimane chiusa sia "\
                                     "per pranzo che per cena. Riprova a inserire il comando /menu e controlla la mensa "\
                                     "di *Colle Pardiso* per ottenere i menù da te desiderati"

                        self.sender.sendMessage(closed_msg, parse_mode="Markdown", reply_markup=ReplyKeyboardRemove(remove_keyboard=True))

                        self._user_state = 0
                    else:
                        markup = ReplyKeyboardMarkup(keyboard=get_da_keyboard())
                        self.sender.sendMessage(msg, parse_mode="Markdown", reply_markup=markup)

                        self._user_state = 22

            elif command_input == "Colle Paradiso":
                self._day_menu['canteen'] = "Colle Paradiso"
                if canteen_closed_cp:
                    keyboard = InlineKeyboardMarkup(inline_keyboard=[
                                 [dict(text="Controlla eventuali aggiornamenti", url='http://www.ersucam.it/')]])
                    self.sender.sendMessage("_Stiamo controllando lo stato della mensa_", parse_mode="Markdown", reply_markup=ReplyKeyboardRemove(remove_keyboard=True))
                    self.sender.sendMessage(canteen_closed_holiday_msg, parse_mode="Markdown", reply_markup=keyboard)

                    # Set user state
                    self._user_state = 0
                else:
                    markup = ReplyKeyboardMarkup(keyboard=get_cp_keyboard())
                    self.sender.sendMessage(msg, reply_markup=markup)

                    self._user_state = 22
            else:
                self.sender.sendMessage("Inserisci una mensa valida")

        # Get lunch or dinner
        elif self._user_state == 22:
            # Setting day
            if command_input == "Oggi" or command_input == "Lunedì" or command_input == "Martedì" or command_input == "Mercoledì" or command_input == "Giovedì" or command_input == "Venerdì" or command_input == "Sabato" or command_input == "Domenica":
                if command_input == "Oggi":
                    per_benino = {
                        0: "Lunedì",
                        1: "Martedì",
                        2: "Mercoledì",
                        3: "Giovedì",
                        4: "Venerdì",
                        5: "Sabato",
                        6: "Domenica"
                    }
                    self._day_menu['day'] = per_benino[datetime.datetime.today().weekday()]
                else:
                    self._day_menu['day'] = command_input

                # Is D'Avack closed?
                if (self._day_menu['day'] == "Venerdì" or self._day_menu['day'] == "Sabato" or self._day_menu['day'] == "Domenica") and self._day_menu['canteen'] == "D'Avack":
                    closed_msg = "La mensa del D'Avack nei giorni *Venerdì*, *Sabato* e *Domenica* rimane chiusa sia "\
                                 "per pranzo che per cena. Riprova a inserire il comando /menu e controlla la mensa "\
                                 "di *Colle Pardiso* per ottenere i menù da te desiderati"

                    self.sender.sendMessage(closed_msg, parse_mode="Markdown", reply_markup=ReplyKeyboardRemove(remove_keyboard=True))
                    self._user_state = 0
                else:
                    # Bot send activity for nice appearence
                    self.sender.sendChatAction("typing")

                    # Choose the right time for eat
                    markup = ReplyKeyboardMarkup(keyboard=get_launch_dinner_keyboard(self._day_menu['canteen'], self._day_menu['day']))

                    if (self._day_menu['day'] == "Sabato" or self._day_menu['day'] == "Domenica") and self._day_menu['canteen'] == "Colle Paradiso":
                        msg = "Ti ricordiamo che durante i giorni di *Sabato* e *Domenica*, la mensa di *Colle Paradiso* rimarrà aperta solo durante "\
                              "il turno del pranzo. \nPer maggiori dettagli riguardo gli orari effettivi delle mense puoi consultare il comando /hours e non scordarti "\
                              "di prendere anche la cena!"
                    elif self._day_menu['canteen'] == "D'Avack":
                        msg = "Ti ricordiamo che la mensa del *D'Avack* è aperta _esclusivamente_ per il turno del pranzo.\n"\
                              "Per maggiori dettagli riguardo gli orari effettivi delle mense puoi consultare il comando /hours"
                    else:
                        msg = "Seleziona dalla lista il menù desiderato"

                    self.sender.sendMessage(msg, parse_mode="Markdown", reply_markup=markup)

                    # Set user state
                    self._user_state = 23
            else:
                self.sender.sendMessage("La data inserita non è valida, riprova inserendone una valida", parse_mode="Markdown", reply_markup=markup)

        # Print menu
        elif self._user_state == 23:
            # Check the existence of the life (see line 22)
            if command_input == "Pranzo" or command_input == "Cena":
                self._day_menu['meal'] = command_input

                # Bot send activity for nice appaerence
                self.sender.sendChatAction("upload_document")
                self.sender.sendMessage("_Stiamo processando la tua richiesta..._", parse_mode="Markdown", reply_markup=ReplyKeyboardRemove(remove_keyboard=True))

                result_menu = get_updated_menu(self._day_menu['canteen'], self._day_menu['day'], self._day_menu['meal'])

                if result_menu != "Error":
                    # Take random number for the donation
                    random_donation = random.randint(0, 5)

                    # qrcode_filename never used, do we need it?
                    now = datetime.datetime.now()
                    qrcode_filename = generate_qr_code(chat_id, result_menu, Dirs.QRCODE, str(now.strftime("%d/%m %H:%M")), self._day_menu['canteen'], command_input)

                    keyboard = ""

                    if db.get_user(chat_id)['role'] == 5:
                        keyboard = InlineKeyboardMarkup(inline_keyboard=[
                                    [dict(text='Prenota con il QR Code!', callback_data='qrcode')]])
                    elif random_donation:
                        keyboard = InlineKeyboardMarkup(inline_keyboard=[
                                    [dict(text='Offrici una birra!', url="https://www.paypal.me/azzeccagarbugli")]])

                    # Prints the menu in a kawaii way
                    if keyboard:
                        self.sender.sendMessage(result_menu, parse_mode="Markdown", reply_markup=keyboard)
                    else:
                        self.sender.sendMessage(result_menu, parse_mode="Markdown")
                else:
                    fail_conversion_msg = "Carissimo utente, ci dispiace che la conversione del menù non sia andata a buon fine. \n\n_Segnala gentilmente l'errore agli sviluppatori "\
                                          "che provederrano a risolvere quest'ultimo_"

                    callback_name = 'notification_developer ' + self._day_menu['canteen'] + ' - ' + self._day_menu['day']

                    keyboard = InlineKeyboardMarkup(inline_keyboard=[
                                 [dict(text="Segnala l'errore ai developer", callback_data=callback_name)]])

                    # Prints the menu in a kawaii way
                    self.sender.sendMessage(fail_conversion_msg, parse_mode="Markdown", reply_markup=keyboard)
                # Set user state
                self._user_state = 0
            else:
                self.sender.sendMessage("Inserisci un parametro valido")

        # Register command
        elif command_input == "/register" or command_input == "/register" + BOT_NAME:
            role = db.get_user(chat_id)['role']

            if role == 0:
                # Inserimento Nome
                msg = "Attraverso il seguente comando potrai confermare la tua identità in maniera *ufficiosa* con i tuoi dati personali. "\
                      "\nMediante tale registrazione ti sarà possibile effettuare *prenotazioni del menù del giorno* quindi ti invitiamo, "\
                      "onde evitare problematiche, all'inserimento di *dati veritieri*."\
                      "\n\n_I tuoi personali innanzitutto sono al sicuro grazie alla crittografia offerta da Telegram e in secondo luogo, carissimo utente, "\
                      "noi teniamo a te davvero molto e vogliamo garantirti la migliore esperienza d'uso possibile_"

                self.sender.sendMessage(msg, parse_mode="Markdown")
                self.sender.sendMessage("Inserisci il tuo *nome*. _Ti sarà chiesta una conferma prima di renderlo definitivo._", parse_mode="Markdown", reply_markup=ForceReply(force_reply=True))

                self._user_state = 31
            elif role == 1:
                msg_text = "La registrazione è già stata effettuata con successo ma non hai confermato di persona la tua identità presso la mensa."\
                            "\n\n_Se pensi che ci sia stato un problema contatta il developer_"
                keyboard = InlineKeyboardMarkup(inline_keyboard=[
                             [dict(text='Developer', url='https://t.me/azzeccagarbugli')]])
                self.sender.sendMessage(msg_text, parse_mode="Markdown", reply_markup=keyboard)

            elif role == 2:
                msg_text = "Ci risulta che tu abbia già confermato personalmente la tua identità presso la mensa, "\
                           "per cui ti è già possibile ordinare i menù.\n\n_Se pensi che ci sia stato un problema contatta il developer_"
                keyboard = InlineKeyboardMarkup(inline_keyboard=[
                             [dict(text='Developer', url='https://t.me/azzeccagarbugli')]])
                self.sender.sendMessage(msg_text, parse_mode="Markdown", reply_markup=keyboard)

            else:
                msg_text = "Il ruolo che ho trovato nel database *(" + str(role) + ")* non richiede che tu effettui una registrazione."\
                           "\n\n_Se pensi che ci sia stato un problema contatta il developer_"
                keyboard = InlineKeyboardMarkup(inline_keyboard=[
                             [dict(text='Developer', url='https://t.me/azzeccagarbugli')]])
                self.sender.sendMessage(msg_text, parse_mode="Markdown", reply_markup=keyboard)

        elif self._user_state == 31:
            # Inserimento Cognome
            db.edit_user(chat_id, "info/first_name", command_input)

            self.sender.sendMessage("Inserisci il tuo *cognome*. _Ti sarà chiesta una conferma prima di renderlo definitivo_", parse_mode="Markdown", reply_markup=ForceReply(force_reply=True))
            self._user_state = 32

        elif self._user_state == 32:
            # Checking pt.1
            db.edit_user(chat_id, "info/last_name", command_input)

            markup = ReplyKeyboardMarkup(keyboard=[
                            ["Confermo"],
                            ["Modifica i dati"]])

            user_info = db.get_user(chat_id)
            msg = "Confermi che il seguente profilo corrisponde alla tua identità reale?"\
                  "\n\n*NOME:* {}\n*COGNOME:* {}"\
                  "\n\n*ATTENZIONE:* una volta confermati non potrai più modificarli".format(user_info['info']['first_name'], user_info['info']['last_name'])
            self.sender.sendMessage(msg, parse_mode="Markdown", reply_markup=markup)
            self._user_state = 33

        elif self._user_state == 33:
            # Checking pt.2
            if command_input == "Confermo":
                db.edit_user(chat_id, "role", 1)

                user_info = db.get_user(chat_id)
                msg_lol = "*" + user_info['info']['first_name'] + " " + user_info['info']['last_name'] + "* welcome in the family ❤️"

                self.sender.sendPhoto("https://i.imgur.com/tFUZ984.jpg", caption=msg_lol, parse_mode="Markdown", reply_markup=ReplyKeyboardRemove(remove_keyboard=True))
                self._user_state = 0

            elif command_input == "Modifica dati":
                self.sender.sendMessage("Inserisci il tuo *nome*. _Ti sarà chiesta una conferma prima di renderlo definitivo_", parse_mode="Markdown", reply_markup=ForceReply(force_reply=True))
                self._user_state = 31

            else:
                self.sender.sendMessage("L'opzione specificata non è valida, scegline una corretta dalla tastiera", parse_mode="Markdown", reply_markup=ForceReply(force_reply=True))

        # Report a bug to the developers
        elif command_input == "/report" or command_input == "/report" + BOT_NAME:
            msg = "Tramite questo comando potrai inviare un *errore* che hai trovato agli sviluppatori,"\
                  "o semplicemente inviargli il tuo *parere* su questo Bot."\
                  "\n\n_Ti basta scrivere qui sotto il testo che vuoi inviargli e la tua richiesta sarà immediatamente salvata nel server e rigirata agli sviluppatori._"\
                  "\n\nPer cominciare digita il *titolo* del messaggio da inviare"
            self.sender.sendMessage(msg, parse_mode="Markdown", reply_markup=ForceReply(force_reply=True))

            self._user_state = 41

        elif self._user_state == 41:
            self._report_texts['title'] = command_input

            msg = "Adesso scrivi il tuo *messaggio*"
            self.sender.sendMessage(msg, parse_mode="Markdown", reply_markup=ForceReply(force_reply=True))

            self._user_state = 42

        elif self._user_state == 42:
            self._report_texts['text'] = command_input

            markup = ReplyKeyboardMarkup(keyboard=[
                            ["Confermo"],
                            ["Ricrea da capo"]])

            user_info = db.get_user(chat_id)
            msg = "Confermi di voler inviare il seguente messaggio?"\
                  "\n\n🏷 *TITOLO:* {}\n📝 *Messaggio*:\n_{}_"\
                  "\n\n*ATTENZIONE:* Una volta confermato non potrai più modificarlo".format(self._report_texts['title'], self._report_texts['text'])
            self.sender.sendMessage(msg, parse_mode="Markdown", reply_markup=markup)
            self._user_state = 43

        elif self._user_state == 43:
            if command_input == "Confermo":
                db.report_error(chat_id, self._report_texts['title'], self._report_texts['text'], high_priority=False)

                msg = "Il tuo messaggio è stato inviato *con successo*, ti ringraziamo per la collaborazione"
                self.sender.sendMessage(msg, parse_mode="Markdown", reply_markup=ReplyKeyboardRemove(remove_keyboard=True))

                self._user_state = 0

            elif command_input == "Ricrea da capo":
                msg = "La precedente segnalazione è stata *annullata*.\nScrivi il *titolo* del messaggio"
                self.sender.sendMessage(msg, parse_mode="Markdown", reply_markup=ForceReply(force_reply=True))

                self._user_state = 41

            else:
                self.sender.sendMessage("L'opzione specificata non è valida, scegline una corretta dalla tastiera", parse_mode="Markdown", reply_markup=ForceReply(force_reply=True))

        # Admin view reports
        elif self._user_state == 51 or self._user_state == 52:
            if self._user_state == 51:
                reports = db.get_reports(new=True, old=False)
            else:
                reports = db.get_reports(new=False, old=True)

            # Retrieving wanted msg
            title = command_input.split(' [')[0]

            msg_data = [
                reports[title]['chat_id'],
                "Alta" if reports[title]['high_priority'] else "Bassa",
                reports[title]['date'],
                title,
                reports[title]['text']
            ]

            # Printing wanted msg
            msg = "👤 *DA:* _{}_\n❗️ *PRIORITÀ:* {}\n"\
                  "📅 *DATA:* {}\n\n"\
                  "🏷 *TITOLO:* {}\n"\
                  "📝 *MESSAGGIO:*\n{}".format(msg_data[0], msg_data[1], msg_data[2], msg_data[3], msg_data[4])

            if self._user_state == 51:
                db.read_report(title)
            self.sender.sendMessage(msg, parse_mode="Markdown", reply_markup=ReplyKeyboardRemove(remove_keyboard=True))

        # Fun messages
        elif command_input.lower() == "questa mensa fa schifo" or command_input.lower() == "che schifo" or command_input.lower() == "siete inutili":
            self.sender.sendSticker("CAADBAADdwADzISpCY36P9nASV4cAg")
            self.sender.sendMessage("_Cikò non è d'accordo con te ma ti vuole bene lo stesso, perchè lui vuole bene a tutti_", parse_mode="Markdown")

        elif command_input.lower() == "cotoletta plz" or command_input.lower() == "i want cotoletta" or command_input.lower() == "give me my cotoletta":
            self.sender.sendSticker("CAADBAADegADzISpCVjpXErTcu75Ag")
            self.sender.sendMessage("_You will have your cotoletta maybe the next time, don't be offended_", parse_mode="Markdown")

        # Default message
        else:
            self.sender.sendMessage("Il messaggio che hai inviato *non è valido*, prova inserendo un comando disponibile nella lista", parse_mode="Markdown")

    def on_callback_query(self, msg):
        """
        Manages all the inline query by the users
        """
        query_id, from_id, query_data = telepot.glance(msg, flavor='callback_query')

        try:  # Attempting to save username
            username = msg['from']['username']
        except KeyError:
            username = "Not defined"

        # Updating console
        print(Fore.GREEN + "[CALLBACK QUERY][{}]{} - From {}@{}{}[{}]: \"{}{}\"".format(
            datetime.datetime.now().strftime("%d/%m %H:%M"),
            Style.RESET_ALL,
            Style.BRIGHT,
            username.ljust(20),
            Style.RESET_ALL,
            str(from_id),
            Style.DIM,
            query_data))

        # Proxy to bot's message editing methods
        msg_identifier = (msg['from']['id'], msg['message']['message_id'])
        self.editor = telepot.helper.Editor(self.bot, msg_identifier)

        try:
            if query_data == 'notification_prices':
                msg_text_prices = "Studenti: 5,50€ - Non studenti: 8,00€"
                self.bot.answerCallbackQuery(query_id, text=msg_text_prices)

            elif 'notification_developer' in query_data:
                txtname = query_data.replace("notification_developer ", "")
                db.report_error("UnicamEat", txtname, "Errore nella generazione del menù.", high_priority=True)

                msg_text_warn = "La segnalazione è stata inviata ai developer"
                self.bot.answerCallbackQuery(query_id, text=msg_text_warn)

            elif query_data == 'qrcode':
                self.bot.sendPhoto(
                    from_id,
                    photo=open(Dirs.QRCODE + str(from_id) + "_" + "QRCode.png", 'rb'),
                    caption="In allegato il tuo *QR Code* contenente i pasti da te selezionati",
                    parse_mode="Markdown")
                self.bot.answerCallbackQuery(query_id)

            elif query_data == "cmd_back_admin":
                keyboard = InlineKeyboardMarkup(inline_keyboard=[
                             [dict(text="⚠️ Segnalazioni", callback_data="cmd_reports")],
                             [dict(text="✉️ Invia messaggio", callback_data="cmd_send_msg"), dict(text="🔒 Chiudi mensa", callback_data="cmd_close_canteen")],
                             [dict(text="🔍 Boolean", callback_data="cmd_bool"), dict(text="🗑 Pulisci cartelle", callback_data="cmd_clean_folders")],
                             [dict(text="📈 Grafico", callback_data="cmd_graph")]])

                self.editor.editMessageText(text="*PANNELLO ADMIN*\n\nSeleziona un _comando_ dalla lista sottostante", parse_mode="Markdown", reply_markup=keyboard)
                self.bot.answerCallbackQuery(query_id)

            elif query_data == 'cmd_reports':
                new_reports, old_reports = db.get_reports_number()

                keyboard = InlineKeyboardMarkup(inline_keyboard=[
                            [dict(text="📩 Visualizza nuovi", callback_data="cmd_view_reports_new")],
                            [dict(text="🗂 Visualizza vecchi", callback_data="cmd_view_reports_old")],
                            [dict(text="<<  Indietro", callback_data="cmd_back_admin")]])

                answer_msg = "Hai *{} messaggi non letti*, _{} già letti_".format(new_reports, old_reports)
                self.editor.editMessageText(answer_msg, parse_mode="Markdown", reply_markup=keyboard)
                self.bot.answerCallbackQuery(query_id)

            elif 'cmd_view_reports' in query_data:
                if 'new' in query_data:
                    reports = db.get_reports(new=True, old=False)
                    self._user_state = 51
                elif 'old' in query_data:
                    reports = db.get_reports(new=False, old=True)
                    self._user_state = 52

                if reports is not None:
                    keyboard = []
                    for key, val in reports.items():
                        keyboard.append([key + " [{}]".format(val['date'])])

                    markup = ReplyKeyboardMarkup(keyboard=keyboard)
                    self.bot.sendMessage(from_id, "Seleziona un messaggio da vedere dalla lista sottostante", reply_markup=markup)

                    self.bot.answerCallbackQuery(query_id)
                else:
                    self.bot.answerCallbackQuery(query_id, text="Non sono presenti messaggi")

            elif query_data == 'cmd_send_msg':
                self.bot.sendMessage(from_id, "Digita il testo che vorresti inoltrare a tutti gli utenti usufruitori di questo bot")

                self.bot.answerCallbackQuery(query_id)
                self._user_state = 11

            elif query_data == 'cmd_close_canteen':
                global canteen_closed_da, canteen_closed_cp

                keyboard = InlineKeyboardMarkup(inline_keyboard=[
                            [dict(text="D'Avack", callback_data="cmd_close_canteen_da")],
                            [dict(text="Colle Paradiso", callback_data="cmd_close_canteen_cp")],
                            [dict(text="<<  Indietro", callback_data="cmd_back_admin")]])

                self.editor.editMessageText(text="Seleziona la mensa", reply_markup=keyboard)
                self.bot.answerCallbackQuery(query_id)

            elif query_data == "cmd_close_canteen_da":
                global canteen_closed_da

                if canteen_closed_da:
                    msg_to_admin = "Ho aperto la mensa D'Avack"
                    canteen_closed_da = False
                else:
                    msg_to_admin = "Ho chiuso la mensa D'Avack"
                    canteen_closed_da = True

                self.bot.answerCallbackQuery(query_id, text=msg_to_admin)

            elif query_data == "cmd_close_canteen_cp":
                global canteen_closed_cp

                if canteen_closed_cp:
                    msg_to_admin = "Ho aperto la mensa Colle Paradiso"
                    canteen_closed_cp = False
                else:
                    msg_to_admin = "Ho chiuso la mensa Colle Paradiso"
                    canteen_closed_cp = True

                self.bot.answerCallbackQuery(query_id, text=msg_to_admin)

            elif query_data == 'cmd_bool':
                self.bot.answerCallbackQuery(query_id, text="Il valore attuale della booleana è: {}".format(str(get_bool())))

            elif query_data == 'cmd_clean_folders':
                delete_files_infolder(Dirs.PDF)
                delete_files_infolder(Dirs.TXT)
                self.bot.answerCallbackQuery(query_id, text="Ho ripulito le folders \"pdfDir\", \"txtDir\" e \"logDir\".")

            elif query_data == 'cmd_graph':
                self.bot.sendChatAction(from_id, "upload_photo")

                # Creation of the png photo to send
                graph_name = Dirs.TEMP + "temp_graph.png"
                create_graph(db, 31, graph_name)

                number_total_user = len(db.get_all_users_id())

                try:
                    self.bot.sendPhoto(from_id, photo=open(graph_name, 'rb'), caption="Il numero totale di utenti è: *{}*".format(str(number_total_user)), parse_mode="Markdown")
                except TypeError:
                    self.bot.sendMessage(from_id, "Per inviare correttamente l'immagine è necessario aggiornare Telepot ad una versione maggiore della 12.6")

                os.remove(graph_name)
                self.bot.answerCallbackQuery(query_id)

            elif query_data == 'cmd_back_settings':
                settings_msg = "Attraverso le impostazioni potrai cambiare diversi parametri all'interno del *Bot*:\n"\
                               "\n• *Lingua*: passa dalla lingua attuale ad un'altra desiderata"\
                               "\n• *Notifiche*: abilita le notifiche per il menù del giorno"

                markup = InlineKeyboardMarkup(inline_keyboard=[
                             [dict(text="Lingua", callback_data="cmd_change_lng")],
                             [dict(text="Notifiche D'Avack", callback_data="cmd_notif_da")],
                             [dict(text="Notifiche Colle Paradiso", callback_data="cmd_notif_cp")]])

                self.editor.editMessageText(text=settings_msg, parse_mode="Markdown", reply_markup=markup)
                self.bot.answerCallbackQuery(query_id)

            elif query_data == 'cmd_change_lng':
                # Work in Progress
                # wanted_language = command_input.replace("Lingua: ", "")
                not_lng_msg_status = "Scegliere la lingua con il quale si desidera utilizzare il Bot"
                markup = InlineKeyboardMarkup(inline_keyboard=[
                          [dict(text="🇮🇹 Italiano", callback_data="cmd_lng_it")],
                          [dict(text="🇬🇧 Inglese", callback_data="cmd_lng_ing")],
                          [dict(text="🇨🇳 Cinese", callback_data="cmd_lng_cinese")],
                          [dict(text="<<  Indietro", callback_data="cmd_back_settings")]])

                self.editor.editMessageText(text=not_lng_msg_status, parse_mode="Markdown", reply_markup=markup)
                self.bot.answerCallbackQuery(query_id)

            elif "cmd_lng" in query_data:
                # Work in progress
                self.bot.answerCallbackQuery(query_id, text="Funzione ancora non implementata")

            elif query_data == 'cmd_notif_da':
                not_da_msg_status = "Scegliere se *abilitare* o *disabilitare* le notifiche"
                markup = InlineKeyboardMarkup(inline_keyboard=[
                          [dict(text="🔔 Abilita", callback_data="cmd_notif_da_on")],
                          [dict(text="🔕 Disabilita", callback_data="cmd_notif_da_off")],
                          [dict(text="<<  Indietro", callback_data="cmd_back_settings")]])

                self.editor.editMessageText(text=not_da_msg_status, parse_mode="Markdown", reply_markup=markup)
                self.bot.answerCallbackQuery(query_id)

            elif query_data == 'cmd_notif_da_on':
                db.edit_user(from_id, "preferences/notif_da", True)
                self.bot.answerCallbackQuery(query_id, text="Le notifiche per il D'Avack sono state abilitate")

            elif query_data == 'cmd_notif_da_off':
                db.edit_user(from_id, "preferences/notif_da", False)
                self.bot.answerCallbackQuery(query_id, text="Le notifiche per il D'Avack sono state disabilitate")

            elif query_data == 'cmd_notif_cp':
                not_cp_msg_status = "Scegliere se *abilitare* o *disabilitare* le notifiche per il pranzo e per la cena, o per entrambe"
                markup = InlineKeyboardMarkup(inline_keyboard=[
                          [dict(text="Pranzo", callback_data="cmd_notif_cp_lunch")],
                          [dict(text="Cena", callback_data="cmd_notif_cp_dinner")],
                          [dict(text="<<  Indietro", callback_data="cmd_back_settings")]])

                self.editor.editMessageText(text=not_cp_msg_status, parse_mode="Markdown", reply_markup=markup)
                self.bot.answerCallbackQuery(query_id)

            elif query_data == 'cmd_notif_cp_lunch':
                not_cp_msg_status = "Scegliere se *abilitare* o *disabilitare* le notifiche per il pranzo"
                markup = InlineKeyboardMarkup(inline_keyboard=[
                          [dict(text="🔔 Abilita", callback_data="cmd_notif_cp_lunch_on")],
                          [dict(text="🔕 Disabilita", callback_data="cmd_notif_cp_lunch_off")],
                          [dict(text="<<  Indietro", callback_data="cmd_notif_cp")]])

                self.editor.editMessageText(text=not_cp_msg_status, parse_mode="Markdown", reply_markup=markup)
                self.bot.answerCallbackQuery(query_id)

            elif query_data == 'cmd_notif_cp_dinner':
                not_cp_msg_status = "Scegliere se *abilitare* o *disabilitare* le notifiche per la cena"
                markup = InlineKeyboardMarkup(inline_keyboard=[
                          [dict(text="🔔 Abilita", callback_data="cmd_notif_cp_dinner_on")],
                          [dict(text="🔕 Disabilita", callback_data="cmd_notif_cp_dinner_off")],
                          [dict(text="<<  Indietro", callback_data="cmd_notif_cp")]])

                self.editor.editMessageText(text=not_cp_msg_status, parse_mode="Markdown", reply_markup=markup)
                self.bot.answerCallbackQuery(query_id)

            elif query_data == 'cmd_notif_cp_lunch_on':
                db.edit_user(from_id, "preferences/notif_cp_l", True)
                self.bot.answerCallbackQuery(query_id, text="Le notifiche per Colle Paradiso nel turno del pranzo sono state abilitate")

            elif query_data == 'cmd_notif_cp_lunch_off':
                db.edit_user(from_id, "preferences/notif_cp_l", False)
                self.bot.answerCallbackQuery(query_id, text="Le notifiche per Colle Paradiso nel turno del pranzo sono state disabilitate")

            elif query_data == 'cmd_notif_cp_dinner_on':
                db.edit_user(from_id, "preferences/notif_cp_d", True)
                self.bot.answerCallbackQuery(query_id, text="Le notifiche per Colle Paradiso nel turno della cena sono state abilitate")

            elif query_data == 'cmd_notif_cp_dinner_off':
                db.edit_user(from_id, "preferences/notif_cp_d", False)
                self.bot.answerCallbackQuery(query_id, text="Le notifiche per Colle Paradiso nel turno della cena sono state disabilitate")

            elif query_data == 'cmd_position_da':
                self.bot.sendLocation(from_id, "43.137908", "13.0688287")
                self.bot.answerCallbackQuery(query_id, text="La posizione del D'Avack è stata condivisa")

            elif query_data == 'cmd_position_cp':
                self.bot.sendLocation(from_id, "43.1437097", "13.0822057")
                self.bot.answerCallbackQuery(query_id, text="La posizione di Colle Paradiso è stata condivisa")

        except telepot.exception.TelegramError as e:
            """
            Managing multiple click on an inline query by ignoring this exception
            """
            if e.description != 'Bad Request: message is not modified':
                logging.error('on_close() called due to %s: %s', type(e).__name__, e)
                self.close()


    def basic_cmds(self, command_input):
        if command_input == "/start" or command_input == "/start" + BOT_NAME:
            start_msg = "*Benvenuto su @UnicamEatBot!*\nQui troverai il menù del giorno offerto dall'ERSU, per gli studenti di Unicam, per le mense di Colle Paradiso e del D'Avack. "\
                        "\nInizia digitando il comando /menu per accedere al menu o prova altri comandi per scoprire maggiori informazioni riguardo al *Bot*. "\
                        "\nSe hai qualche dubbio o perplessità prova il comando /help per ulteriori dettagli."\
                        "\n\n_Il Bot e' stato creato in collaborazione ufficiale con l'ERSU di Camerino_"

            self.sender.sendMessage(start_msg, parse_mode="Markdown")
            return True

        elif command_input == "/help" or command_input == "/help" + BOT_NAME:
            help_msg = "Il servizio offerto da *Unicam Eat!* permette di accedere a diversi contenuti, raggiungibili attraverso determinati comandi tra cui:\n\n"\
                       "/info: fornisce ulteriori informazioni sul Bot e sui suoi creatori\n\n"\
                       "/menu: mediante questo comando è possibile ottenere il menù del giorno, selezionando in primo luogo la *mensa* in cui si desidera mangiare, "\
                       "succesivamente il *giorno* e infine il parametro *pranzo* o *cena* in base alle proprie esigenze\n\n"\
                       "/hours: visualizza gli orari delle mense disponibili nel Bot\n\n"\
                       "/position: restituisce le posizioni delle mense di Camerino\n\n"\
                       "/prices: inoltra una foto contenente il listino dei prezzi e, in particolar modo, la tabella di conversione di quest'ultimi\n\n"\
                       "/warnings: inoltra all'utente delle avvertenze predisposte dalla mensa operante\n\n"\
                       "/allergens: vengono visualizzati gli alimenti _o i loro componenti_ che possono scatenare reazioni immuno-mediate\n\n"\
                       "/settings: comando che permette di modificare alcuni settaggi del Bot secondo le proprie necessità\n\n"\
                       "/report: permette di inviare un messaggio agli sviluppatori, che sia di segnalazione o altro"

            self.sender.sendMessage(help_msg, parse_mode="Markdown")
            return True

        elif command_input == "/hours" or command_input == "/hours" + BOT_NAME:
            opening_msg = "*• D'Avack*\n"\
                        "Aperta tutti i giorni della settimana durante il pranzo, esclusi *Venerdì*, *Sabato* e *Domenica*, dalle ore *12:30* alle ore *14:15*. \n"\
                        "\n*• Colle Paradiso*\n"\
                        "Aperta tutti i giorni della settimana dalle ore *12:30* alle ore *14:15* e dalle ore *19:30* alle ore *21:15*."\
                        "\nDurante il week-end la mensa, invece, rimarrà aperta *esclusivamente* per pranzo dalle ore *12:30* alle ore *13:30*."\
                        "_\n\nPer le posizioni delle mense di Camerino è possibile consultare il comando_ /position"

            self.sender.sendMessage(opening_msg, parse_mode="Markdown")
            return True

        elif command_input == "/position" or command_input == "/position" + BOT_NAME:
            msg_text = "Di seguito puoi accedere ai due comandi che ti restitueranno la posizione delle mense del *D'Avack* e di *Colle Paradiso*"
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                         [dict(text="D'Avack", callback_data="cmd_position_da")],
                         [dict(text="Colle Paradiso", callback_data="cmd_position_cp")]])

            self.sender.sendMessage(msg_text, parse_mode="Markdown", reply_markup=keyboard)
            return True

        elif command_input == "/info" or command_input == "/info" + BOT_NAME or command_input == BOT_NAME:
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                         [dict(text='GitHub', url='https://github.com/Azzeccagarbugli/UnicamEat'), dict(text='Developer', url='https://t.me/azzeccagarbugli')],
                         [dict(text='Offrici una birra!', url='https://www.paypal.me/azzeccagarbugli')]])

            info_msg = "*Unicam Eat!* nasce con l'idea di aiutare tutti gli studenti di Unicam nella visualizzazione dei menù "\
                       "offerti dal servizio di ristorazione dell'Ersu, presso le mense di *Colle Paradiso* e *D'Avack*. "\
                       "\nÈ possibile utilizzare i pulsanti disponibili di seguito per ottenere informazioni riguardo il codice sorgente del Bot e "\
                       "per segnalare direttamente un problema di malfunzionamento al team di sviluppo. "\
                       "\n\nInfine, se sei soddisfatto del servizio messo a dispozione e della qualità di quest'ultimo puoi donare una birra agli sviluppatori, "\
                       "ne saremmo davvero felici"

            self.sender.sendPhoto(photo="https://i.imgur.com/6d6Sdtx.png")
            self.sender.sendMessage(info_msg, parse_mode="Markdown", reply_markup=keyboard)
            return True

        elif command_input == "/allergens" or command_input == "/allergens" + BOT_NAME:
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                         [dict(text='PDF del Regolamento Europeo', url='http://www.sviluppoeconomico.gov.it/images/stories/documenti/Reg%201169-2011-UE_Etichettatura.pdf')]])

            allergeni_msg = "In allegato la lista degli allergeni approvata dal Regolamento Europeo n.1169/2011"
            self.sender.sendPhoto(photo="https://i.imgur.com/OfURcFz.png", caption=allergeni_msg, reply_markup=keyboard)
            return True

        elif command_input == "/prices" or command_input == "/prices" + BOT_NAME:
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                        [dict(text='Costo di un pasto completo', callback_data='notification_prices')]])

            prices_msg = "In allegato la lista dei prezzi con annessa tabella di corrispondenza"
            self.sender.sendPhoto(photo="https://i.imgur.com/BlDDpAE.png", caption=prices_msg, reply_markup=keyboard)
            return True

        elif command_input == "/warnings" or command_input == "/warnings" + BOT_NAME:
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

            self.sender.sendMessage(warning_msg, parse_mode="Markdown")
            return True

        else:
            return False


def update(upd_time):
    """
    Send the notification to the users
    """
    now = datetime.datetime.now()
    curr_time = {now.time().hour, now.time().minute}

    # Supper or lunch
    have_to_send = ""

    # Error message
    err_msg = "Si è verificato un errore all'interno di *@UnicamEatBot*, il menù non è stato convertito correttamente"

    if curr_time == notification_lunch:
        have_to_send = "Pranzo"
    elif curr_time == notification_dinner:
        have_to_send = "Cena"

    per_bene = {
        0 : "Lunedì",
        1 : "Martedì",
        2 : "Mercoledì",
        3 : "Giovedì",
        4 : "Venerdì",
        5 : "Sabato",
        6 : "Domenica"
    }

    if have_to_send:
        # Get the day
        day_week_day = datetime.datetime.today().weekday()
        day = per_bene[day_week_day]

        # Sending to Avack users
        if (day == "Lunedì" or day == "Martedì" or day == "Mercoledì" or day == "Giovedì") and have_to_send == "Pranzo" and canteen_closed_da == False:
            canteen = "D'Avack"
            msg_menu = get_updated_menu(canteen, day, have_to_send)

            if msg_menu == "Errore":
                for chat_id in db.get_admins():
                    try:
                        bot.sendMessage(chat_id, err_msg, parse_mode="Markdown")
                    except telepot.exception.TelegramError as e:
                        if e.error_code == 400:
                            print(Fore.YELLOW + "[WARNING] Non sono riuscito ad inviare il messaggio a: " + chat_id)
            else:
                for chat_id in db.get_users_with_pref("notif_da", True):
                    print(Fore.YELLOW + "[SENDING AVACK] Sto inviando un messaggio a: " + chat_id)
                    keyboard = InlineKeyboardMarkup(inline_keyboard=[
                                [dict(text='Offrici una birra!', url="https://www.paypal.me/azzeccagarbugli")]])

                    # Prints the menu in a kawaii way
                    try:
                        bot.sendMessage(chat_id, msg_menu, parse_mode="Markdown")
                    except telepot.exception.TelegramError as e:
                        if e.error_code == 400:
                            print(Fore.YELLOW + "[WARNING] Non sono riuscito ad inviare il messaggio a: " + chat_id)

        # Sending to ColleParadiso users
        if (day == "sabato" or day == "domenica") and have_to_send == "Cena" and canteen_closed_cp == True:
            pass
        else:
            canteen = "Colle Paradiso"
            msg_menu = get_updated_menu(canteen, day, have_to_send)

            if msg_menu == "Errore":
                for chat_id in db.get_admins():
                    try:
                        bot.sendMessage(chat_id, err_msg, parse_mode="Markdown")
                    except telepot.exception.TelegramError as e:
                        if e.error_code == 400:
                            print(Fore.YELLOW + "[WARNING] Non sono riuscito ad inviare il messaggio a: " + chat_id)
            else:
                if have_to_send == "Pranzo":
                    l_or_d = "l"
                elif have_to_send == "Cena":
                    l_or_d = "d"

                for chat_id in db.get_users_with_pref("notif_cp_" + l_or_d, True):
                    print(Fore.YELLOW + "[SENDING COLLEPARADISO] Sto inviando un messaggio a: " + chat_id)
                    keyboard = InlineKeyboardMarkup(inline_keyboard=[
                                [dict(text='Offrici una birra!', url="https://www.paypal.me/azzeccagarbugli")]])

                    try:
                        bot.sendMessage(chat_id, msg_menu, parse_mode="Markdown")
                    except telepot.exception.TelegramError as e:
                        if e.error_code == 400:
                            print(Fore.YELLOW + "[WARNING] Non sono riuscito ad inviare il messaggio a: " + chat_id)

    time.sleep(upd_time)


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
    quit()

with open(pidfile, 'w') as f:
    f.write(str(os.getpid()))

# Start working
try:
    # Checks if all the files and folders exist
    check_dir_files()

    # Initializing the DB
    db = Firebase("credentials_db.json")

    bot = telepot.DelegatorBot(TOKEN, [
        include_callback_query_chat_id(
            pave_event_space())(
                per_chat_id(types=['private']), create_open, UnicamEat, timeout=120),
    ])

    # Checking if some messages has been sent to the bot
    try:
        updates = bot.getUpdates()
        if updates:
            last_update_id = updates[-1]['update_id']
            bot.getUpdates(offset=last_update_id + 1)
    except urllib3_exceptions.MaxRetryError:
        print(Fore.RED + "[ERROR] Tentativo di connessione fallito, assicurati di essere connesso alla rete e riprova.")
        quit()

    # Creating a new thread for the listening of the messages
    MessageLoop(bot).run_as_thread()

    print(Style.DIM + "\nDa grandi poteri derivano grandi responsabilità...\n")

    # Notification system as a different thread
    while(1):
        update(updating_time)
finally:
    os.unlink(pidfile)
