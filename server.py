import re, aiohttp
from aiohttp import web
from aiohttp.web import Request

async def get_m3u8(username):
    username = f"@{username}" if not username.startswith("@") else username
    url = f"https://www.tiktok.com/{username}/live"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
           body = await resp.text()
           print(resp.status)
        body = body.lower()
    matches = re.findall(r"room_id=(\d+)", body)
    if not matches:
        matches = re.findall(r"roomid=(\d+)", body)
        if not matches:
            return None, None
    roomId = matches[1]
    apiURL = f"https://www.tiktok.com/api/live/detail/?aid=1988&roomID={roomId}"
    async with aiohttp.ClientSession() as session:
        async with session.get(apiURL) as resp:
            res = await resp.json()
    return res["LiveRoomInfo"]["liveUrl"], res

async def handle(request: Request):
    username = request.match_info.get('username')
    m3u8, stats = await get_m3u8(username)
    if not m3u8:
        return web.json_response({"success": False, "message": "Live stream may not be active"}, status=404)
    
    return web.json_response({"success": True, "m3u8": m3u8, "stats": stats}, status=200)

app = web.Application()
app.add_routes([web.get('/{username}', handle)])
web.run_app(app)
