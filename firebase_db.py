"""
Unicam Eat! - Telegram Bot (FireBase framework file)
Authors: Azzeccagarbugli (f.coppola1998@gmail.com)
         Porchetta       (clarantonio98@gmail.com)
"""
import os
import requests
import filecmp
from colorama import Fore
import xml.etree.ElementTree as ET

import datetime
from calendar import monthrange

import firebase_admin
from firebase_admin import credentials, db

from settings import MENU_URL, Dirs


class Firebase:
    def __init__(self, cert):
        """
        What a beautiful world
        """
        cred = credentials.Certificate(cert)

        try:
            firebase_admin.initialize_app(cred, {
                'databaseURL': 'https://unicam-eat.firebaseio.com'
            })
        except ValueError:
            print(Fore.RED + "[ERROR] Il Database è probabilmente già aperto in un'altra istanza, "
                  "oppure un parametro non è stato passato correttamente. Si prega di chiuderla e riprovare.")
            quit()

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

    def edit_user(self, chat_id, key, val):
        """
        Modifies a key value of a user, given his chat_id
        """
        if self.exists_user(chat_id):
            db.reference('users/' + str(chat_id)).update({
                key: val
            })
            return True
        return False

    def remove_user(self, chat_id):
        """
        Deletes a user under /users, because he deserves to be banned
        """
        if self.exists_user(chat_id):
            db.reference('users/' + str(chat_id)).delete()
            return True
        return False

    def get_user(self, chat_id):
        """
        Retrieves wanted user data, given his chat_id
        """
        return db.reference('users/' + str(chat_id)).get()

    def get_all_users_id(self):
        """
        Retrieves all the ids of the users in the db
        """
        # NOTE that we don't really need to convert to list, but it is very usefull for debug purpose
        # since like this we can sort it and have an output as we really have in the Firebase console
        users_list = list(db.reference('users/').get(shallow=True))
        users_list.sort(key=int)
        return users_list

    def get_admins(self):
        """
        Retrieves all the admin's chat_ids
        """
        return list(db.reference('users/').order_by_child('role').equal_to(5).get())

    def get_users_with_pref(self, pref, val):
        """
        Retrieves all the users with a specified setting
        """
        return list(db.reference('users/').order_by_child('preferences/' + pref).equal_to(val).get())

    def exists_user(self, chat_id):
        """
        Checks if a user is already in the db
        """
        return self.get_user(chat_id) is not None

    def update_daily_users(self, user_info):
        """
        Updates daily users list for graph information
        """
        if not self.exists_user(user_info['id']):
            self.add_user(user_info)

        now = datetime.datetime.now()

        db.reference('daily_users/' + now.strftime("%Y/%m/%d")).update({
            str(user_info['id']): True
        })

    def get_daily_users(self, days=1):
        """
        Tricky function to get the data needed for the graph.
        The data consists in a numbers' list rappresenting the users that have
        used the bot in a specific day
        """
        now = datetime.datetime.now()
        curr_year = now.strftime("%Y")
        curr_month = now.strftime("%m")

        if days < 1:
            return [0]  # Error: days is not valid
        else:
            daily_users = []
            while(22 == 22):  # Starting loop
                if curr_month == now.strftime("%m"):
                    total_days_in_month = now.day
                else:
                    total_days_in_month = monthrange(int(curr_year), int(curr_month))[1]

                # Querying Firebase
                month_ref = db.reference('daily_users/' + curr_year + "/" + curr_month + "/")
                days_in_month = month_ref.get()

                # Until when we have a month where we can retrieve data, let's go
                if days_in_month is not None:
                    for i in range(total_days_in_month, 0, -1):
                        day = str(i).zfill(2)
                        if day in days_in_month.keys():
                            daily_users.append(len(days_in_month[day]))
                        else:
                            daily_users.append(0)

                        days -= 1
                        if days == 0:
                            return daily_users

                    if int(curr_month) > 1:
                        curr_month = str(int(curr_month)-1).zfill(2)
                    else:  # Happy new year :)
                        curr_year = str(int(curr_year)-1)
                        curr_month = "12"
                else:
                    for i in range(days, 0, -1):
                        daily_users.append(0)
                    return daily_users

    def correct_title(self, title):
        """
        Checks if a given report is valid
        In case it isn't valid, this function will fix it
        """
        illegal_chrs = ['.', '$', '[', ']', '#', '/']
        markdown_chrs = ['_', '*']
        for chr in illegal_chrs:
            if chr in title:
                title = title.replace(chr, " ")
        for chr in markdown_chrs:
            if chr in title:
                title = title.replace(chr, "")
        return title

    def report_error(self, chat_id, title, text, high_priority=False):
        """
        Saves a report written by user to the db
        """
        # Current day
        now = datetime.datetime.now()

        # Fixing title to make Firebase happy
        title = self.correct_title(title)

        db.reference('reports/to_read/' + title).set({
            "chat_id": chat_id,
            "date": now.strftime("%Y-%m-%d"),  # ISO 8601
            "high_priority": high_priority,
            "text": text
        })

    def get_reports(self, new=True, old=True):
        """
        Reads all the reports written by the users
        """
        if new and not old:
            # new_reports = db.reference('reports/').order_by_child('read').equal_to(False).order_by_child('date').limit_to_first(20).get()
            new_reports = db.reference('reports/to_read/').order_by_child('date').limit_to_first(20).get()
            return new_reports

        elif old and not new:
            old_reports = db.reference('reports/already_read/').order_by_child('date').limit_to_first(20).get()
            return old_reports

        elif new and old:
            new_reports = db.reference('reports/to_read/').order_by_child('date').limit_to_first(20).get()
            old_reports = db.reference('reports/already_read/').order_by_child('date').limit_to_first(20).get()
            return (new_reports, old_reports)

        else:
            return None

    def read_report(self, title):
        # Copying msg for archive purpose
        report_to_copy = db.reference('reports/to_read/' + title).get()
        db.reference('reports/to_read/' + title).delete()
        db.reference('reports/already_read/' + title).set(report_to_copy)

    def get_reports_number(self):
        new_numb = db.reference('reports/to_read/').get()
        old_numb = db.reference('reports/already_read/').get()

        if new_numb is None:
            new_numb = 0
        else:
            new_numb = len(new_numb)

        if old_numb is None:
            old_numb = 0
        else:
            old_numb = len(old_numb)

        return (new_numb, old_numb)

    def update_menues(self):
        try:
            request = requests.get(MENU_URL)

            # Writing pdf
            filename = Dirs.TEMP + 'menu_data.xml'
            filename_old = Dirs.TEMP + 'menu_data_old.xml'
            with open(filename, 'wb') as f:
                f.write(request.content)

            # Checking the existance of an old menu
            gotta_update = False
            if not os.path.isfile(filename_old):
                gotta_update = True
            else:
                # Check if files are equal
                if not filecmp.cmp(filename, filename_old):
                    gotta_update = True
                os.unlink(filename_old)

            if gotta_update:
                tree = ET.parse(filename)
                root = tree.getroot()

                for child in root:
                    courses = [{}, {}, {}, {}, {}, {}]
                    for product in child:
                        # Getting product name
                        name = self.correct_keyname(product.attrib.get('Descrizione').capitalize())

                        # Getting prices
                        if product.attrib.get('FlagPrezzo') == 'S':
                            price = "[{} €]".format(product.attrib.get('Prezzo')[0:4])
                        else:
                            price = "[{} pt]".format(product.attrib.get('Punti'))

                        # Getting the type of the meal
                        if product.attrib.get('TipoProdotto') == 'P':    # Primi
                            index = 0
                        elif product.attrib.get('TipoProdotto') == 'S':  # Secondi
                            index = 1
                        elif product.attrib.get('TipoProdotto') == 'Z':  # Pizza e panini
                            index = 2
                        elif product.attrib.get('TipoProdotto') == 'A':  # Altro
                            index = 3
                        elif product.attrib.get('TipoProdotto') == 'E':  # Extra
                            index = 4
                        elif product.attrib.get('TipoProdotto') == 'B':  # Bevande
                            index = 5

                        courses[index][name] = price

                    # Really good suff ;)
                    data = "/" + str(child.attrib.get('Data').split('T')[0])
                    canteen_cp = True if child.attrib.get('MensaCP') == 'S' else False
                    canteen_da = True if child.attrib.get('MensaDA') == 'S' else False
                    meal = "/Pranzo" if child.attrib.get('FlagCena') == 'N' else "/Cena"

                    if canteen_cp:
                        db.reference('/menues' + data + "/Colle Paradiso" + meal).update({
                            "Primi": courses[0],
                            "Secondi": courses[1],
                            "Pizza\Panini": courses[2],
                            "Altro": courses[3],
                            "Extra": courses[4],
                            "Bevande": courses[5]
                        })
                    if canteen_da:
                        db.reference('/menues' + data + "/D'Avack" + meal).update({
                            "Primi": courses[0],
                            "Secondi": courses[1],
                            "Pizza\Panini": courses[2],
                            "Altro": courses[3],
                            "Extra": courses[4],
                            "Bevande": courses[5]
                        })

                os.rename(filename, filename_old)

                return True
        except Exception as e:
            print(e)
            return False

    def correct_keyname(self, keyname, reverse=False):
        """
        Utility function that fix the invalid characters that are not supported by Firebase
        . $ # ] [ /
        """
        invalid_chrs = [
            [".", ","],
            ["$", "€"],
            ["#", "\\\\"],
            ["[", "("],
            ["]", ")"],
            ["/", "\\"]
        ]
        if not reverse:
            keyname = keyname.replace(invalid_chrs[0][0], invalid_chrs[0][1]).replace(invalid_chrs[1][0], invalid_chrs[1][1])
            keyname = keyname.replace(invalid_chrs[2][0], invalid_chrs[2][1]).replace(invalid_chrs[3][0], invalid_chrs[3][1])
            keyname = keyname.replace(invalid_chrs[4][0], invalid_chrs[4][1]).replace(invalid_chrs[5][0], invalid_chrs[5][1])
            return keyname
        else:
            keyname = keyname.replace(invalid_chrs[0][1], invalid_chrs[0][0]).replace(invalid_chrs[1][1], invalid_chrs[1][0])
            keyname = keyname.replace(invalid_chrs[2][1], invalid_chrs[2][0]).replace(invalid_chrs[3][1], invalid_chrs[3][0])
            keyname = keyname.replace(invalid_chrs[4][1], invalid_chrs[4][0]).replace(invalid_chrs[5][1], invalid_chrs[5][0])
            return keyname

    def get_updated_menu(self, canteen, day, meal):
        per_bene = {
            "Lunedì": 0,
            "Martedì": 1,
            "Mercoledì": 2,
            "Giovedì": 3,
            "Venerdì": 4,
            "Sabato": 5,
            "Domenica": 6
        }

        tua_mozzarella = {
            "Primi": 0,
            "Secondi": 1,
            "Pizza\\Panini": 2,
            "Altro": 3,
            "Extra": 4,
            "Bevande": 5
        }

        day_data = (datetime.datetime.today() - datetime.timedelta(days=datetime.datetime.today().weekday()) + datetime.timedelta(days=per_bene[day])).strftime("%Y-%m-%d")
        menu_data = db.reference('/menues/{}/{}/{}'.format(day_data, canteen, meal)).get()

        if menu_data == None:
            return "Error"

        courses = [[], [], [], [], [], []]

        for el in menu_data:
            all_courses_in_franco = menu_data[el]
            for course in all_courses_in_franco:
                course_name = "{} _{}_".format(self.correct_keyname(course, reverse=True), menu_data[el][course])
                courses[tua_mozzarella[el]].append(course_name)

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

    def get_food_in_menu(self, food_wanted):
        """
        Obtain cotoletta to the infinity and beyond
        """
        now = datetime.datetime.now()
        today = now.strftime("%Y-%m-%d")
        query_db = db.reference('menues/').order_by_key().start_at(today).get()

        result = ""
        for day in query_db:
            canteens = query_db[day]
            for canteen in canteens:
                meals = canteens[canteen]
                for meal in meals:
                    dishes = meals[meal]
                    for dish in dishes:
                        foods = dishes[dish]
                        for food in foods:
                            if food_wanted.lower() in food.lower():  # Cotoletta found! :P
                                if result != "":
                                    result += "\n"
                                result += "Il giorno *{}* alla mensa *{}* nel menù *{}* nella tipologia *{}*".format(day, canteen, meal, dish)
        return result

    def rename_users_key(self, key_to_edit, new_key_val, start_val):
        """
        Utility function to rename a key for all the users in the db
        """
        for chat_id in self.get_all_users_id():
            db.reference('users/' + str(chat_id) + "/" + key_to_edit).delete()
            db.reference('users/' + str(chat_id)).update({new_key_val: start_val})

    def convert_users_from_txt(self, file_name, bot):
        """
        Utility function to add all the chat ids in a .txt file to the Firebase db.
        Important: it requires a Telegram bot to work properly
        Example using os:
            convert_users_from_txt(self, file_name=os.path.dirname(os.path.abspath(__file__))+"\\user_db.txt")
        """
        with open(file_name, "r") as f:
            out = f.readlines()

        for chat_id in out:
            self.add_user(bot.getChat(chat_id))
