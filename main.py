import asyncio
import os
import yt_dlp
from telethon import TelegramClient, events
from telethon.sessions import StringSession
from telethon.errors import FloodWaitError
from pytgcalls import PyTgCalls
from pytgcalls.types import MediaStream

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")
STRING = os.getenv("STRING")

# ✅ Decode cookies from env variable (base64 encoded)
cookies_b64 = os.getenv("COOKIES_B64")
if cookies_b64:
    import base64
    with open("cookies.txt", "wb") as f:
        f.write(base64.b64decode(cookies_b64))
    print("✅ cookies.txt written from env")
else:
    print("⚠️ No COOKIES_B64 env var found")

bot = TelegramClient("bot", API_ID, API_HASH)
user = TelegramClient(StringSession(STRING), API_ID, API_HASH)
vc = PyTgCalls(user)

def download(query):
    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": "song.%(ext)s",
        "quiet": True,
        "cookiefile": "cookies.txt" if os.path.exists("cookies.txt") else None,
        "extractor_args": {
            "youtube": {
                "player_client": ["android_vr", "android_music"],
            }
        },
        "postprocessors": [{
            "key": "FFmpegExtractAudio",
            "preferredcodec": "mp3",
        }],
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(f"ytsearch1:{query}", download=True)["entries"][0]
        return "song.mp3", info["title"]

@bot.on(events.NewMessage(pattern=r"/play (.+)"))
async def play(event):
    query = event.pattern_match.group(1)
    await event.reply("⏳ Searching...")
    try:
        loop = asyncio.get_event_loop()
        file, title = await loop.run_in_executor(None, download, query)
        await vc.play(event.chat_id, MediaStream(file))
        await event.reply(f"▶️ Playing: **{title}**")
    except Exception as e:
        await event.reply(f"❌ Error: {e}")

@bot.on(events.NewMessage(pattern=r"/stop"))
async def stop(event):
    try:
        await vc.leave_group_call(event.chat_id)
        await event.reply("⏹️ Stopped.")
