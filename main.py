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

bot = TelegramClient("bot", API_ID, API_HASH).start(bot_token=BOT_TOKEN)
user = TelegramClient(StringSession(STRING), API_ID, API_HASH)

vc = PyTgCalls(user)

def download(query):
    ydl_opts = {
        "format": "bestaudio",
        "quiet": True,
        "extractor_args": {
            "youtube": {
                "player_client": ["android"],
                "player_skip": ["webpage", "configs"]
            }
        }
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(f"ytsearch1:{query}", download=False)["entries"][0]
        return info["url"], info["title"]

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