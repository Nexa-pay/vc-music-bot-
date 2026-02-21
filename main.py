import asyncio
import os
import subprocess
import base64
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
    # Clean up old file
    for f in os.listdir("."):
        if f.endswith(".mp3"):
            os.remove(f)

    result = subprocess.run(
        ["spotdl", query, "--output", "song.mp3", "--format", "mp3"],
        capture_output=True,
        text=True
    )

    if result.returncode != 0:
        raise Exception("spotdl failed: " + result.stderr)

    # Find the downloaded file
    for f in os.listdir("."):
        if f.endswith(".mp3"):
            return f, f.replace(".mp3", "")

    raise Exception("No mp3 file found after download")

@bot.on(events.NewMessage(pattern=r"/play (.+)"))
async def play(event):
    query = event.pattern_match.group(1)
    await event.reply("Searching Spotify...")
    try:
        loop = asyncio.get_event_loop()
        file, title = await loop.run_in_executor(None, download, query)
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
