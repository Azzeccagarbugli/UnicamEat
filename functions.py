"""
Unicam Eat! - Telegram Bot (Core functions file)
Authors: Azzeccagarbugli (f.coppola1998@gmail.com)
         Porchetta       (clarantonio98@gmail.com)

Da rivedere:
- report_error
- boolean file
"""

from settings import Dirs, courses_dictionaries, boolFile

import os
import requests
import filecmp

import time
import datetime

from colorama import Fore

from io import StringIO

from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfpage import PDFPage

import numpy as np

import qrcode

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker


def server_status():
    """
    This function pings the ERSU's server

    :returns: bool -- **True Success**, **False Error**.
    """
    # Try to ping the server
    SITE_URL = "http://www.ersucam.it/"

    if requests.head(SITE_URL).status_code == 200:
        return True
    else:
        return False


def dl_updated_pdf(canteen, day):
    """
    Tries to download the updated pdf from Ersu's website

    :param canteen: Name of the canteen.
    :type canteen: str.
    :param day: Day of the week.
    :type day: str.
    :returns: bool -- **True Success**, **False Error**.
    """
    # Directory where put the file, and name of the file itself
    filename = Dirs.PDF + canteen + '_' + day + '.pdf'

    if server_status():
        # Check the existence of the files
        url = get_url(canteen, day)
        request = requests.get(url)

        # Writing pdf
        with open(filename, 'wb') as f:
            f.write(request.content)
        return True
    else:
        return False


def check_updated_txt(pdfFileName):
    """
    Checks the Dirs.TXT updating if necessary the txt file containing the menu of the day

    :param pdfFileName: Name of the pdf to check.
    :type pdfFileName: str.
    :returns: bool::
        - **True** -- The update was successfull.
        - **False** -- There was an error and we don't have the most updated PDF available.
    """
    if not os.path.isfile(Dirs.TXT + pdfFileName + ".txt"):
        print(Fore.CYAN + "[FILE] Ho aggiunto un nuovo file convertito in .txt")

        os.rename(Dirs.TXT + "converted.txt", Dirs.TXT + pdfFileName + ".txt")
    elif today_weekend() != 0:
        if filecmp.cmp(Dirs.TXT + "converted.txt", Dirs.TXT + pdfFileName + ".txt"):
            print(Fore.CYAN + "[FILE] I due file erano identici, ho cestinato converted.txt")

            os.remove(Dirs.TXT + "converted.txt")
        else:
            print(Fore.CYAN + "[FILE] I due file erano diversi ed ho voluto aggiornare con l'ultimo scaricato")

            os.remove(Dirs.TXT + pdfFileName + ".txt")
            os.rename(Dirs.TXT + "converted.txt", Dirs.TXT + pdfFileName + ".txt")
    else:
        print(Fore.CYAN + "[FILE] Controllo se ho i file aggiornati o meno...")

        if get_bool() == "False":
            if filecmp.cmp(Dirs.TXT + "converted.txt", Dirs.TXT + pdfFileName + ".txt"):
                print(Fore.CYAN + "[FILE] I due file sono ancora uguali, inviato un msg di errore.")

                return False
            else:
                print(Fore.CYAN + "[FILE] Ho trovato un aggiornamento ed ho sostituito il file con quello più recente")

                os.remove(Dirs.TXT + pdfFileName + ".txt")
                os.rename(Dirs.TXT + "converted.txt", Dirs.TXT + pdfFileName + ".txt")

                write_bool("True")
        else:
            print(Fore.CYAN + "[FILE] Dovrei avere i file aggiornati online, la booleana era True.")

            if filecmp.cmp(Dirs.TXT + "converted.txt", Dirs.TXT + pdfFileName + ".txt"):
                print(Fore.CYAN + "[FILE] I due file erano identici, ho cestinato converted.txt")

                os.remove(Dirs.TXT + "converted.txt")
            else:
                print(Fore.CYAN + "[FILE] I due file erano diversi ed ho voluto aggiornare con l'ultimo scaricato")

                os.remove(Dirs.TXT + pdfFileName + ".txt")
                os.rename(Dirs.TXT + "converted.txt", Dirs.TXT + pdfFileName + ".txt")
    return True


