# Your token Bot, you can get it on Telegram Bot Father
TOKEN = 'YOUR_TOKEN'

bot_name = "@UnicamEatBot"

# Start message
start_msg = "*Benvenuto su @UnicamEatBot!*\nQui troverai il menù del giorno offerto dall'ERSU, per gli studenti di Unicam, per le mense di Colle Paradiso e del D'Avack. "\
            "\nInizia digitando il comando /menu per accedere al menu o prova altri comandi per scoprire maggiori informazioni riguardo al bot. "\
            "Se hai qualche dubbio o perplessità prova il comando /help per ulteriori dettagli."\
            "\n\n_Il bot e' stato creato in modo non ufficiale, né ERSU Camerino né Unicam sono responsabili in alcun modo._"

# Help message
help_msg = "UNICAM E' VERAMENTE EUFORICA"

# Directory
directory_fcopp = 'YOUR_PATH'

# Closed canteen
closed_msg = "La mensa del D'Avack nei giorni <b>Venerdì</b>, <b>Sabato</b> e <b>Domenica</b> rimane chiusa sia "\
            "per pranzo che per cena. Riprova a inserire il comando /menu e controlla la mensa "\
            "di <b>Colle Pardiso</b> per ottenere i menù da te desiderati"

# Opening time
opening_msg = "<b>D'Avack</b>\n"\
            "Aperta tutti i giorni della settimana durante il pranzo, esclusi <b>Venerdì</b>, <b>Sabato</b> e <b>Domenica</b>, dalle ore <b>12:30</b> alle ore <b>14:15</b>. "\
            "\n<i>Posizione:</i> /posizione_avak\n"\
            ""\
            "\n<b>Colle Paradiso</b>\n"\
            "Aperta tutti i giorni della settimana dalle ore <b>12:30</b> alle ore <b>14:15</b> e dalle ore <b>19:30</b> alle ore <b>21:15</b>."\
            "\nDurante il week-end la mensa, invece, rimarrà aperta <b>esclusivamente</b> per pranzo dalle ore <b>12:30</b> alle ore <b>13:15</b>."\
            "\n<i>Posizione:</i> /posizione_colleparadiso"

# Info message
info_msg =  "Unicam Eat! nasce con l'idea di aiutare tutti gli studenti di Unicam nella visualizzazione dei menù "\
            "offerti dal servizio di ristorazione dell'Ersu, presso le mense di *Colle Paradiso* e *D'Avack*. "\
            "\nÈ possibile utilizzare i pulsanti disponibili di seguito per ottenere informazioni rigurado il codice sorgente del Bot e "\
            "per segnalare direttamente un problema di malfunzionamento al team di sviluppo. "\
            "\n\nInfine, se sei soddisfatto del servizio messo a dispozione e della qualità di quest'ultimo puoi donare una birra agli sviluppatori, "\
            "ne saremo davvero felici"

# Food warning message
allergeni_msg = "In allegato la lista degli allergeni approvata dal Regolamento Europeo n.1169/2011"

# Settings message
settings_msg =  "*FUNZIONI SPERIMENTALI NON IMPLEMENTATE, FUNZIONAMENTO NON CORRETTO*"\
                "\n\nAttraverso le impostazioni potrai cambiare diversi parametri all'interno del bot: "\
                "\n• *Lingua*: passa dalla lingua italiana a quella inglese, o viceversa"\
                "\n• *Notifiche*: abilita le notifiche per il menù del giorno"\
                "\n• *Visualizzazione giorni*: visualizza solamente il menù di oggi o domani, non di tutta la settimana"

# Prices message
prices_msg = "In allegato la lista dei prezzi con annessa tabella di corrispondenza"

# Dictionaries
courses_dictionaries = [
    ["past", "zupp", "passat", "tagliatell", "ris", "chicche", "minestron", "penn", "chitarr", "prim"],
    ["panin", "pizz", "crostin", "piadin", "focacci"],
    ["frutt", "yogurt", "contorn", "dolc", "pan", "sals"],
    ["porzionat", "formaggi", "olio", "confettur", "cioccolat", "asport"],
    ["lattin", "brick", "acqua"]
]

# Directory PDF and directory .txt
pdfDir   = directory_fcopp + "/PDF/"
txtDir   = directory_fcopp + "/Text/"
boolFile = directory_fcopp + "/Boolean/update_menu.txt"

# Admin allowed
admins_array = {22, 222}

class color:
   PURPLE = '\033[95m'
   CYAN = '\033[96m'
   DARKCYAN = '\033[36m'
   BLUE = '\033[94m'
   GREEN = '\033[92m'
   YELLOW = '\033[93m'
   RED = '\033[91m'
   BOLD = '\033[1m'
   ITALIC = '\033[3m'
   UNDERLINE = '\033[4m'
   END = '\033[0m'
