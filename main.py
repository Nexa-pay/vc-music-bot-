import asyncio
import os
import base64
import httpx
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

async def search_jiosaavn(query):
    url = "https://saavn.dev/api/search/songs"
    async with httpx.AsyncClient() as client:
        r = await client.get(url, params={"query": query, "limit": 1})
        data = r.json()
        song = data["data"]["results"][0]
        title = song["name"] + " - " + song["artists"]["primary"][0]["name"]
        # Get highest quality download URL
        download_url = song["downloadUrl"][-1]["url"]
        return title, download_url

def download_direct(url, title):
    for f in os.listdir("."):
        if f.endswith(".mp3"):
            os.remove(f)

    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": "song.%(ext)s",
        "quiet": True,
        "postprocessors": [{
            "key": "FFmpegExtractAudio",
            "preferredcodec": "mp3",
        }],
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])
    return "song.mp3"

@bot.on(events.NewMessage(pattern=r"/play (.+)"))
async def play(event):
    query = event.pattern_match.group(1)
    await event.reply("Searching JioSaavn...")
    try:
        title, url = await search_jiosaavn(query)
        loop = asyncio.get_event_loop()
        file = await loop.run_in_executor(None, download_direct, url, title)
        await vc.play(event.chat_id, MediaStream(file))
        await event.reply("Playing: " + title)
    except Exception as e:
        await event.reply("Error: " + str(e))

@bot.on(events.NewMessage(pattern=r"/stop"))
async def stop(event):
    try:
        await vc.leave_group_call(event.chat_id)
        await event.reply("Stopped.")
    except Exception as e:
        await event.reply("Error: " + str(e))

async def main():
    while True:
        try:
            await bot.start(bot_token=BOT_TOKEN)
            break
        except FloodWaitError as e:
            print("FloodWait: waiting " + str(e.seconds) + "s...")
            await asyncio.sleep(e.seconds + 5)

    await user.start()
    await vc.start()
    print("Bot Running")
    await bot.run_until_disconnected()

asyncio.run(main())
