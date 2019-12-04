import os

# Your token Bot, you can get it on Telegram Bot Father
TOKEN = ''
BOT_NAME = "@UnicamEatBot"
MENU_URL = ""  # Your URL of the menu in a .xml format
FIREBASE_URL = 'https://unicam-eat.firebaseio.com'


class Dirs:
    CURRENT = os.path.dirname(os.path.abspath(__file__))
    QRCODE = CURRENT + "/QRCode/"
    TEMP = CURRENT + "/Temp/"


# Updating time in secs
updating_time = 60

# Times for the notification
notification_lunch = {12, 30}
notification_dinner = {18, 30}

# Times for updating menues
update_first = [{12, 10}, {12, 11}, {12, 12}, {12, 13}, {12, 14}, {12, 15}, {12, 16}, {12, 17}, {12, 18}, {12, 19}]
update_second = [{19, 10}, {19, 11}, {19, 12}, {19, 13}, {19, 14}, {19, 15}, {19, 16}, {19, 17}, {19, 18}, {19, 19}]
