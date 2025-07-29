# (c) mohdsabahat

#Logging
import logging
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

logger = logging.getLogger(__name__)

import os
import pyrogram
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
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
                InlineKeyboardButton("𝗧𝗮𝗸𝗲 𝗔𝗰𝗰𝗲𝘀𝘀", url="https://t.me/Yae_X_Miko"),
                InlineKeyboardButton("𝗛𝗲𝗹𝗽", callback_data="help_menu")
            ]
        ]
    )

    await message.reply_photo(
        photo=Config.YAE_MIKO_PIC,
        caption=f"<b>Hᴇʟʟᴏ {message.from_user.mention}\n\nɪ ᴀᴍ sᴜʙᴛɪᴛʟᴇ ᴍɪxᴇʀ ʙᴏᴛ ᴡɪᴛʜ ᴄᴜsᴛᴏᴍ sᴜʙᴛɪᴛʟᴇ.</b>\n<b>ɪғ ʏᴏᴜ ᴡᴀɴᴛ ᴛᴏ ᴜsᴇ ʙᴏᴛ ᴛʜᴀɴ ᴛᴀᴋᴇ ᴀᴄᴄᴇss</b>",
        reply_markup=keyboard
    )

@Client.on_callback_query(filters.regex("help_menu"))
async def help_callback(bot, callback_query: CallbackQuery):
    help_text = """<b>𝗪𝗲𝗹𝗰𝗼𝗺𝗲 𝗧𝗼 𝗧𝗵𝗲 𝗛𝗲𝗹𝗽 𝗠𝗲𝗻𝘂.</b>

<b>𝗛𝗼𝘄 𝗧𝗼 𝗨𝘀𝗲 𝗧𝗵𝗶𝘀 𝗕𝗼𝘁.</b>
<b>1</b> : sᴇɴᴅ ᴀ ᴠɪᴅᴇᴏ ғɪʟᴇ {ғɪʟᴇ sʜᴏᴜʟᴅ ʙᴇ ɪɴ .ᴍᴋᴠ ᴏʀ .ᴍᴘ4}.
<b>2</b> : sᴇɴᴅ ᴀ sᴜʙᴛɪᴛʟᴇ ғɪʟᴇ. {ғɪʟᴇ sʜᴏᴜʟᴅ ʙᴇ ɪɴ .ᴀss ᴏʀ .sʀᴛ}.
<b>3</b> : ᴄʜᴏᴏsᴇ ʏᴏᴜʀ ᴅᴇsɪʀᴇᴅ ᴛʏᴘᴇ ᴏғ ᴍᴜxɪɴɢʜ {sᴏғᴛᴍᴜx ᴏʀ ʜᴀʀᴅᴍᴜx}."""

    help_keyboard = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("𝐁𝐚𝐜𝐤", callback_data="back_to_start"),
                InlineKeyboardButton("𝐂𝐥𝐨𝐬𝐞", callback_data="close_menu")
            ]
        ]
    )

    await callback_query.edit_message_media(
        media=pyrogram.types.InputMediaPhoto(
            media=Config.HELP_PIC,
            caption=help_text
        ),
        reply_markup=help_keyboard
    )
    
    await callback_query.answer()

@Client.on_callback_query(filters.regex("back_to_start"))
async def back_to_start(bot, callback_query: CallbackQuery):
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
                InlineKeyboardButton("𝗧𝗮𝗸𝗲 𝗔𝗰𝗰𝗲𝘀𝘀", url="https://t.me/Yae_X_Miko"),
                InlineKeyboardButton("𝗛𝗲𝗹𝗽", callback_data="help_menu")
            ]
        ]
    )

    await callback_query.edit_message_media(
        media=pyrogram.types.InputMediaPhoto(
            media=Config.YAE_MIKO_PIC,
            caption=f"<b>Hᴇʟʟᴏ {callback_query.from_user.mention}\n\nɪ ᴀᴍ sᴜʙᴛɪᴛʟᴇ ᴍɪxᴇʀ ʙᴏᴛ ᴡɪᴛʜ ᴄᴜsᴛᴏᴍ sᴜʙᴛɪᴛʟᴇ.</b>\n<b>ɪғ ʏᴏᴜ ᴡᴀɴᴛ ᴛᴏ ᴜsᴇ ʙᴏᴛ ᴛʜᴀɴ ᴛᴀᴋᴇ ᴀᴄᴄᴇss</b>"
        ),
        reply_markup=keyboard
    )
    
    await callback_query.answer()

@Client.on_callback_query(filters.regex("close_menu"))
async def close_menu(bot, callback_query: CallbackQuery):
    await callback_query.message.delete()
    await callback_query.answer()

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
