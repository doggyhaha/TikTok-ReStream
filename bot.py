from pyrogram import Client, filters
from pyrogram.types import Message
from pytgcalls.pytgcalls import PyTgCalls
from pytgcalls.types import Update
from pytgcalls.types import StreamVideoEnded
from pytgcalls.types.input_stream import AudioVideoPiped
from pytgcalls.types.input_stream.quality import HighQualityVideo, MediumQualityVideo, LowQualityVideo
from pytgcalls.types.input_stream.quality import HighQualityAudio, MediumQualityAudio, LowQualityAudio
from pytgcalls.types.browsers import Browsers
from pytgcalls.stream_type import StreamType
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import requests
import traceback
from typing import Union

API_ID = 1234567
HASH = "1234567890abcdef1234567890abcdef"

client = Client('ubot', api_id=API_ID, api_hash=HASH)
pytgcalls = PyTgCalls(client)

tiktok_api = "http://127.0.0.1:8080/"

chats = {} #chatid: tiktok username
running = []

viddict = {
    "high": HighQualityVideo(),
    "medium": MediumQualityVideo(),
    "low": LowQualityVideo()
}

auddict = {
    "high": HighQualityAudio(),
    "medium": MediumQualityAudio(),
    "low": LowQualityAudio()
} #TODO: set this using commands


audio = "high"
video = "high"

audquality: Union[HighQualityAudio, MediumQualityAudio, LowQualityAudio] = auddict[audio]
vidquality: Union[HighQualityVideo, MediumQualityVideo, LowQualityVideo] = viddict[video]

async def get_tiktok_url(username):
    url = f"{tiktok_api}{username}"
    r = requests.get(url)
    if r.status_code == 200:
        j = r.json()
        url = j['m3u8']
        r = requests.get(url)
    return j if r.status_code == 200 and r.content else None

"""
example response
{"success": true, "m3u8": "https://pull-hls-f16-tt02.tiktokcdn.com/game/stream-3571322672690495858/index.m3u8", "stats": {"LiveRoomInfo": {"coverUrl": "https://p16-webcast.tiktokcdn.com/img/720x720/tos-maliva-avt-0068/5ddfba1287bb1f07958732880b2b4122~tplv-obj.jpeg", "liveRoomStats": {"userCount": 3038}, "liveUrl": "https://pull-hls-f16-tt02.tiktokcdn.com/game/stream-3571322672690495858/index.m3u8", "ownerInfo": {"avatarLarger": "https://p16-sign-va.tiktokcdn.com/tos-maliva-avt-0068/5ddfba1287bb1f07958732880b2b4122~c5_1080x1080.jpeg?x-expires=1677420000&x-signature=hIEzQiINy%2FYVyeI1wOnOF6ZTivE%3D", "avatarMedium": "https://p16-sign-va.tiktokcdn.com/tos-maliva-avt-0068/5ddfba1287bb1f07958732880b2b4122~c5_720x720.jpeg?x-expires=1677420000&x-signature=hbYpVzlB2aE2GTqEIVDP13NFWKY%3D", "avatarThumb": "https://p16-sign-va.tiktokcdn.com/tos-maliva-avt-0068/5ddfba1287bb1f07958732880b2b4122~c5_100x100.jpeg?x-expires=1677420000&x-signature=2X9YNCADGEbtoeRQstWkp%2FNi0%2FY%3D", "commentSetting": 0, "downloadSetting": 0, "duetSetting": 0, "ftc": false, "id": "6751467583184864261", "isADVirtual": false, "nickname": "Ninja", "openFavorite": false, "privateAccount": false, "relation": 0, "secUid": "MS4wLjABAAAAZXLncOSAXIs5qwS4nW5PJWTickp_0o-WiS8Pit1V5AWynpl1JEaaSXrcv7phd5mN", "secret": false, "signature": "Just want to make people happy. Use code NINJA on the item shop!", "stitchSetting": 0, "ttSeller": false, "uniqueId": "ninja", "verified": true}, "roomID": "7203720713600027435", "status": 2, "title": "FORTNITE FAMILY FRIDAY W/ BRO"}, "extra": {"fatal_item_ids": [], "logid": "20230224143839BBC7EC7DEA517C43B497", "now": 1677249520000}, "log_pb": {"impr_id": "20230224143839BBC7EC7DEA517C43B497"}, "statusCode": 0, "status_code": 0}}"""