def convert_in_txt(fname, pages=None):
    """
    Converts a .pdf file to a .txt file, using pdfminer.six lib

    :param fname: The name of the PDF to use.
    :type name: str.
    :param pages: The number of the pages of the PDF's file.
    :type name: int.
    """
    if not pages:
        pagenums = set()
    else:
        pagenums = set(pages)

    output = StringIO()
    manager = PDFResourceManager()
    converter = TextConverter(manager, output, laparams=LAParams())
    interpreter = PDFPageInterpreter(manager, converter)

    infile = open(Dirs.PDF + fname, 'rb')
    for page in PDFPage.get_pages(infile, pagenums):
        interpreter.process_page(page)
    infile.close()
    converter.close()
    text = output.getvalue()
    output.close()

    textFilename = Dirs.TXT + "converted.txt"
    textFile = open(textFilename, "w")
    textFile.write(text)
    textFile.close()


def advanced_read_txt(canteen, day, lunch_or_dinner="Pranzo"):
    """
    Reads the txt of the menu requested, formatting and ordering prices and foods

    :param canteen: The name of the canteen.
    :type canteen: str.
    :param day: A day of the week.
    :type day: str.
    :param lunch_or_dinner: moment of the day of which we want the menu.
    :type lunch_or_dinner: str.
    :returns:  str -- The menu requested given in a string.
    """
    txtName = Dirs.TXT + str(canteen) + "_" + str(day) + ".pdf.txt"

    # Convert in the right day and the right canteen, just for good appaerence
    msg_menu = "🗓 - *{}* - *{}* - *{}*\n\n".format(clean_canteen(canteen), clean_day(day), lunch_or_dinner)

    # Getting ready to work
    my_file = open(txtName, "r")
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
    secs_foods = []
    secs_prices = []

    for sec in secs:
        if sec[0][0].isdigit() and sec[0] != "1 Formaggino":
            secs_prices.append(sec)
        else:
            secs_foods.append(sec)

    del secs

    # IMPORTANT: This will try to understand the structure of the sections produced before
    if not foods_prices_are_ordered(secs_prices, secs_foods):
        c_secs_foods = secs_foods[:]
        c_secs_prices = secs_prices[:]

        i1, i2 = 0, 0
        for i, (prices, foods) in enumerate(zip(c_secs_prices, c_secs_foods)):
            if len(prices) != len(foods):
                i1 = i
                break

        for i, (prices, foods) in enumerate(zip(c_secs_prices, c_secs_foods)):
            if len(prices) != len(foods) and i != i1 and i != i1+1 and i != i1+2:
                i2 = i
                break

        if i1 != 0 and i2 != 0:
            c_secs_prices[i1:i1+3], c_secs_prices[i2:i2+3] = c_secs_prices[i2:i2+3], c_secs_prices[i1:i1+3]
        else:
            print(Fore.RED + "[ERROR] Nice Shit Bro x1000000")

        if not foods_prices_are_ordered(c_secs_prices, c_secs_foods):
            print(Fore.CYAN + "[CONVERSION] ESITO 1: False")

            c_secs_foods  = secs_foods[:]
            c_secs_prices = secs_prices[:]

            # Checks if we have pizza/panini at lunch
            if '1,00€' in c_secs_prices[5] or '0,80€' in c_secs_prices[5]:
                # Checks if we don't have pizza/panini at dinner
                if '1,00€' in c_secs_prices[10] or '0,80€' in c_secs_prices[10]:
                    c_secs_prices[3:5], c_secs_prices[6:8] = c_secs_prices[6:8], c_secs_prices[3:5]
                    c_secs_prices[5],   c_secs_prices[6] = c_secs_prices[6],   c_secs_prices[5]
                    c_secs_prices[6],   c_secs_prices[7] = c_secs_prices[7],   c_secs_prices[6]

                    c_secs_foods = secs_foods[0], secs_foods[2], secs_foods[4], secs_foods[1], secs_foods[3], secs_foods[5], secs_foods[6], secs_foods[7], secs_foods[8], secs_foods[9], secs_foods[10]
                else:
                    c_secs_prices[3:6], c_secs_prices[6:9] = c_secs_prices[6:9], c_secs_prices[3:6]
                    c_secs_foods = secs_foods[0], secs_foods[2], secs_foods[4], secs_foods[1], secs_foods[3], secs_foods[5], secs_foods[6], secs_foods[7], secs_foods[8], secs_foods[9], secs_foods[10], secs_foods[11]

                    if not foods_prices_are_ordered(c_secs_prices, c_secs_foods, more_info = True):
                        c_secs_foods = secs_foods[0], secs_foods[2], secs_foods[4], secs_foods[1], secs_foods[3], secs_foods[8], secs_foods[5], secs_foods[6], secs_foods[7], secs_foods[9], secs_foods[10], secs_foods[11]

            # Checks if we don't have pizza/panini at dinner
            elif '1,00€' in c_secs_prices[9] or '0,80€' in c_secs_prices[9]:
                print(Fore.YELLOW + "[PIZZA STYLE] No pizza no party")
                c_secs_prices[2:4], c_secs_prices[5:7] = c_secs_prices[5:7], c_secs_prices[2:4]
                c_secs_prices[4],   c_secs_prices[5] = c_secs_prices[5],   c_secs_prices[4]
                c_secs_prices[5],   c_secs_prices[6] = c_secs_prices[6],   c_secs_prices[5]

                c_secs_foods = secs_foods[0], secs_foods[2], secs_foods[1], secs_foods[3], secs_foods[4], secs_foods[5], secs_foods[6], secs_foods[7], secs_foods[8], secs_foods[9]
            else:
                c_secs_prices[2:5], c_secs_prices[5:8] = c_secs_prices[5:8], c_secs_prices[2:5]
                c_secs_foods = secs_foods[0], secs_foods[2], secs_foods[1], secs_foods[3], secs_foods[4], secs_foods[5], secs_foods[6], secs_foods[7], secs_foods[8], secs_foods[9], secs_foods[10]

            if not foods_prices_are_ordered(c_secs_prices, c_secs_foods, more_info = True):
                print(Fore.CYAN + "[CONVERSION] ESITO 2: False")
                print(Fore.RED + "[CONVERSION] Non è stato possibile riordinare correttamente la lista")

                return msg_menu + "Errore!"
            else:
                print(Fore.CYAN + "[CONVERSION] ESITO 2: True")

                secs_foods, secs_prices = from_menu_lord(lunch_or_dinner, c_secs_foods, c_secs_prices)
        else:
            print(Fore.CYAN + "[CONVERSION] ESITO 1: True")

            secs_foods, secs_prices = from_menu_lord(lunch_or_dinner, c_secs_foods, c_secs_prices)

    else:
        print(Fore.GREEN + "[SUCCESS CONVERSION] La lista è ordinata, strano...")

    # Creates a sorted menu without repetitions with prices and foods together
    # Tries to create a menu for lunch and another for dinner
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

    # Courses names
    courses_texts = ["🍝 - *Primi:*\n", "🍖 - *Secondi:*\n", "🍕 - *Pizza/Panini:*\n", "🍰 - *Altro:*\n", "🧀 - *Extra:*\n", "🍺 - *Bevande:*\n"]

    for course_text, course in zip(courses_texts, courses):
        msg_menu += course_text
        for el in course:
            msg_menu += "• " + el + "\n"
        msg_menu += "\n"
    msg_menu += "_Il menù potrebbe subire variazioni_"

    return msg_menu


