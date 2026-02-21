import asyncio
import os
import httpx
from pyrogram import Client, filters
from pytgcalls import PyTgCalls
from pytgcalls.types import MediaStream

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")
STRING = os.getenv("STRING"))

bot = Client("bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)
user = Client("user", api_id=API_ID, api_hash=API_HASH, session_string=STRING)
vc = PyTgCalls(user)

def download(query):
    for f in os.listdir("."):
        if f.endswith(".mp3") or f.endswith(".m4a"):
            os.remove(f)

    with httpx.Client(timeout=30, follow_redirects=True) as client:
        r = client.get(
            "https://api.deezer.com/search",
            params={"q": query, "limit": 1}
        )
        data = r.json()
        tracks = data.get("data", [])
        if not tracks:
            raise Exception("No results found for: " + query)

        track = tracks[0]
        title = track["title"] + " - " + track["artist"]["name"]
        preview_url = track.get("preview")

        if not preview_url:
            raise Exception("No preview URL found")

        r = client.get(preview_url, timeout=60)
        with open("song.mp3", "wb") as f:
            f.write(r.content)

    return "song.mp3", title

@bot.on_message(filters.command("play"))
async def play(client, message):
    query = " ".join(message.command[1:])
    if not query:
        await message.reply("Usage: /play song name")
        return
    await message.reply("Searching...")
    try:
        loop = asyncio.get_event_loop()
        file, title = await loop.run_in_executor(None, download, query)
        await vc.play(message.chat.id, MediaStream(file))
        await message.reply("Playing: " + title)
    except Exception as e:
        await message.reply("Error: " + str(e))

@bot.on_message(filters.command("stop"))
async def stop(client, message):
    try:
        await vc.leave_group_call(message.chat.id)
        await message.reply("Stopped.")
    except Exception as e:
        await message.reply("Error: " + str(e))

async def main():
    await bot.start()
    await user.start()
    await vc.start()
    print("Bot Running")
    await asyncio.gather(bot.idle())

asyncio.run(main())
