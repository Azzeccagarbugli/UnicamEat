import os

# Your token Bot, you can get it on Telegram Bot Father
TOKEN = ''
BOT_NAME = "@UnicamEatBot"

# Dictionaries
courses_dictionaries = [
    ["past", "zupp", "passat", "tagliatell", "riso", "chicche", "minestron", "penn", "chitarr", "tortellin", "prim", "raviol", "maccheroncin"],
    ["panin", "pizz", "crostin", "piadin", "focacci"],
    ["frutt", "yogurt", "contorn", "dolc", "pan", "sals"],
    ["porzionat", "formaggi", "olio", "confettur", "cioccolat", "asport"],
    ["lattin", "brick", "acqua"]
]


class Dirs:
    CURRENT = os.path.dirname(os.path.abspath(__file__))
    PDF = CURRENT + "/PDF/"
    TXT = CURRENT + "/Text/"
    BOOL = CURRENT + "/Boolean/"
    LOG = CURRENT + "/Log/"
    QRCODE = CURRENT + "/QRCode/"


# Bool file
boolFile = Dirs.BOOL + "update_menu.txt"

# Times for the notification
notification_lunch = {12, 30}
notification_dinner = {18, 30}
