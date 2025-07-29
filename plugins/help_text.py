# (c) mohdsabahat

#Logging
import logging
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

logger = logging.getLogger(__name__)

import os
import pyrogram
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from chat import Chat
from config import Config
logging.getLogger('pyrogram').setLevel(logging.WARNING)

async def insert(user_id):
    """Insert or update user in database - placeholder function"""
    # This function should handle user registration/tracking
    # You can implement database insertion logic here if needed
    logger.info(f"User {user_id} accessed the bot")
    pass

@Client.on_message(filters.command("start") & filters.private)
async def strtCap(bot, message):
    user_id = int(message.from_user.id)
    await insert(user_id)

    # Get bot info to access username
    bot_info = await bot.get_me()
    bot_username = bot_info.username

    keyboard = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("ʏ", url="https://t.me/Yae_X_Miko"),
                InlineKeyboardButton("ᴀ", url="https://t.me/Yae_X_Miko"),
                InlineKeyboardButton("ᴇ", url="https://t.me/Yae_X_Miko"),
                InlineKeyboardButton("ᴍ", url="https://t.me/Yae_X_Miko"),
                InlineKeyboardButton("ɪ", url="https://t.me/Yae_X_Miko"),
                InlineKeyboardButton("ᴋ", url="https://t.me/Yae_X_Miko"),
                InlineKeyboardButton("ᴏ", url="https://t.me/Yae_X_Miko")
            ],
            [
                InlineKeyboardButton("𝗧𝗮𝗸𝗲 𝗔𝗰𝗰𝗲𝘀𝘀", url="https://t.me/Yae_X_Miko")
            ]
        ]
    )

    await message.reply_photo(
        photo=Config.YAE_MIKO_PIC,
        caption=f"<b>Hᴇʟʟᴏ {message.from_user.mention}\n\nɪ ᴀᴍ sᴜʙᴛɪᴛʟᴇ ᴍɪxᴇʀ ʙᴏᴛ ᴡɪᴛʜ ᴄᴜsᴛᴏᴍ sᴜʙᴛɪᴛʟᴇ.</b>\n<b>ɪғ ʏᴏᴜ ᴡᴀɴᴛ ᴛᴏ ᴜsᴇ ʙᴏᴛ ᴛʜᴀɴ ᴛᴀᴋᴇ ᴀᴄᴄᴇss</b>",
        reply_markup=keyboard
    )

@pyrogram.Client.on_message(pyrogram.filters.command(['help']))
async def help_user(bot, update):

    if str(update.from_user.id) in Config.ALLOWED_USERS:
        await bot.send_message(
            update.chat.id,
            Chat.HELP_TEXT,
            reply_to_message_id = update.id
        )

    else:

        await bot.send_message(
            update.chat.id,
            Chat.NO_AUTH_USER,
            reply_to_message_id = update.id
        )
