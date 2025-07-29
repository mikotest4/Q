import os, time, re, uuid, asyncio
from config import Config
from helper_func.settings_manager import SettingsManager
from pyrogram.enums import ParseMode

running_jobs: dict[str, dict] = {}

progress_pattern = re.compile(r'(frame|fps|size|time|bitrate|speed)\s*=\s*(\S+)')
def parse_progress(line: str):
    items = {k: v for k, v in progress_pattern.findall(line)}
    return items or None

async def readlines(stream):
    pattern = re.compile(br'[\r\n]+')
    data = bytearray()
    while not stream.at_eof():
        parts = pattern.split(data)
        data[:] = parts.pop(-1)
        for line in parts:
            yield line
        data.extend(await stream.read(1024))

async def read_stderr(start: float, msg, proc, job_id: str):
    async for raw in readlines(proc.stderr):
        line = raw.decode(errors='ignore')
        prog = parse_progress(line)
        if not prog:
            continue
        elapsed = time.time() - start
        if round(elapsed) % 5 == 0:
            text = (
                f"🔄 <b>Processing Job</b> [<code>{job_id}</code>]\n\n"
                f"📊 <b>Progress Details:</b>\n"
                f"• Size: <code>{prog.get('size','N/A')}</code>\n"
                f"• Time: <code>{prog.get('time','N/A')}</code>\n"
                f"• Speed: <code>{prog.get('speed','N/A')}</code>\n"
                f"• Bitrate: <code>{prog.get('bitrate','N/A')}</code>"
            )
            try:
                await msg.edit(text, parse_mode=ParseMode.HTML)
            except:
                pass

async def softmux_vid(vid_filename: str, sub_filename: str, msg):
    start    = time.time()
    vid_path = os.path.join(Config.DOWNLOAD_DIR, vid_filename)
    sub_path = os.path.join(Config.DOWNLOAD_DIR, sub_filename)
    base     = os.path.splitext(vid_filename)[0]
    output   = f"{base}_soft.mkv"
    out_path = os.path.join(Config.DOWNLOAD_DIR, output)
    sub_ext  = os.path.splitext(sub_filename)[1].lstrip('.')

    proc = await asyncio.create_subprocess_exec(
        'ffmpeg', '-hide_banner',
        '-i', vid_path, '-i', sub_path,
        '-map', '1:0', '-map', '0',
        '-disposition:s:0', 'default',
        '-c:v', 'copy', '-c:a', 'copy',
        '-c:s', sub_ext,
        '-y', out_path,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )

    job_id = uuid.uuid4().hex[:8]
    reader = asyncio.create_task(read_stderr(start, msg, proc, job_id))
    waiter = asyncio.create_task(proc.wait())
    running_jobs[job_id] = {'proc': proc, 'tasks': [reader, waiter]}

    await msg.edit(
        f"🔄 <b>Soft-Mux Started</b>\n\n"
        f"🆔 Job ID: <code>{job_id}</code>\n"
        f"📝 Operation: Embedding subtitles\n"
        f"🎬 Output: <code>{output}</code>\n\n"
        f"<i>Send </i><code>/cancel {job_id}</code><i> to abort</i>",
        parse_mode=ParseMode.HTML
    )

    await asyncio.wait([reader, waiter])
    running_jobs.pop(job_id, None)

    if proc.returncode == 0:
        await msg.edit(
            f"✅ <b>Soft-Mux Completed!</b>\n\n"
            f"🆔 Job ID: <code>{job_id}</code>\n"
            f"⏱️ Duration: <code>{round(time.time()-start)}s</code>\n"
            f"📁 File: <code>{output}</code>",
            parse_mode=ParseMode.HTML
        )
        await asyncio.sleep(2)
        return output
    else:
        err = await proc.stderr.read()
        await msg.edit(
            f"❌ <b>Soft-Mux Failed!</b>\n\n"
            f"🆔 Job ID: <code>{job_id}</code>\n"
            f"🚫 Error Details:\n<pre>{err.decode(errors='ignore')[:500]}</pre>",
            parse_mode=ParseMode.HTML
        )
        return False