def foods_prices_are_ordered(secs_prices, secs_foods, more_info = False):
    """
    Checks if the list of prices corresponds to the list of foods.

    :param secs_prices: The list containing only prices.
    :type secs_prices: list.
    :param secs_foods: The list containing only foods.
    :type secs_foods: list.
    :param more_info: A debug variable that allows to print more informations to the console.
    :type more_info: bool.
    :returns: bool::
        - **True** -- The sorting was successfull.
        - **False** -- The sorting was unsuccessfull.
    """
    for i, (price, food) in enumerate(zip(secs_prices, secs_foods)):
        if len(price) != len(food):
            if more_info:
                print(Fore.CYAN + "[CONVERSION BUG] C'è ancora un errore. A: " + str(i))
                print(Fore.CYAN + "[CONVERSION BUG] Dettagli:\n" + str(price) + " - " + str(food))
            return False
    return True


def from_menu_lord(lunch_or_dinner, secs_foods, secs_prices):
    """
    Extract from the full menu the lunch or dinner menu

    :param lunch_or_dinner: moment of the day of which we want the menu.
    :type lunch_or_dinner: str.
    :param secs_foods: The list containing only foods.
    :type secs_foods: list.
    :param secs_prices: The list containing only prices.
    :type secs_prices: list.
    :returns: list -- Returns two lists containing foods and prices of the moment of the day wanted.
    """
    moment_foods, moment_prices = [], []
    if lunch_or_dinner == "Pranzo":
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


