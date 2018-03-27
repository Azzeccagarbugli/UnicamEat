import os

# Your token Bot, you can get it on Telegram Bot Father
TOKEN = ''
bot_name  = "@UnicamEatBot"

# Start message
start_msg = "*Benvenuto su @UnicamEatBot!*\nQui troverai il menù del giorno offerto dall'ERSU, per gli studenti di Unicam, per le mense di Colle Paradiso e del D'Avack. "\
            "\nInizia digitando il comando /menu per accedere al menu o prova altri comandi per scoprire maggiori informazioni riguardo al bot. "\
            "Se hai qualche dubbio o perplessità prova il comando /help per ulteriori dettagli."\
            "\n\n_Il bot e' stato creato in modo non ufficiale, né ERSU Camerino né Unicam sono responsabili in alcun modo._"

# Help message
help_msg = "Il servizio offerto da *Unicam Eat!* permette di accedere a diversi contenuti, raggiungibili attraverso determinati comandi tra cui:\n\n"\
           "*/info*: fornisce ulteriori informazioni sul bot e sui suoi creatori\n\n"\
           "*/menu*: mediante questo comando è possibile ottenere il menù del giorno, selezionando in primo luogo la *mensa* in cui si desidera mangiare, "\
           "succesivamente il *giorno* e infine il parametro *pranzo* o *cena* in base alle proprie esigenze\n\n"\
           "*/orari*: visualizza gli orari delle mense disponibili nel bot\n\n"\
           "*/prezzi*: inoltra una foto contenente il listino dei prezzi e, in particolar modo, la tabella di conversione di quest'ultimi\n\n"\
           "*/avvertenze*: inoltra all'utente delle avvertenze predisposte dalla mensa operante\n\n"\
           "*/allergeni*: vengono visualizzati gli alimenti _o i loro componenti_ che possono scatenare reazioni immuno-mediate\n\n"\
           "*/impostazioni*: comando che permette di modificare alcuni settaggi del bot secondo le proprie necessità"\

# Closed canteen
closed_msg = "La mensa del D'Avack nei giorni <b>Venerdì</b>, <b>Sabato</b> e <b>Domenica</b> rimane chiusa sia "\
             "per pranzo che per cena. Riprova a inserire il comando /menu e controlla la mensa "\
             "di <b>Colle Pardiso</b> per ottenere i menù da te desiderati"

# Opening time
opening_msg = "<b>• D'Avack</b>\n"\
            "Aperta tutti i giorni della settimana durante il pranzo, esclusi <b>Venerdì</b>, <b>Sabato</b> e <b>Domenica</b>, dalle ore <b>12:30</b> alle ore <b>14:15</b>. "\
            "\n<i>Posizione:</i> /posizione_avak\n"\
            ""\
            "\n<b>• Colle Paradiso</b>\n"\
            "Aperta tutti i giorni della settimana dalle ore <b>12:30</b> alle ore <b>14:15</b> e dalle ore <b>19:30</b> alle ore <b>21:15</b>."\
            "\nDurante il week-end la mensa, invece, rimarrà aperta <b>esclusivamente</b> per pranzo dalle ore <b>12:30</b> alle ore <b>13:30</b>."\
            "\n<i>Posizione:</i> /posizione_colleparadiso"

# Info message
info_msg =  "*Unicam Eat!* nasce con l'idea di aiutare tutti gli studenti di Unicam nella visualizzazione dei menù "\
            "offerti dal servizio di ristorazione dell'Ersu, presso le mense di *Colle Paradiso* e *D'Avack*. "\
            "\nÈ possibile utilizzare i pulsanti disponibili di seguito per ottenere informazioni riguardo il codice sorgente del Bot e "\
            "per segnalare direttamente un problema di malfunzionamento al team di sviluppo. "\
            "\n\nInfine, se sei soddisfatto del servizio messo a dispozione e della qualità di quest'ultimo puoi donare una birra agli sviluppatori, "\
            "ne saremmo davvero felici"

# Food warning message
allergeni_msg = "In allegato la lista degli allergeni approvata dal Regolamento Europeo n.1169/2011"

