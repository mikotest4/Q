import logging, os
from config import Config
from helper_func.dbhelper import Database as Db
from plugins.muxer import queue_worker

logging.basicConfig(level=logging.DEBUG,
                    format="%(asctime)s - %(name)s - %(message)s")
logging.getLogger('pyrogram').setLevel(logging.WARNING)

db = Db().setup()
if not os.path.isdir(Config.DOWNLOAD_DIR):
    os.mkdir(Config.DOWNLOAD_DIR)

from pyrogram import Client
from pyrogram.enums import ParseMode

class QueueBot(Client):
    async def start(self):
        await super().start()
        
        # Send startup notification to admin
        try:
            # Get the first admin from ALLOWED_USERS list
            admin_id = int(Config.ALLOWED_USERS[0])
            await self.send_message(
                chat_id=admin_id,
                text="<b>𝗠𝗮𝘀𝘁𝗲𝗿 𝗕𝗼𝘁 𝗜𝘀 𝗢𝗻𝗹𝗶𝗻𝗲.</b>",
                parse_mode=ParseMode.HTML
            )
            logging.info(f"Startup notification sent to admin: {admin_id}")
        except Exception as e:
            logging.error(f"Failed to send startup notification: {e}")
        
        # launch our single background worker
        self.loop.create_task(queue_worker(self))

app = QueueBot(
    "SubtitleMuxer",
    bot_token=Config.BOT_TOKEN,
    api_id=Config.APP_ID,
    api_hash=Config.API_HASH,
    plugins=dict(root="plugins")
)

if __name__ == "__main__":
    app.run()
