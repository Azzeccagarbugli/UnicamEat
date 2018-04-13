"""
Unicam Eat! - Telegram Bot (FireBase framework file)
Authors: Azzeccagarbugli (f.coppola1998@gmail.com)
         Porchetta       (clarantonio98@gmail.com)
"""
import firebase_admin
from firebase_admin import credentials, db

from colorama import Fore

import datetime
from calendar import monthrange


class Firebase:
    def __init__(self, cert):
        self.cert = cert

    def initialize_sdk(self):
        """
        Initialize the Firebase Admin SDK
        """
        cred = credentials.Certificate(self.cert)

        try:
            firebase_admin.initialize_app(cred, {
                'databaseURL': 'https://unicam-eat.firebaseio.com'
            })
        except ValueError:
            print(Fore.RED + "[ERROR] Il Database è probabilmente già aperto in un'altra istanza, "
                  "oppure un parametro non è stato passato correttamente. Si prega di chiuderla e riprovare.")
            quit()

    def add_user(self, chat_id, user_info):
        """
        Adds a new user under /users
        """
        if not self.exists_user(chat_id):
            # Trying to get full name
            if 'first_name' in user_info and 'last_name' in user_info:
                name = user_info['first_name'] + " " + user_info['last_name']
            elif 'first_name' in user_info:
                name = user_info['first_name']
            elif 'last_name' in user_info:
                name = user_info['last_name']
            else:
                name = "Not Defined"

            # Trying to get username
            if 'username' in user_info:
                username = user_info['username']
            else:
                username = "Not Defined"

            db.reference('users/' + str(chat_id)).set({
                "info": {
                    "name": name,
                    "username": username
                },
                "preferences": {
                    "language": "IT",
                    "notif_cp_d": True,
                    "notif_cp_l": True,
                    "notif_da": True
                },
                "role": 0
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
        # NOTE that we don't really need to convert to list, but it is very userful for debug purpose
        # since like this we can sort it and have an output as we really have in the firebase console
        users_list = list(db.reference('users/').get(shallow=True))
        users_list.sort(key=int)
        return users_list

    def get_admins(self):
        """
        Retrieves all the admin's chat_ids
        """
        return list(db.reference('users/').order_by_child('role').equal_to(1).get())

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

    def update_daily_users(self, chat_id):
        """
        Updates the 22 to make sure that we always have the 22 in our hearts
        """
        now = datetime.datetime.now()
        try:
            db.reference('daily_users/' + now.strftime("%Y/%m/%d")).get()[chat_id]
            return False
        except (KeyError, TypeError) as e:
            db.reference('daily_users/' + now.strftime("%Y/%m/%d")).update({
                str(chat_id): True
            })
            return True

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
            self.add_user(chat_id.rstrip(), bot.getChat(chat_id))