# General warning
warning_msg = "Si avvisano gli utenti che, nel personalizzare il proprio pasto, è consentito ritirare <b>al massimo 2 porzioni di ciascuna pietanza o prodotto</b>, "\
              "nel modo indicato: \n"\
              "• <b>Max n. 2</b> - Primi piatti\n"\
              "• <b>Max n. 2</b> - Secondi piatti\n"\
              "• <b>Max n. 2</b> - Contorni\n"\
              "• <b>Max n. 2</b> - Panini\n"\
              "• <b>Max n. 2</b> - Prodotti confezionati\n"\
              "• <b>Max n. 2</b> - Prodotti a scelta fra Frutta, Yogurt e Dolce\n\n"\
              "<i>È severamente vietato</i>, <b>agli utenti in attesa del ritiro del pasto, toccare piatti e pietanze disponibili sul bancone self-service, senza ritirarli. "\
              "Qualora venissero ritirati non sarà più possibile riconsegnarli.</b>\n\n"\
              "<i>È possibile </i><b>riconsegnare il pasto durante il percorso self-service, solamente prodotti confezionati.</b>\n\n"\
              "<i>È altresì assolutamente vietato</i> <b>prelevare più di tre tovaglioli ed un bicchiere, a pasto.</b>"

# Settings message
settings_msg  =  "Attraverso le impostazioni potrai cambiare diversi parametri all'interno del bot: "\
                 "\n• *Lingua*: passa dalla lingua italiana a quella inglese, o viceversa"\
                 "\n• *Notifiche*: abilita le notifiche per il menù del giorno"\

# Prices message
prices_msg = "In allegato la lista dei prezzi con annessa tabella di corrispondenza"

# Fail conversion
fail_conversion_msg = "_Carissimo utente, ci dispiace che la conversione del menù non sia andata a buon fine. Segnala gentilmente l'errore agli sviluppatori "\
                      "che provederrano a risolvere quest'ultimo_"

# Courses names
courses_texts = ["🍝 - *Primi:*\n", "🍖 - *Secondi:*\n", "🍕 - *Pizza/Panini:*\n", "🍰 - *Altro:*\n", "🧀 - *Extra:*\n", "🍺 - *Bevande:*\n"]

# Dictionaries
courses_dictionaries = [
    ["past", "zupp", "passat", "tagliatell", "riso", "chicche", "minestron", "penn", "chitarr", "tortellin", "prim", "raviol", "maccheroncin"],
    ["panin", "pizz", "crostin", "piadin", "focacci"],
    ["frutt", "yogurt", "contorn", "dolc", "pan", "sals"],
    ["porzionat", "formaggi", "olio", "confettur", "cioccolat", "asport"],
    ["lattin", "brick", "acqua"]
]

# General directory
directory_fcopp = os.path.dirname(os.path.abspath(__file__))

# Directory PDF, directory .txt and general directories
pdfDir   = directory_fcopp + "/PDF/"
txtDir   = directory_fcopp + "/Text/"
boolDir  = directory_fcopp + "/Boolean/"
logDir   = directory_fcopp + "/Log/"
usNoDir  = directory_fcopp + "/UserNotification/"
usersDir = directory_fcopp + "/Users/"
dailyusersDir = usersDir + "DailyUsers/"
qrCodeDir = directory_fcopp + "/QRCode/"

# Bool file
boolFile = boolDir + "update_menu.txt"

# Users Database
usersFile = usersDir + "users_db.txt"

# Times for the notification
notification_lunch = {12, 30}
notification_dinner = {18, 30}

# Admin allowed
admins_array = {22}

class color:
    PURPLE    = '\033[95m'
    CYAN      = '\033[96m'
    DARKCYAN  = '\033[36m'
    BLUE      = '\033[94m'
    GREEN     = '\033[92m'
    YELLOW    = '\033[93m'
    RED       = '\033[91m'
    BOLD      = '\033[1m'
    ITALIC    = '\033[3m'
    UNDERLINE = '\033[4m'
    END       = '\033[0m'
