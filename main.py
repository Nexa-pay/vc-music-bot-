import os
import yt_dlp
from telethon import TelegramClient, events
from telethon.sessions import StringSession
from pytgcalls import PyTgCalls
from pytgcalls.types import MediaStream
from pytgcalls.types import AudioQuality

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")
STRING = os.getenv("STRING")

bot = TelegramClient("bot", API_ID, API_HASH)
user = TelegramClient(StringSession(STRING), API_ID, API_HASH)
vc = PyTgCalls(user)

async def main():
    await bot.start(bot_token=BOT_TOKEN)
    await user.start()
    await vc.start()
    print("Bot Running")
    await bot.run_until_disconnected()

asyncio.run(main())

def download(query):
    ydl_opts = {
        "quiet": True,
        "skip_download": True,
        "format": "bestaudio/best",
        "default_search": "ytsearch1",
        "extract_flat": True
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(query, download=False)["entries"][0]

    return f"https://www.youtube.com/watch?v={info['id']}", info["title"]
    
from pytgcalls.types import MediaStream

@bot.on(events.NewMessage(pattern=r"/play (.+)"))
async def play(event):
    url, title = download(event.pattern_match.group(1))

    await vc.play(
        event.chat_id,
        MediaStream(url)
    )

    await event.reply(f"▶️ Playing: {title}")
    
print("Bot Running")

with bot:
    user.start()
    vc.start()
    bot.run_until_disconnected()