# plugins/fonts.py

import os
from pyrogram import Client, filters
from pyrogram.enums import ParseMode
from helper_func.settings_manager import SettingsManager
from config import Config

# User authorization check
async def _check_user(filt, client, message):
    return str(message.from_user.id) in Config.ALLOWED_USERS
check_user = filters.create(_check_user)

def get_available_fonts():
    """Get list of available font files."""
    if not os.path.exists(Config.FONTS_DIR):
        return []
    return [f for f in os.listdir(Config.FONTS_DIR) if f.endswith(('.ttf', '.otf'))]

@Client.on_message(filters.command("fonts") & check_user & filters.private)
async def list_fonts(client, message):
    """Show all available fonts."""
    fonts = get_available_fonts()
    
    if not fonts:
        await message.reply(
            "❌ <b>No Custom Fonts Found!</b>\n\n"
            "Please add font files (.ttf or .otf) to the fonts directory.",
            parse_mode=ParseMode.HTML
        )
        return
    
    font_list = []
    current_font = SettingsManager.get(message.from_user.id).get('font', 'auto')
    
    for i, font in enumerate(fonts, 1):
        font_name = os.path.splitext(font)[0]
        status = " ✅" if font == current_font else ""
        font_list.append(f"{i}. <code>{font_name}</code>{status}")
    
    current_display = "Auto Select" if current_font == 'auto' else os.path.splitext(current_font)[0]
    
    text = (
        f"🔤 <b>Available Fonts ({len(fonts)})</b>\n"
        f"📌 <b>Current Font:</b> <code>{current_display}</code>\n\n"
        + "\n".join(font_list) +
        "\n\n<i>Use quick commands below to switch fonts:</i>"
    )
    
    await message.reply(text, parse_mode=ParseMode.HTML)

@Client.on_message(filters.command("font_auto") & check_user & filters.private)
async def set_auto_font(client, message):
    """Set font to auto-select mode."""
    uid = message.from_user.id
    SettingsManager.set(uid, 'font', 'auto')
    await message.reply(
        "✅ <b>Font Updated!</b>\n\n"
        "🔤 Current Font: <code>Auto Select</code>\n"
        "<i>FFmpeg will automatically choose the best font for your subtitles.</i>",
        parse_mode=ParseMode.HTML
    )

@Client.on_message(filters.command("font_ybx") & check_user & filters.private)
async def set_ybx_font(client, message):
    """Set YBX TOP font."""
    uid = message.from_user.id
    font_file = "YBX TOP.ttf"
    
    if not os.path.exists(os.path.join(Config.FONTS_DIR, font_file)):
        await message.reply(
            f"❌ <b>Font Not Found!</b>\n\n"
            f"The font <code>{font_file}</code> is not available.\n"
            f"Please check your fonts directory.",
            parse_mode=ParseMode.HTML
        )
        return
    
    SettingsManager.set(uid, 'font', font_file)
    await message.reply(
        "✅ <b>Font Updated!</b>\n\n"
        "🔤 Current Font: <code>YBX TOP</code>\n"
        "<i>This font will be used for your next hard-mux operation.</i>",
        parse_mode=ParseMode.HTML
    )

@Client.on_message(filters.command("font_rapier") & check_user & filters.private)
async def set_rapier_font(client, message):
    """Set Rapier Zero font."""
    uid = message.from_user.id
    font_file = "Rapier Zero.otf"
    
    if not os.path.exists(os.path.join(Config.FONTS_DIR, font_file)):
        await message.reply(
            f"❌ <b>Font Not Found!</b>\n\n"
            f"The font <code>{font_file}</code> is not available.\n"
            f"Please check your fonts directory.",
            parse_mode=ParseMode.HTML
        )
        return
    
    SettingsManager.set(uid, 'font', font_file)
    await message.reply(
        "✅ <b>Font Updated!</b>\n\n"
        "🔤 Current Font: <code>Rapier Zero</code>\n"
        "<i>This font will be used for your next hard-mux operation.</i>",
        parse_mode=ParseMode.HTML
    )

@Client.on_message(filters.command("font_komix") & check_user & filters.private)
async def set_komix_font(client, message):
    """Set Komix font."""
    uid = message.from_user.id
    font_file = "Komix.ttf"
    
    if not os.path.exists(os.path.join(Config.FONTS_DIR, font_file)):
        await message.reply(
            f"❌ <b>Font Not Found!</b>\n\n"
            f"The font <code>{font_file}</code> is not available.\n"
            f"Please check your fonts directory.",
            parse_mode=ParseMode.HTML
        )
        return
    
    SettingsManager.set(uid, 'font', font_file)
    await message.reply(
        "✅ <b>Font Updated!</b>\n\n"
        "🔤 Current Font: <code>Komix</code>\n"
        "<i>This font will be used for your next hard-mux operation.</i>",
        parse_mode=ParseMode.HTML
    )

@Client.on_message(filters.command("font_set") & check_user & filters.private)
async def set_custom_font(client, message):
    """Set font by filename - /font_set filename.ttf"""
    uid = message.from_user.id
    
    if len(message.command) != 2:
        fonts = get_available_fonts()
        font_list = "\n".join([f"• <code>{f}</code>" for f in fonts]) if fonts else "No fonts available"
        
        await message.reply(
            "<b>📝 Usage:</b> <code>/font_set filename.ttf</code>\n\n"
            f"<b>🔤 Available Fonts:</b>\n{font_list}",
            parse_mode=ParseMode.HTML
        )
        return
    
    font_file = message.command[1]
    font_path = os.path.join(Config.FONTS_DIR, font_file)
    
    if not os.path.exists(font_path):
        await message.reply(
            f"❌ <b>Font Not Found!</b>\n\n"
            f"The font <code>{font_file}</code> doesn't exist in the fonts directory.\n"
            f"Use <code>/fonts</code> to see available fonts.",
            parse_mode=ParseMode.HTML
        )
        return
    
    SettingsManager.set(uid, 'font', font_file)
    font_name = os.path.splitext(font_file)[0]
    
    await message.reply(
        f"✅ <b>Font Updated!</b>\n\n"
        f"🔤 Current Font: <code>{font_name}</code>\n"
        f"<i>This font will be used for your next hard-mux operation.</i>",
        parse_mode=ParseMode.HTML
    )
