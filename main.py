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

    async with httpx.AsyncClient(timeout=20) as client:
        # Search
        r = await client.get(
            "https://saavn.dev/api/search/songs",
            params={"query": query, "limit": 1}
        )
        data = r.json()
        print("FULL RESPONSE:", data)

        results = data.get("data", {}).get("results", [])
        if not results:
            raise Exception("No results found for: " + query)

        song = results[0]
        print("SONG KEYS:", list(song.keys()))

        title = song.get("name", query)

        # Print all possible url fields
        for key in song:
            if "url" in key.lower() or "download" in key.lower() or "media" in key.lower():
                print("URL FIELD:", key, "=", song[key])

        # Try every possible download field
        download_url = None
        if "downloadUrl" in song and song["downloadUrl"]:
            urls = song["downloadUrl"]
            print("downloadUrl field:", urls)
            if isinstance(urls, list):
                download_url = urls[-1].get("url") or urls[-1].get("link")
            elif isinstance(urls, str):
                download_url = urls

        if not download_url and "url" in song:
            download_url = song["url"]

        if not download_url:
            raise Exception("Dump: " + str(song))

        print("Downloading from:", download_url)

        # Download audio
        r = await client.get(download_url, follow_redirects=True, timeout=60)
        with open("song.m4a", "wb") as f:
            f.write(r.content)

    return "song.m4a", title

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
