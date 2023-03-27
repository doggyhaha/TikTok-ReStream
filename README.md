# Tiktok ReStream 🎵

This is a simple webserver + example Telegram bot that allows you to get the HLS stream from TikTok live streams. 

## Usage

1. Install the requirements with `pip install -r requirements.txt` 
2. Run the server with `python server.py`
3. Review the settings in bot.py (audio quality, video quality and server url)
4. Run the bot with `python bot.py`

The Telegram bot depends on [py-tgcalls](https://github.com/pytgcalls/pytgcalls) which depends on [NodeJS](https://nodejs.org/) and [FFmpeg](https://ffmpeg.org/) so you need to install both of them for the bot to work, not needed for the server.

## Warning

This was just a fun project to see if it was possible to get the HLS stream from TikTok, i do not guarantee that this will work in the future.

TikTok website is different in the following countries: Italy, Hong Kong and United Kingdom. so you may need to use a VPN/proxy to use this.

This project is not affiliated with TikTok in any way. 

TikTok is a trademark or registered trademark of TikTok. This project is not intended for commercial use.