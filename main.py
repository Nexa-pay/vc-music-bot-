import os
import asyncio
import yt_dlp
from telethon import TelegramClient, events
from telethon.sessions import StringSession
from pytgcalls import PyTgCalls, idle
from pytgcalls.types import MediaStream          # ✅ Correct for v2.2+

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")
STRING = os.getenv("STRING")

bot = TelegramClient("bot", API_ID, API_HASH)
user = TelegramClient(StringSession(STRING), API_ID, API_HASH)
vc = PyTgCalls(user)

def download(query):
    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": "song.%(ext)s",
        "quiet": True,
        "cookiefile": "cookies.txt",              # ✅ Add this
        "extractor_args": {"youtube": {"js_runtimes": ["nodejs"]}},
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
        file, title = download(query)
        await vc.play(                           # ✅ v2.2+ uses play(), not join_group_call()
            event.chat_id,
            MediaStream(file),                   # ✅ MediaStream replaces AudioPiped
        )
        await event.reply(f"▶️ Playing: **{title}**")
    except Exception as e:
        await event.reply(f"❌ Error: {e}")

@bot.on(events.NewMessage(pattern=r"/stop"))
async def stop(event):
    try:
        await vc.leave_group_call(event.chat_id)
        await event.reply("⏹️ Stopped.")
    except Exception as e:
        await event.reply(f"❌ {e}")

async def main():
    await bot.start(bot_token=BOT_TOKEN)
    await user.start()
    await vc.start()
    print("✅ Bot Running")
    await bot.run_until_disconnected()

asyncio.run(main())
