
import os

class Config:

    BOT_TOKEN = "7819249411:AAHBwacCoXZl71xq8yF1bkqgxqzTkoFPCYA"
    APP_ID = 27999679
    API_HASH = "f553398ca957b9c92bcb672b05557038"

    #comma seperated user id of users who are allowed to use
    ALLOWED_USERS = [x.strip(' ') for x in os.environ.get('ALLOWED_USERS','7970350353').split(',')]
 # Absolute path to the folder where you keep your .ttf/.otf files
    FONTS_DIR = os.path.join(os.getcwd(), "fonts")
    
    DOWNLOAD_DIR = 'downloads'
