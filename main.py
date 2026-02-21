import asyncio
import os
import httpx
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

async def search_and_download(query):
    for f in os.listdir("."):
        if f.endswith(".mp3") or f.endswith(".m4a"):
            os.remove(f)

    async with httpx.AsyncClient(timeout=30, follow_redirects=True) as client:
        # Search Deezer public API - no auth needed
        r = await client.get(
            "https://api.deezer.com/search",
            params={"q": query, "limit": 1}
        )
        data = r.json()
        print("Deezer response:", data)

        tracks = data.get("data", [])
        if not tracks:
            raise Exception("No results found for: " + query)

        track = tracks[0]
        title = track["title"] + " - " + track["artist"]["name"]
        preview_url = track.get("preview")  # 30 second MP3 preview, always free

        if not preview_url:
            raise Exception("No preview URL in track: " + str(track))

        print("Title:", title)
        print("Preview URL:", preview_url)

        r = await client.get(preview_url, timeout=60)
        with open("song.mp3", "wb") as f:
            f.write(r.content)

    return "song.mp3", title

@bot.on(events.NewMessage(pattern=r"/play (.+)"))
async def play(event):
    query = event.pattern_match.group(1)
    await event.reply("Searching...")
    try:
        file, title = await search_and_download(query)
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
