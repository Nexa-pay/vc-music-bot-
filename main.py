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

bot = TelegramClient("bot", API_ID, API_HASH)
user = TelegramClient(StringSession(STRING), API_ID, API_HASH)
vc = PyTgCalls(user)

def download(query):
    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": "song.%(ext)s",
        "quiet": True,
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
    except Exception as e:
        await event.reply(f"❌ {e}")

async def main():
    # ✅ Handle flood wait on startup instead of crashing
    while True:
        try:
            await bot.start(bot_token=BOT_TOKEN)
            break
        except FloodWaitError as e:
            print(f"⏳ FloodWait: sleeping {e.seconds} seconds...")
            await asyncio.sleep(e.seconds)

    await user.start()
    await vc.start()
    print("✅ Bot Running")
    await bot.run_until_disconnected()

asyncio.run(main())
