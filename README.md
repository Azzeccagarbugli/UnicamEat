

![alt text](https://i.imgur.com/oxhwj19.png "UnicamEat!")

[![forthebadge](http://forthebadge.com/images/badges/made-with-python.svg)](https://www.python.org/)
[![forthebadge](http://forthebadge.com/images/badges/built-with-love.svg)](https://www.paypal.me/azzeccagarbugli)
[![forthebadge](http://forthebadge.com/images/badges/powered-by-water.svg)](https://it.wikipedia.org/wiki/Acqua)
[![forthebadge](http://forthebadge.com/images/badges/cc-by-nd.svg)](https://opensource.org/licenses/MIT)

**Unicam Eat!** è un bot Telegram ideato per la gestione dei menù settimanali offerti dal servizio di ristorazione dell'**ERDIS** agli studenti Unicam.

***

## Idea e scopo

L'idea e lo scopo che ci alla base del servizio sono molto semplici: *fornire con una maggiore efficienza i menù agli studenti universitari, e soprattutto, rendere più accessibile l'accesso a quest'ultimi,* utilizzando una piattaforma come Telegram che è in grado di mettere in simbiosi questi due aspetti.

Fondamentalmente i menù universitari dell'ERDIS di Camerino, vengono **esclusivamente** distribuiti mediante il sito ufficiale di quest'ultimo attraverso dei semplici file PDF e quindi abbiamo pensato di andare a rendere il servizio più *usufruibile* e *istantaneo*.

## Caratteristiche

*“Look at the menu of the day, but do it with style”*

Di seguito le principali caratteristiche di **Unicam Eat!**:
* Ottenere il menù di un qualsiasi giorno della settimana in maniera intuitiva
* Software basato su un framework solido e affidabile
* Possibilità di ricevere notifiche per il menù del giorno
* Controllare prezzi, orari e molto altro grazie a un semplice click
* Condividere il menù del giorno grazie alle funzionalità di Telegram
* Utilizzo del database di Google, Firebase per la gestione in real-time dei dati
* Servizio dinamico ed elegante

## Utilizzo del Bot

<img align="left" width="300" src="https://i.imgur.com/qDUExac.jpg">

Come primo step è fondamentale andare ad aggiungere il **Bot** nella prorpia lista dei contatti all'interno di Telegram, è possibile infatti raggiungere **Unicam Eat!** mediante il seguente [**link**](https://t.me/UnicamEatBot/).

Una volta aggiunto il servizio all'interno dell'applicazione di messaggistica basterà usufruire dei comandi, elencati all'interno del comando di riferimento ``/help``, per effettuare le richieste desiderate.

Sicuramente la feature più interessante offerta da **Unicam Eat!** è quella di andare a _inviare messaggi di testo_ contenenti il menù del giorno per permettere una **maggiore rapidità di visualizzazione** rispetto ai servizi presenti attualmente sul sito dell' **ERDIS** e soprattutto una **maggiore efficenza nell'andare a reperire il menù selezionato**.

Per accedere a questa feature basterà digitare il comando ``/menu`` e a questo punto il Bot guiderà l'utente verso la selezione innanzitutto della mensa in cui si desidera mangiare, e in seguito chiederà all'utente di quale giorno necessita il menù.

Durante l'intera procedura di selezione l'utente verrà aiutato nella scelta dei parametri disponibili grazie a tastiera dinamiche che andranno a migliorare la **User Experience**, per rendere l'utilizzo di **Unicam Eat!** decisamente più _user friendly_.
<br><br><br>

## Struttura di Unicam Eat!

**Unicam Eat!** come già affermato in precedenza è un bot Telegram. Questa piattaforma di messaggistica, infatti, mette a disposizione delle API che gli sviluppatori possono usufruire per andare a interfacciarsi con Telegram stesso.

Il framework adoperato in questo caso è stato [**Telepot**](http://telepot.readthedocs.io/en/latest/).

---
### Gli elementi cardini del progetto

Abbiamo strutturato il nostro codice sorgente seguendo dei canoni **scrupolosi** e **ferrei**, e il risultato è stato eccelente.

In questo modo il software è diviso in sezioni, ben distinguibili tra loro. Questo **stile di coding** consente una maggiore facilità di studio e sopratutto una fase di *debugging* davvero alla portata di chiunque.

#### Query al file .xml

Grazie ai file fornitici dall'**ERDIS** siamo in grado di effettuare una query su un file .xml che ci restituirà come risultato le pietanze relative a ogni giorno della settimana con allegata descrizione e costo di quest'ultimi.

È possibile accedere a questa parte del codice consultando la funzione *get_updated_menu()* all'interno del file [functions.py](https://github.com/Azzeccagarbugli/UnicamEat/blob/master/functions.py).
```python
def append_product(index, product):
      """
      Internal function to append products to courses list
      """
      # Getting product_name
      product_name = product.attrib.get('Descrizione').capitalize()

      # Fixing typo error
      if index == 5:
          if "The" in product_name:
              product_name = product_name.replace("The", "Tè")

      # Concatenating prices
      if product.attrib.get('FlagPrezzo') == 'S':
          product_name += " _[{} €]_".format(product.attrib.get('Prezzo'))
      else:
          product_name += " _[{} pt]_".format(product.attrib.get('Punti'))

      # Appending product
      courses[index].append(product_name)

    ...
```

#### Invio del menù attraverso Telegram

Una volta completate le prime due fasi si può passare alla fase finale cioè, sostanzialmente, l'invio del messaggio contenente il menù mediante Telegram.

Come già affermato in precedenza, grazie all'uso di **Telepot**, possiamo utilizzare le API messe a disposizione da Telegram e quindi andare ad usufruire una serie davvero molto ampia di *features* che vanno a costituire la struttura stessa del bot.

```python
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
```

#### Controllo e sicurezza dell'intero sistema attraverso Firebase

Grazie all'utilizzo di Firebase, tecnologia molto recente basata su piattaforme di casa Google, possiamo garantire **sicurezza** e **privacy** a tutti i dati degli utenti e gestire le risorse del database in una maniera davvero efficente.

```python
class Firebase:
.
.
.
  def add_user(self, user_info):
        """
        Adds a new user under /users
        """
        if not self.exists_user(user_info['id']):
            # Trying to get first name
            if 'first_name' in user_info:
                first_name = user_info['first_name']
            else:
                first_name = "Not Defined"

            # Trying to get last name
            if 'last_name' in user_info:
                last_name = user_info['last_name']
            else:
                last_name = "Not Defined"

            # Trying to get username
            if 'username' in user_info:
                username = user_info['username']
            else:
                username = "Not Defined"

            db.reference('users/' + str(user_info['id'])).update({
                "info": {
                    "first_name": first_name,
                    "last_name": last_name,
                    "username": username
                },
                "preferences": {
                    "language": "IT",
                    "notif_cp_d": True,
                    "notif_cp_l": True,
                    "notif_da": True
                },
                "role": 0  # Default user
            })
            return True
        return False
```

## Installazione

Il Bot viene rilasciato con licenza **MIT**, ciò significa che chiunque voglia modificare o proporre suggerimenti per implementare nuove funzionalità o per risolvere eventuali problemi, può farlo liberamente utilizzando GitHub.

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

*Il Bot è stato creato in modo non ufficiale, per poi diventarlo grazie alla collaborazione con lo stuff dell'ERDIS di Camerino*