async def fetch_streams():
    for chat_id, username in chats.items():
        if chat_id not in running:
            ttk = await get_tiktok_url(username)
            if ttk is None:
                return
            url = ttk['m3u8']
            stats = ttk['stats']
            #send live infos in chat
            title = stats['LiveRoomInfo']['title']
            username = stats['LiveRoomInfo']['ownerInfo']['nickname']
            unique_id = stats['LiveRoomInfo']['ownerInfo']['uniqueId']
            user_count = stats['LiveRoomInfo']['liveRoomStats']['userCount']
            signature = stats['LiveRoomInfo']['ownerInfo']['signature']
            large_avatar = stats['LiveRoomInfo']['ownerInfo']['avatarLarger']
            text = f"🔴 LIVE NOW: {title}\n👨‍💻 @{unique_id} ({username})\n\n👥 {user_count} viewers\n\n📝 {signature}"
            text += f"\n\n<a href='{large_avatar}'>&#8203;</a>"
            await client.send_message(chat_id, text)
            try:
                await pytgcalls.join_group_call(
                    chat_id,
                    AudioVideoPiped(
                        url,
                        audquality,
                        vidquality,
                        headers={
                            'User-Agent': Browsers().chrome_windows,
                        },
                    ),
                    stream_type=StreamType().pulse_stream,
                )
                running.append(chat_id)
            except:
                print(traceback.format_exc())
                await client.send_message(chat_id, 'Could not join group call')

@client.on_message(filters.command('play') & filters.user("cagavo"))
async def play(client: Client, message: Message):
    chat_id = message.chat.id
    if len(message.command) < 2:
        await client.send_message(chat_id, 'Please provide a username')
        return
    username = message.text.split(" ", 1)[1]
    chats[chat_id] = username
    await message.reply_text(f"Started listening to {username}...")
    ttk = await get_tiktok_url(username)
    if ttk is None:
        await client.send_message(chat_id, 'User\'s stream may be offline')
        return
    url = ttk['m3u8']
    stats = ttk['stats']
    title = stats['LiveRoomInfo']['title']
    username = stats['LiveRoomInfo']['ownerInfo']['nickname']
    unique_id = stats['LiveRoomInfo']['ownerInfo']['uniqueId']
    user_count = stats['LiveRoomInfo']['liveRoomStats']['userCount']
    signature = stats['LiveRoomInfo']['ownerInfo']['signature']
    large_avatar = stats['LiveRoomInfo']['ownerInfo']['avatarLarger']
    text = f"🔴 LIVE NOW: {title}\n👨‍💻 @{unique_id} ({username})\n\n👥 {user_count} viewers\n\n📝 {signature}"
    text += f"\n\n<a href='{large_avatar}'>&#8203;</a>"
    await client.send_message(chat_id, text)
    print("Playin fromg: " + url)
    try:
        await pytgcalls.join_group_call(
            chat_id,
            AudioVideoPiped(
                url,
                audquality,
                vidquality,
                headers={
                    'User-Agent': Browsers().chrome_windows,
                },
            ),
            stream_type=StreamType().pulse_stream,
        )
        running.append(chat_id)
    except:
        print(traceback.format_exc())
        await client.send_message(chat_id, 'Could not join group call')

@client.on_message(filters.command('stop') & filters.user("cagavo"))
async def stop(client: Client, message: Message):
    chat_id = message.chat.id
    try:
        await pytgcalls.leave_group_call(chat_id)
    except:
        print(traceback.format_exc())
        await client.send_message(chat_id, 'Could not leave group call')
    del chats[chat_id]
    running.remove(chat_id)
    await message.reply_text('Stopped listening')

@pytgcalls.on_stream_end()
async def my_handler(pytgclient: PyTgCalls, update: Update):
    if isinstance(update, StreamVideoEnded):
        chat_id = update.chat_id
        try:
            await pytgcalls.leave_group_call(chat_id)
            await client.send_message(chat_id, 'Stream ended')
            running.remove(chat_id)
        except:
            print(traceback.format_exc())
            await client.send_message(chat_id, 'Could not leave group call')

sched = AsyncIOScheduler()
sched.add_job(fetch_streams, 'interval', minutes=15)
sched.start()

pytgcalls.run()