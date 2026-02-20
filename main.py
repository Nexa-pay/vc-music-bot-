import os
import asyncio
import yt_dlp
from telethon import TelegramClient, events
from telethon.sessions import StringSession
from pytgcalls import PyTgCalls
from pytgcalls.types.input_stream import InputAudioStream, InputStream
from pytgcalls.types.input_stream.quality import HighQualityAudio

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")
STRING = os.getenv("STRING")

bot = TelegramClient("bot", API_ID, API_HASH).start(bot_token=BOT_TOKEN)
user = TelegramClient(StringSession(STRING), API_ID, API_HASH)
vc = PyTgCalls(user)

def download(query):
    ydl_opts = {"format": "bestaudio","outtmpl": "song.%(ext)s","quiet": True}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(f"ytsearch:{query}", download=True)["entries"][0]
        return "song.webm", info["title"]

@bot.on(events.NewMessage(pattern=r"/play (.+)"))
async def play(event):
    file, title = download(event.pattern_match.group(1))
    await vc.join_group_call(event.chat_id, InputStream(InputAudioStream(file, HighQualityAudio())))
    await event.reply(f"▶️ Playing: {title}")

async def main():
    await user.start()
    await vc.start()
    await bot.run_until_disconnected()

asyncio.run(main())
