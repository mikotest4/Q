import os

class Config:

    BOT_TOKEN = "7819249411:AAHBwacCoXZl71xq8yF1bkqgxqzTkoFPCYA"
    APP_ID = 27999679
    API_HASH = "f553398ca957b9c92bcb672b05557038"

    # comma separated user id of users who are allowed to use
    ALLOWED_USERS = [x.strip(' ') for x in os.environ.get('ALLOWED_USERS','7970350353').split(',')]
    
    # Absolute path to the folder where you keep your .ttf/.otf files
    FONTS_DIR = os.path.join(os.getcwd(), "fonts")
    
    DOWNLOAD_DIR = 'downloads'
    
    # MongoDB Configuration
    DB_URI = os.environ.get("DATABASE_URL", "mongodb+srv://Koi:aloksingh@cluster0.86wo9.mongodb.net/?retryWrites=true&w=majority")
    DB_NAME = os.environ.get("DATABASE_NAME", "Koi")
    
    # Yae Miko Picture URL
    YAE_MIKO_PIC = "https://telegra.ph/file/8c3d010a3456bb919767d-8a0c8cf2056766c5ee.jpg"
