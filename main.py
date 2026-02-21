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

    # Try multiple JioSaavn API mirrors
    apis = [
        "https://saavn.dev/api/search/songs",
        "https://jiosaavn-api-privatecvc2.vercel.app/search/songs",
    ]

    song = None
    async with httpx.AsyncClient(timeout=15) as client:
        for api in apis:
            try:
                r = await client.get(api, params={"query": query, "limit": 1})
                data = r.json()
                song = data["data"]["results"][0]
                break
            except Exception:
                continue

    if not song:
        raise Exception("All JioSaavn APIs failed")

    title = song["name"] + " - " + song["artists"]["primary"][0]["name"]
    download_url = song["downloadUrl"][-1]["url"]  # highest quality

    # Download the file directly
    async with httpx.AsyncClient(timeout=60, follow_redirects=True) as client:
        r = await client.get(download_url)
        with open("song.m4a", "wb") as f:
            f.write(r.content)

    return "song.m4a", title

@bot.on(events.NewMessage(pattern=r"/play (.+)"))
async def play(event):
    query = event.pattern_match.group(1)
    await event.reply("Searching...")
    try:
        loop = asyncio.get_event_loop()
        file, title = await loop.run_in_executor(
            None, lambda: asyncio.run(search_and_download(query))
        )
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