def append_courses(my_list, dictionary=courses_dictionaries):
    """
    Splits the full list containing prices and foods into the courses

    :param my_list: The list that contain all the foods without sorting.
    :type my_list: list.
    :param dictionary: A dictionary which holds all the words for the sorting of the courses.
    :type dictionary: dictionary.
    :returns:  list -- Courses of the menu wanted.
    """
    courses = [[], [], [], [], [], []]

    for el in my_list:
        for ci, course_dictionary in enumerate(dictionary):
            for word in course_dictionary:
                if word.lower() in el.lower() and "pizzaiola" not in el.lower() and el not in courses[0] and el not in courses[1] and el not in courses[2] and el not in courses[3] and el not in courses[4] and el not in courses[5]:
                    if ci >= 1:
                        courses[ci+1].append(el)
                    else:
                        courses[ci].append(el)

    for el in my_list:
        if el not in courses[0] and el not in courses[1] and el not in courses[2] and el not in courses[3] and el not in courses[4] and el not in courses[5]:
            courses[1].append(el)

    return courses


def is_course(my_list, dictionary=courses_dictionaries):
    """
    Checks which course the list belongs to

    :param my_list: The list that contain all the foods without sorting.
    :type my_list: list.
    :param dictionary: A dictionary which holds all the words for the sorting of the courses.
    :type dictionary: dictionary.
    :returns:  str -- The keyword of the dish.
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


def get_menu_updated(canteen, day, lunch_or_dinner):
    """
    Prepare the updated menu for the notification to the user

    :param canteen: Name of the canteen.
    :type canteen: str.
    :param day: Day of the week.
    :type day: str.
    :param lunch_or_dinner: Moment of the day of which we want the menu.
    :type lunch_or_dinner: str.
    :returns:  str -- The menu requested given in a string.
    """
    while(1):
        if dl_updated_pdf(canteen, day) is False:
            time.sleep(30)
            continue

        pdfFileName = canteen + '_' + day + ".pdf"
        print(Fore.YELLOW + "[SENDING FILE] Sto provando a inviare il PDF - " + pdfFileName)
        convert_in_txt(pdfFileName)

        if check_updated_txt(pdfFileName) is True:
            # Send the message that contain the meaning of the life
            msg_menu = advanced_read_txt(canteen, day, lunch_or_dinner)

            # Try to see if there is a possible error
            if "Errore!" in msg_menu:
                return "Errore"
            else:
                return msg_menu
        else:
            return "Errore"


def readlines_fromfile(path):
    """
    Reads the lines of a file

    :returns: list -- Content of the file it self
    """
    f = open(path, "r")
    out = f.readlines()
    f.close()

    return out


def create_graph(db, days, graph_name):
    """
    Creates a graph that shows the usage of the bot during the past 30 days

    :param days: The number of the days that the graph should show.
    :type days: int.
    :returns: str -- name of the output image of the graph
    """
    fig, ax = plt.subplots()

    for axis in [ax.xaxis, ax.yaxis]:
        axis.set_major_locator(ticker.MaxNLocator(integer=True))

    daily_users_data = db.get_daily_users(days)
    days = np.arange(0, -days, -1)

    plt.plot(days, daily_users_data, marker='o', color='b')
    plt.fill_between(days, daily_users_data, 0, color='0.822')

    loc = ticker.MultipleLocator(base=3.0)
    ax.xaxis.set_major_locator(loc)

    plt.xlabel("Giorni del mese")
    plt.ylabel("Utilizzo di Unicam Eat")
    plt.title("Statistiche di utilizzo")
    plt.grid(True)

    plt.savefig(graph_name)
    plt.clf()


def today_weekend():
    """
    Returns today weekday in the form of a number.

    :returns: int -- The current day in an integer format.
    """
    return datetime.datetime.today().weekday()


def get_url(canteen, day):
    """
    Returns the URL of the pdf file.

    :param canteen: Name of the canteen.
    :type canteen: str.
    :param day: Day of the week.
    :type day: str.
    :returns: str -- The URL of the pdf file.
    """
    URL = "http://www.ersucam.it/wp-content/uploads/mensa/menu"
    return (URL + "/" + canteen + "/" + day + ".pdf")


def get_day(day):
    """
    Convert the day from an integer type to a string type.

    :param day: Day of the week in an integer format.
    :type day: int.
    :returns: str -- The day of the week converted.
    """
    # Days of the week but in numeric format
    days_week_int = {
        0: "Lunedì",
        1: "Martedì",
        2: "Mercoledì",
        3: "Giovedì",
        4: "Venerdì",
        5: "Sabato",
        6: "Domenica"
    }

    # Check today
    if day != "Oggi":
        return days_week_int[day]
    else:
        return days_week_int[today_weekend()]


def clean_canteen(canteen):
    """
    Convert the name of the canteen from a horrible style to the right one.

    :param canteen: The name of the canteen in a horrible style.
    :type canteen: string.
    :returns: str -- The day of the week converted.
    """

    # Available canteen in Camerino
    canteen_unicam = {
        "Avack": "D'Avack",
        "ColleParadiso": "Colle Paradiso"
    }

    return (canteen_unicam[canteen])


def clean_day(day):
    """
    Convert the name of the day from a horrible style to the right one.

    :param day: Day of the week in an string format.
    :type day: str.
    :returns: str -- The day of the week converted.
    """
    # Days of the week (call me genius :3)
    days_week = {
        "lunedi": "Lunedì",
        "martedi": "Martedì",
        "mercoledi": "Mercoledì",
        "giovedi": "Giovedì",
        "venerdi": "Venerdì",
        "sabato": "Sabato",
        "domenica": "Domenica"
    }

    return days_week[day]


def get_cp_keyboard(user_role=0):
    """
    Return the custom markup for the keyboard, based on the day of the week.

    :param user_role: The role of the current user.
    :type user_role: integer.
    :returns: list -- An array containing the tags to be used for the keyboard of Colle Paradiso.
    """
    # Get the day
    days_week_normal = get_day(today_weekend())

    # Check which day is today and so set the right keyboard
    if user_role > 0:
        markup_array = [["Lunedì"],
                        ["Martedì", "Mercoledì", "Giovedì"],
                        ["Venerdì", "Sabato", "Domenica"]]
    elif days_week_normal == "Lunedì":
        markup_array = [["Oggi"],
                        ["Martedì", "Mercoledì", "Giovedì"],
                        ["Venerdì", "Sabato", "Domenica"]]
    elif days_week_normal == "Martedì":
        markup_array = [["Oggi"],
                        ["Mercoledì", "Giovedì", "Venerdì"],
                        ["Sabato", "Domenica"]]
    elif days_week_normal == "Mercoledì":
        markup_array = [["Oggi"],
                        ["Giovedì", "Venerdì"],
                        ["Sabato", "Domenica"]]
    elif days_week_normal == "Giovedì":
        markup_array = [["Oggi"],
                        ["Venerdì", "Sabato", "Domenica"]]
    elif days_week_normal == "Venerdì":
        markup_array = [["Oggi"],
                        ["Sabato", "Domenica"]]
    elif days_week_normal == "Sabato":
        markup_array = [["Oggi"],
                        ["Domenica"]]
    elif days_week_normal == "Domenica":
        markup_array = [["Oggi"]]
    else:
        print(Fore.RED + "[COLLEPARADISO KEYBOARD] Nice shit bro :)")

    return markup_array


def get_da_keyboard(user_role=0):
    """
    Return the custom markup for the keyboard, based on the day of the week.

    :param user_role: The role of the current user.
    :type user_role: integer.
    :returns: list -- An array containing the tags to be used for the keyboard of D'Avack.
    """
    # Get the day
    days_week_normal = get_day(today_weekend())

    # Check which day is today and so set the right keyboard
    if user_role > 0:
        markup_array = [["Lunedì"],
                        ["Martedì", "Mercoledì", "Giovedì"]]
    elif days_week_normal == "Lunedì":
        markup_array = [["Oggi"],
                        ["Martedì", "Mercoledì", "Giovedì"]]
    elif days_week_normal == "Martedì":
        markup_array = [["Oggi"],
                        ["Mercoledì", "Giovedì"]]
    elif days_week_normal == "Mercoledì":
        markup_array = [["Oggi"],
                        ["Giovedì"]]
    elif days_week_normal == "Giovedì":
        markup_array = [["Oggi"]]
    else:
        print(Fore.RED + "[AVACK KEYBOARD] Nice shit bro :)")

    return markup_array


def get_launch_dinner_keyboard(canteen, day, user_role=0):
    """
    Return the custom markup for the keyboard, based on the lunch or dinner.

    :param user_role: The role of the current user.
    :type user_role: integer.
    :param canteen: Name of the canteen.
    :type canteen: str.
    :param day: Day of the week.
    :type day: str.
    :returns: list -- An array containing the tags to be used for the keyboard.
    """
    # Lunch or supper based on the choose of the user
    if canteen == "ColleParadiso":
        if (day != "sabato" and day != "domenica") or user_role > 0:
            markup_array = [["Pranzo"],
                            ["Cena"]]
        else:
            markup_array = [["Pranzo"]]
    elif canteen == "Avack":
        markup_array = [["Pranzo"]]
    else:
        print(Fore.RED + "[SET KEYBOARD LUNCH/DINNER] Nice shit bro :)")

    return markup_array


def delete_files_infolder(folder_dir):
    """
    Simply deletes all the file inside a folder.

    :param folder_dir: The path of the folder.
    :type folder_dir: str.
    """
    for the_file in os.listdir(folder_dir):
        the_file_path = os.path.join(folder_dir, the_file)
        try:
            if os.path.isfile(the_file_path):
                os.unlink(the_file_path)
        except Exception as e:
            print(Fore.RED + "[ERROR] Errore nella funzione delete_files_infolder: " + e)


def get_bool():
    """
    Get Boolean values stored in boolFile (see settings_dist.py).

    :returns: str -- The content of the boolFile.
    """
    with open(boolFile, 'r') as f:
        return str(f.readline().strip())


def write_bool(bool_value):
    """
    Writes the value specified into the boolFile.

    :param bool_value: A string containing the value to be written in the file.
    :type bool_value: str.
    """
    with open(boolFile, 'w') as f:
        f.writelines(bool_value)


def check_dir_files():
    """
    Checks the existance of all the directories and files
    """
    if not os.path.exists(Dirs.PDF):
        print(Fore.CYAN + "[DIRECTORY] I'm creating this folder of the PDF for you. Stupid human.")
        os.makedirs(Dirs.PDF)
    if not os.path.exists(Dirs.TXT):
        print(Fore.CYAN + "[DIRECTORY] I'm creating this folder of the Text Output for you. Stupid human.")
        os.makedirs(Dirs.TXT)
    if not os.path.exists(Dirs.BOOL):
        print(Fore.CYAN + "[DIRECTORY] I'm creating this folder of the Boolean Value for you. Stupid human.")
        os.makedirs(Dirs.BOOL)
    if not os.path.exists(Dirs.QRCODE):
        print(Fore.CYAN + "[DIRECTORY] I'm creating this folder for the QR Code for you. Stupid human.")
        os.makedirs(Dirs.QRCODE)

    if not os.path.isfile(boolFile):
        f = open(boolFile, "w")
        f.close()


def generate_qr_code(chat_id, msg, folder_dir, date, canteen, meal):
    """
    Generate the QR Code for the selected menu

    :param chat_id: A string containing the value of the chat_id.
    :type chat_id: str.
    :param msg: A string containing the menu of the day.
    :type msg: str.
    :param folder_dir: A string containing the path of the folder.
    :type folder_dir: str.
    :param date: The current date.
    :type date: str.
    :param canteen: The selected canteen.
    :type canteen: str.
    :param meal: The selected meal.
    :type meal: str.
    :returns: str -- The path of the QR Code.
    """
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=7,
        border=4,
    )
    qr.add_data(str(chat_id) + " - " + date + " - " + canteen + " - " + meal + "\n\n" + msg)
    qr.make(fit=True)

    filename = folder_dir + str(chat_id) + "_" + "QRCode.png"

    img = qr.make_image(fill_color="black", back_color="white")
    img.save(filename)

    return filename