async def hardmux_vid(vid_filename: str, sub_filename: str, msg):
    start = time.time()
    cfg = SettingsManager.get(msg.chat.id)

    # Get encoding settings
    res = cfg.get('resolution', '1920:1080')
    fps = cfg.get('fps', 'original')
    codec = cfg.get('codec', 'libx264')
    crf = cfg.get('crf', '27')
    preset = cfg.get('preset', 'faster')
    selected_font = cfg.get('font', 'auto')

    vid_path = os.path.join(Config.DOWNLOAD_DIR, vid_filename)
    sub_path = os.path.join(Config.DOWNLOAD_DIR, sub_filename)
    
    # Build video filters
    vf = []
    
    # Subtitle filter with font handling
    if selected_font == 'auto':
        # Let FFmpeg auto-select fonts from the fonts directory
        subtitle_filter = f"subtitles={sub_path}:fontsdir={Config.FONTS_DIR}"
    else:
        # Use specific font
        font_name = os.path.splitext(selected_font)[0]
        subtitle_filter = f"subtitles={sub_path}:fontsdir={Config.FONTS_DIR}:force_style='FontName={font_name}'"
    
    vf.append(subtitle_filter)
    
    # Resolution filter
    if res != 'original': 
        vf.append(f"scale={res}")
    
    # FPS filter
    if fps != 'original': 
        vf.append(f"fps={fps}")
    
    vf_arg = ",".join(vf)

    base = os.path.splitext(vid_filename)[0]
    output = f"{base}_hard.mp4"
    out_path = os.path.join(Config.DOWNLOAD_DIR, output)

    # Build FFmpeg command
    cmd = [
        'ffmpeg', '-hide_banner',
        '-i', vid_path,
        '-vf', vf_arg,
        '-c:v', codec,
        '-preset', preset,
        '-crf', crf,
        '-map', '0:v:0', '-map', '0:a:0?',
        '-c:a', 'copy',
        '-y', out_path
    ]

    proc = await asyncio.create_subprocess_exec(
        *cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )

    job_id = uuid.uuid4().hex[:8]
    reader = asyncio.create_task(read_stderr(start, msg, proc, job_id))
    waiter = asyncio.create_task(proc.wait())
    running_jobs[job_id] = {'proc': proc, 'tasks': [reader, waiter]}

    # Font display name
    font_display = "Auto Select" if selected_font == 'auto' else os.path.splitext(selected_font)[0]

    await msg.edit(
        f"🔄 <b>Hard-Mux Started</b>\n\n"
        f"🆔 Job ID: <code>{job_id}</code>\n"
        f"📝 Operation: Burning subtitles\n"
        f"🎬 Output: <code>{output}</code>\n\n"
        f"⚙️ <b>Settings:</b>\n"
        f"• Resolution: <code>{res}</code>\n"
        f"• Codec: <code>{codec}</code>\n"
        f"• CRF: <code>{crf}</code>\n"
        f"• Font: <code>{font_display}</code>\n\n"
        f"<i>Send </i><code>/cancel {job_id}</code><i> to abort</i>",
        parse_mode=ParseMode.HTML
    )

    await asyncio.wait([reader, waiter])
    running_jobs.pop(job_id, None)

    if proc.returncode == 0:
        await msg.edit(
            f"✅ <b>Hard-Mux Completed!</b>\n\n"
            f"🆔 Job ID: <code>{job_id}</code>\n"
            f"⏱️ Duration: <code>{round(time.time()-start)}s</code>\n"
            f"📁 File: <code>{output}</code>\n"
            f"🔤 Font Used: <code>{font_display}</code>",
            parse_mode=ParseMode.HTML
        )
        await asyncio.sleep(2)
        return output
    else:
        err = await proc.stderr.read()
        await msg.edit(
            f"❌ <b>Hard-Mux Failed!</b>\n\n"
            f"🆔 Job ID: <code>{job_id}</code>\n"
            f"🚫 Error Details:\n<pre>{err.decode(errors='ignore')[:500]}</pre>",
            parse_mode=ParseMode.HTML
        )
        return False
