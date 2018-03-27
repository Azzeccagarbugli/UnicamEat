

![alt text](https://i.imgur.com/oxhwj19.png "UnicamEat!")

[![forthebadge](http://forthebadge.com/images/badges/made-with-python.svg)](https://www.python.org/)
[![forthebadge](http://forthebadge.com/images/badges/built-with-love.svg)](https://www.paypal.me/azzeccagarbugli)
[![forthebadge](http://forthebadge.com/images/badges/powered-by-water.svg)](https://it.wikipedia.org/wiki/Acqua)
[![forthebadge](http://forthebadge.com/images/badges/cc-by-nd.svg)](https://opensource.org/licenses/MIT)

**Unicam Eat!** è un bot Telegram ideato per la gestione dei menù settimanali offerti dal servizio di ristorazione dell'**ERSU** agli studenti Unicam.

***

## Idea e scopo

L'idea e lo scopo che ci alla base del servizio sono molto semplici: *fornire con una maggiore efficienza i menù agli studenti universitari, e soprattutto, rendere più accessibile l'accesso a quest'ultimi,* utilizzando una piattaforma come Telegram che è in grado di mettere in simbiosi questi due aspetti.

Fondamentalmente i menù universitari dell'ERSU di Camerino, vengono **esclusivamente** distribuiti mediante il sito ufficiale di quest'ultimo attraverso dei semplici file PDF e quindi abbiamo pensato di andare a rendere il servizio più *usufruibile* e *istantaneo*.

## Caratteristiche

*Look at the menu of the day, but do it with style*

Di seguito le principali caratteristiche di **Unicam Eat!**:
* Ottenere il menù del giorno, o di un giorno qualsiasi della settimana
* Piattaforma basata su un software solido e affidabile
* Possibilità di ricevere notifiche per il menù del giorno
* Controllare prezzi, orari e molto altro grazie a un semplice click
* Condividere il menù del giorno
* Servizio dinamico ed elegante

## Utilizzo del Bot

<img align="left" width="202" src="https://i.imgur.com/qDUExac.jpg"> 

Come primo step è fondamentale andare ad aggiungere il **bot** nella prorpia lista dei contatti all'interno di Telegram, è possibile infatti raggiungere **Unicam Eat!** mediante il seguente [**link**](https://t.me/UnicamEatBot/).

Una volta aggiunto il servizio all'interno dell'applicazione di messaggistica basterà usufruire dei comandi, elencati all'interno del comando di riferimento ``/help``, per effettuare le richieste desiderate.

Sicuramente la feature più interessante offerta da **Unicam Eat!** è quella di andare a _inoltare messaggi di testo_ contenenti il menù del giorno per permettere una **maggiore rapidità di visualizzazione** e soprattutto una **maggiore efficenza nell'andare a reperire il menù selezionato**.

Per accedere a questa feature basterà digitare il comando ``/menu`` e a questo punto il bot guiderà l'utente verso la selezione innanzitutto della mensa in cui si desidera mangiare, e in seguito chiederà all'utente di quale giorno necessita il menù.

Durante l'intera procedura di selezione l'utente verrà aiutato nella scelta dei parametri disponibili grazie a delle tastiera dinamiche che andranno a migliorare la **User Experience** per rendere l'utilizzo di **Unicam Eat!** decisamente _user friendly_.
</br>

## Struttura di Unicam Eat!

Unicam Eat! come già affermato in precedenza è un bot Telegram. Questa piattaforma di messaggistica, infatti, mette a disposizione delle API che gli sviluppatori possono usufruire per andare a interfacciarsi con Telegram stesso. 

Il framework adoperato in questo caso è stato [**Telepot**](http://telepot.readthedocs.io/en/latest/).

---
### Gli elementi cardini del progetto

Abbiamo strutturato il nostro codice sorgente seguendo dei canoni **scrupolosi** e **ferrei**, e il risultato è stato eccelente.

In questo modo il software è diviso in sezioni, ben distinguibili tra loro. Questo **stile di coding** consente una maggiore facilità di studio e sopratutto una fase di *debugging* davvero alla portata di chiunque.


#### Il download dei file

Il core del progetto sta nell'andare a scaricare, attraverso delle request, i file PDF contenenti il menù richiesto e convertirli, grazie all'aiuto di **PDFMiner**, in semplici file di testo con i quali è possibile lavorare in maniera decisamente più semplice.

```python
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

    infile = open(pdfDir + fname, 'rb')
    for page in PDFPage.get_pages(infile, pagenums):
        interpreter.process_page(page)
    infile.close()
    converter.close()
    text = output.getvalue()
    output.close()

    textFilename = txtDir + "converted.txt"
    textFile = open(textFilename, "w")
    textFile.write(text)
    textFile.close()
```
#### Algoritmo di sorting

Una volta effettuata la conversione, e quindi ottenuto il file di testo desiderato, si passa alla fase più delicata dell'intero processo, ovvero, andare a riordinare in maniera più affidabile possibile il menù del giorno seguendo le linee guida del PDF originale.

Questa parte del software viene gestita in maniera davvero dettagliata e meticolosa per evitare eventuali problemi di qualsiasi genere. 


È possibile accedere a questa parte del codice consultando la funzione *advanced_read_txt()* all'interno del file [functions.py](https://github.com/Azzeccagarbugli/UnicamEat/blob/master/functions.py).
```python
def advanced_read_txt(canteen, day, launch_or_dinner = "Pranzo"):
    """
    Format the messagge of the selected menu
    """
    txtName = txtDir + str(canteen) + "_" +  str(day) + ".pdf.txt"

    # Convert in the right day and the right canteen, just for good appaerence
    msg_menu = "🗓 - *{}* - *{}* - *{}*\n\n".format(clean_canteen(canteen), clean_day(day), launch_or_dinner)

    # Getting ready to work
    my_file = open(txtName, "r")
    out = my_file.readlines()
    my_file.close()

    # Divides by sections the .txt
    my_char = '\n'.encode("unicode_escape").decode("utf-8")
    secs = []
    current_sec = []

    ...
```

#### Invio del menù attraverso Telegram

Una volta completate le prime due fasi si può passare alla fase finale cioè, sostanzialmente, l'invio del messaggio contenente il menù mediante Telegram. 

Come già affermato in precedenza, grazie all'uso di **Telepot**, possiamo utilizzare le API messe a disposizione da Telegram e quindi andare ad usufruire una serie davvero molto ampia di *features* che vanno a costituire la struttura stessa del bot.

```python
try:
    # Start working
    bot = telepot.Bot(TOKEN)

    # Checking if some messages has been sent to the bot
    updates = bot.getUpdates()
    if updates:
        last_update_id = updates[-1]['update_id']
        bot.getUpdates(offset = last_update_id + 1)

    # Starting message_loop
    bot.message_loop({'chat': handle,
                      'callback_query': on_callback_query})

    print("Da grandi poteri derivano grandi responsabilità")

    # Notification system
    while(1):
        update()
finally:
    os.unlink(pidfile)
```


## Installazione

Il bot viene rilasciato con licenza MIT, ciò significa che chiunque voglia modificare o proporre suggerimenti per implementare nuove funzionalità o per risolvere eventuali problemi, può farlo liberamente utilizzando GitHub.

---

Per compilare il codice sulla propria macchina basterà installare le dipendenze del software attraverso questo comando:
```bash
$ sudo pip3 install -r requirements.txt
```
Dopodichè sarà necessario andare a importare nel file ``UnicamEat.py`` il file ``settings_dist.py`` invece che il file ``settings.py``, andando a modificare secondo le prorpie scelte i parametri all'interno del file stesso.

Una volta installate le dipendenze e, modificate le varie impostazioni all'interno del file ``settings_dist.py``, basterà lanciare il seguente comando:
```bash
$ python3 UnicamEat.py
```

## Crediti

Lo sviluppo del codice è stato effettuato da [Francesco Coppola](https://github.com/Azzeccagarbugli) e da [Antonio Strippoli](https://github.com/Porchetta).

*Il bot è stato creato in modo non ufficiale, né ERSU Camerino né Unicam sono responsabili in alcun modo*
