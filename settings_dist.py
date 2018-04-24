import os

# Your token Bot, you can get it on Telegram Bot Father
TOKEN = ''
BOT_NAME = "@UnicamEatBot"
MENU_URL = ""  # Your URL of the menu in a .xml format


class Dirs:
    CURRENT = os.path.dirname(os.path.abspath(__file__))
    QRCODE = CURRENT + "/QRCode/"
    TEMP = CURRENT + "/Temp/"


# Updating time in secs
updating_time = 60

# Times for the notification
notification_lunch = {12, 30}
notification_dinner = {18, 30}
