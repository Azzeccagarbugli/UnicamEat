"""
Unicam Eat! - Telegram Bot (Core functions file)
Authors: Azzeccagarbugli (f.coppola1998@gmail.com)
         Porchetta       (clarantonio98@gmail.com)

Da rivedere:
- report_error
- boolean file
"""

from settings import Dirs, MENU_URL

import os
import requests
import filecmp

import time
import datetime

from colorama import Fore

from io import StringIO
import xml.etree.ElementTree as ET

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


def get_updated_menu(canteen, day, meal):
    """
    Get the updated menu parsing an xml file
    """
    request = requests.get(MENU_URL)

    # Writing pdf
    filename = os.path.dirname(os.path.abspath(__file__)) + '/Temp/menu_data.xml'
    with open(filename, 'wb') as f:
        f.write(request.content)

    per_bene = {
        "Lunedì": 0,
        "Martedì": 1,
        "Mercoledì": 2,
        "Giovedì": 3,
        "Venerdì": 4,
        "Sabato": 5,
        "Domenica": 6
    }

    tree = ET.parse(filename)
    root = tree.getroot()

    # Getting stuff ready for the query
    day_data = (datetime.datetime.today() - datetime.timedelta(days=datetime.datetime.today().weekday()) + datetime.timedelta(days=per_bene[day])).strftime("%Y-%m-%d")
    canteen_data = 'MensaCP' if canteen == "Colle Paradiso" else 'MensaDA'
    meal_data = "S" if meal == 'Cena' else "N"

    courses = [ [], [], [], [], [], [] ]

    for child in root:
        if day_data in child.attrib.get('Data').split('T')[0] and child.attrib.get(canteen_data) == "S" and child.attrib.get('FlagCena') == meal_data:
            for product in child:
                # Primi
                if product.attrib.get('TipoProdotto') == 'P':
                    courses[0].append(product.attrib.get('Descrizione'))
                # Secondi
                if product.attrib.get('TipoProdotto') == 'S':
                    courses[1].append(product.attrib.get('Descrizione'))
                # Pizza e panini
                if product.attrib.get('TipoProdotto') == 'Z':
                    courses[2].append(product.attrib.get('Descrizione'))
                # Altro
                if product.attrib.get('TipoProdotto') == 'A':
                    courses[3].append(product.attrib.get('Descrizione'))
                # Extra
                if product.attrib.get('TipoProdotto') == 'E':
                    courses[4].append(product.attrib.get('Descrizione'))
                # Bevande
                if product.attrib.get('TipoProdotto') == 'B':
                    temp = product.attrib.get('Descrizione')
                    if "The" in temp:
                        temp = temp.replace("The", "Tè")
                    courses[5].append(temp)

    if not courses[0] and not courses[1] and not courses[2] and not courses[3] and not courses[4] and not courses[5]:
        return "Error"
    else:
        # Courses names
        courses_texts = ["🍝 - *Primi:*\n", "🍖 - *Secondi:*\n", "🍕 - *Pizza/Panini:*\n", "🍰 - *Altro:*\n", "🧀 - *Extra:*\n", "🍺 - *Bevande:*\n"]

        msg_menu = "🗓 - *{}* - *{}* - *{}*\n\n".format(canteen, day, meal)
        for course_text, course in zip(courses_texts, courses):
            msg_menu += course_text
            for el in course:
                msg_menu += "• " + el + "\n"
            msg_menu += "\n"
        msg_menu += "_Il menù potrebbe subire variazioni_"

        return msg_menu


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


def get_cp_keyboard(user_role=0):
    """
    Return the custom markup for the keyboard, based on the day of the week.

    :param user_role: The role of the current user.
    :type user_role: integer.
    :returns: list -- An array containing the tags to be used for the keyboard of Colle Paradiso.
    """
    # Get the day
    days_week_normal = datetime.datetime.today().weekday()

    # Check which day is today and so set the right keyboard
    if user_role > 0:
        markup_array = [["Lunedì"],
                        ["Martedì", "Mercoledì", "Giovedì"],
                        ["Venerdì", "Sabato", "Domenica"]]
    elif days_week_normal == 0:
        markup_array = [["Oggi"],
                        ["Martedì", "Mercoledì", "Giovedì"],
                        ["Venerdì", "Sabato", "Domenica"]]
    elif days_week_normal == 1:
        markup_array = [["Oggi"],
                        ["Mercoledì", "Giovedì", "Venerdì"],
                        ["Sabato", "Domenica"]]
    elif days_week_normal == 2:
        markup_array = [["Oggi"],
                        ["Giovedì", "Venerdì"],
                        ["Sabato", "Domenica"]]
    elif days_week_normal == 3:
        markup_array = [["Oggi"],
                        ["Venerdì", "Sabato", "Domenica"]]
    elif days_week_normal == 4:
        markup_array = [["Oggi"],
                        ["Sabato", "Domenica"]]
    elif days_week_normal == 5:
        markup_array = [["Oggi"],
                        ["Domenica"]]
    elif days_week_normal == 6:
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
    days_week_normal = datetime.datetime.today().weekday()

    # Check which day is today and so set the right keyboard
    if user_role > 0:
        markup_array = [["Lunedì"],
                        ["Martedì", "Mercoledì", "Giovedì"]]
    elif days_week_normal == 0:
        markup_array = [["Oggi"],
                        ["Martedì", "Mercoledì", "Giovedì"]]
    elif days_week_normal == 1:
        markup_array = [["Oggi"],
                        ["Mercoledì", "Giovedì"]]
    elif days_week_normal == 2:
        markup_array = [["Oggi"],
                        ["Giovedì"]]
    elif days_week_normal == 3:
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
    if canteen == "Colle Paradiso":
        if (day != "Sabato" and day != "Domenica") or user_role > 0:
            markup_array = [["Pranzo"],
                            ["Cena"]]
        else:
            markup_array = [["Pranzo"]]
    elif canteen == "D'Avack":
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


def check_dir_files():
    """
    Checks the existance of all the directories and files
    """
    if not os.path.exists(Dirs.QRCODE):
        print(Fore.CYAN + "[DIRECTORY] I'm creating this folder for the QR Code for you. Stupid human.")
        os.makedirs(Dirs.QRCODE)
    if not os.path.exists(Dirs.TEMP):
        print(Fore.CYAN + "[DIRECTORY] I'm creating this folder for the Temps file for you. Stupid human.")
        os.makedirs(Dirs.TEMP)


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
