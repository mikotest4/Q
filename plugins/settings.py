# plugins/settings.py

from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.enums import ParseMode
from helper_func.settings_manager import SettingsManager
import os
from config import Config

# in‑memory state for who's currently in settings
_PENDING = {}

# Option lists
RESOLUTIONS = [
    ('8K','7680:4320'),('4K','3840:2160'),
    ('1440p','2560:1440'),('1080p','1920:1080'),
    ('720p','1280:720'),('480p','854:480'),
    ('360p','640:360'),('240p','426:240'),
    ('144p','256:144'),('original','original'),
]
FPS_OPTIONS = [
    ('60 FPS','60'),('50 FPS','50'),
    ('30 FPS','30'),('25 FPS','25'),
    ('24 FPS','24'),('original','original'),
]
CODECS = [
    ('H.264','libx264'),('H.265','libx265'),
    ('VP9','libvpx-vp9'),('AV1','libaom-av1'),
]
PRESETS = [
    ('ultrafast','ultrafast'),('superfast','superfast'),
    ('veryfast','veryfast'),('faster','faster'),
    ('fast','fast'),('medium','medium'),
    ('slow','slow'),('slower','slower'),
    ('veryslow','veryslow'),
]

# Font options - dynamically loaded from fonts directory
def get_font_options():
    """Get available fonts from the fonts directory."""
    font_options = [('Auto Select', 'auto')]
    
    if os.path.exists(Config.FONTS_DIR):
        font_files = [f for f in os.listdir(Config.FONTS_DIR) if f.endswith(('.ttf', '.otf'))]
        for font_file in sorted(font_files):
            font_name = os.path.splitext(font_file)[0]
            font_options.append((font_name, font_file))
    
    return font_options

def _keyboard(options: list, tag: str) -> InlineKeyboardMarkup:
    """Build inline keyboard rows of one button each."""
    return InlineKeyboardMarkup(
        [[InlineKeyboardButton(n, callback_data=f"{tag}*{v}")]
         for n, v in options]
    )

@Client.on_message(filters.command("settings") & filters.private)
async def start_settings(client: Client, message):
    """Entry point: choose resolution."""
    uid = message.from_user.id
    _PENDING[uid] = 'res'
    await message.reply(
        "<b>🔧 Settings Configuration</b>\n<b>Step 1/6:</b> Choose your target resolution:",
        reply_markup=_keyboard(RESOLUTIONS, 'res'),
        parse_mode=ParseMode.HTML
    )

@Client.on_callback_query()
async def handle_settings_cb(client: Client, cq):
    """Handle each button press."""
    uid = cq.from_user.id
    stage = _PENDING.get(uid)
    if not stage:
        return  # not in settings flow

    action, val = cq.data.split('*', 1)
    await cq.answer()

    if action == 'res':
        SettingsManager.set(uid, 'resolution', val)
        _PENDING[uid] = 'fps'
        await cq.edit_message_text(
            "<b>🔧 Settings Configuration</b>\n<b>Step 2/6:</b> Choose your target frame rate:",
            reply_markup=_keyboard(FPS_OPTIONS, 'fps'),
            parse_mode=ParseMode.HTML
        )

    elif action == 'fps':
        SettingsManager.set(uid, 'fps', val)
        _PENDING[uid] = 'codec'
        await cq.edit_message_text(
            "<b>🔧 Settings Configuration</b>\n<b>Step 3/6:</b> Choose your video codec:",
            reply_markup=_keyboard(CODECS, 'codec'),
            parse_mode=ParseMode.HTML
        )

    elif action == 'codec':
        SettingsManager.set(uid, 'codec', val)
        _PENDING[uid] = 'crf'
        await cq.edit_message_text(
            "<b>🔧 Settings Configuration</b>\n<b>Step 4/6:</b> Send me a CRF value (0–51):\n\n"
            "<i>💡 Lower values = better quality, larger file size\n"
            "📌 Recommended: 18-28</i>",
            parse_mode=ParseMode.HTML
        )

    elif action == 'preset':
        SettingsManager.set(uid, 'preset', val)
        _PENDING[uid] = 'font'
        font_options = get_font_options()
        await cq.edit_message_text(
            "<b>🔧 Settings Configuration</b>\n<b>Step 6/6:</b> Choose your subtitle font:",
            reply_markup=_keyboard(font_options, 'font'),
            parse_mode=ParseMode.HTML
        )

    elif action == 'font':
        SettingsManager.set(uid, 'font', val)
        cfg = SettingsManager.get(uid)
        
        font_display = cfg.get('font', 'auto')
        if font_display != 'auto':
            font_display = os.path.splitext(font_display)[0]
        
        summary = (
            "<b>✅ Settings Saved Successfully!</b>\n\n"
            f"🎬 <b>Video Settings:</b>\n"
            f"• Resolution: <code>{cfg.get('resolution', 'original')}</code>\n"
            f"• Frame Rate: <code>{cfg.get('fps', 'original')}</code>\n"
            f"• Codec: <code>{cfg.get('codec', 'libx264')}</code>\n"
            f"• CRF Quality: <code>{cfg.get('crf', '27')}</code>\n"
            f"• Preset: <code>{cfg.get('preset', 'faster')}</code>\n\n"
            f"🔤 <b>Subtitle Settings:</b>\n"
            f"• Font: <code>{font_display}</code>\n\n"
            f"<i>These settings will be used for all your hard-mux operations!</i>"
        )
        _PENDING.pop(uid, None)
        await cq.edit_message_text(summary, parse_mode=ParseMode.HTML)

@Client.on_message(filters.text & filters.private)
async def handle_crf_text(client: Client, message):
    """Catch CRF numeric entry."""
    uid = message.from_user.id
    if _PENDING.get(uid) != 'crf':
        return

    txt = message.text.strip()
    if not txt.isdigit() or not (0 <= int(txt) <= 51):
        return await message.reply(
            "❌ <b>Invalid CRF Value!</b>\n\n"
            "Please enter a number between <b>0</b> and <b>51</b>.\n\n"
            "<i>💡 Tip: Use 18-28 for best balance of quality and file size.</i>",
            parse_mode=ParseMode.HTML
        )

    SettingsManager.set(uid, 'crf', txt)
    _PENDING[uid] = 'preset'
    await message.reply(
        "<b>🔧 Settings Configuration</b>\n<b>Step 5/6:</b> Choose your encoding preset:\n\n"
        "<i>💡 Faster presets = quicker encoding but larger files\n"
        "📌 Recommended: fast or medium</i>",
        reply_markup=_keyboard(PRESETS, 'preset'),
        parse_mode=ParseMode.HTML
    )
