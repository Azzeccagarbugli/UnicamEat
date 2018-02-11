# Unicam Eat!

![alt text](https://i.imgur.com/HPCaYrx.png "UnicamEat!")

Unicam Eat! è un bot Telegram ideato per la gestione dei menù settimanali offerti dal servizio di ristorazione dell'**ERSU** agli studenti Unicam.

***

## Idea e scopo

L'idea e lo scopo che ci alla base del servizio sono molto semplici: *fornire con una maggiore efficenza i menù agli studenti universitari, e soprattutto, rendere più accessibile l'accesso a quest'ultimi,* utilizzando una piattaforma come Telegram che è in grado di mettere in simbiosi questi due aspetti.
Fondamentalmente i menù universitari dell'ERSU di Camerino, vengono **esclusivamente** distribuiti mediante il sito ufficiale di quest'ultimo attraverso dei semplici file PDF e quindi abbiamo pensato di andare a rendere il servizio più *usufruibile* e *istantaneo*.

## Struttura di Unicam Eat!

Unicam Eat! come già affermato in precedenza è un bot Telegram. Questa piattafroma di messaggistica, infatti, mette a dispozione delle API che gli sviluppatori possono usufruire per andare a interfacciarsi con Telegram stesso. Il framework adoperato in questo caso è stato **Telepot**.
Il core del progetto sta nell'andare a scaricare, attraverso delle request, i file PDF contenenti il menù e convertirli, grazie all'aiuto di PDFMiner, in semplici file di testo con i quali è possibile lavorare in maniera decisamente più semplice.

## Installazione

Il bot viene rilasciato con licenza MIT, ciò significa che chiunque voglia modificare o proporre suggerimenti per implementare nuove funzionalità o per risolvere eventuali, può farlo liberamente utilizzando GitHub.

---

Per compilare il codice sulla propria macchina basterà installare le dipendenze del software attraverso questo comando:
```bash
$ sudo pip install -r requirements.txt
```
Una volta installate le dipendenze, sarà necessario modificare i vari parametri all'interno del file *settings_dist.py* per poi infine lanciare il comando:
```bash
$ python3 UnicamEat.py
```

## Crediti

Lo sviluppo del codice è stato effettuato da [Francesco Coppola](https://github.com/Azzeccagarbugli) e da [Antonio Strippoli](https://github.com/Porchetta).
*Il bot è stato creato in modo non ufficiale, né ERSU Camerino né Unicam sono responsabili in alcun modo*
