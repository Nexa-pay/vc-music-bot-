import os
import asyncio
import yt_dlp
from telethon import TelegramClient, events
from telethon.sessions import StringSession
from pytgcalls import PyTgCalls
from pytgcalls.types import AudioPiped, AudioParameters   # ✅ Fixed import

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
        "postprocessors": [{                          # ✅ Force convert to raw audio
            "key": "FFmpegExtractAudio",
            "preferredcodec": "mp3",
        }],
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(f"ytsearch1:{query}", download=True)["entries"][0]
        return "song.mp3", info["title"]              # ✅ Always .mp3 now

@bot.on(events.NewMessage(pattern=r"/play (.+)"))
async def play(event):
    query = event.pattern_match.group(1)
    await event.reply("⏳ Searching and downloading...")
    
    try:
        file, title = download(query)
        
        try:
            # Try joining first (if not in call yet)
            await vc.join_group_call(
                event.chat_id,
                AudioPiped(                           # ✅ Replaces InputStream(InputAudioStream(...))
                    file,
                    AudioParameters(bitrate=128000),
                ),
            )
        except Exception:
            # Already in call — just change the stream
            await vc.change_stream(
                event.chat_id,
                AudioPiped(file, AudioParameters(bitrate=128000)),
            )
        
        await event.reply(f"▶️ Playing: **{title}**")
    
    except Exception as e:
        await event.reply(f"❌ Error: {e}")

@bot.on(events.NewMessage(pattern=r"/stop"))
async def stop(event):
    try:
        await vc.leave_group_call(event.chat_id)
        await event.reply("⏹️ Stopped and left voice chat.")
    except Exception as e:
        await event.reply(f"❌ Error: {e}")

async def main():
    await bot.start(bot_token=BOT_TOKEN)
    await user.start()
    await vc.start()                                  # ✅ Must start after user.start()
    print("✅ Bot Running")
    await bot.run_until_disconnected()

asyncio.run(main())
