import asyncio, os, requests
from TikTokLive import TikTokLiveClient

USER = os.environ["TIKTOK_USER"]
TOKEN = os.environ["TG_TOKEN"]
CHAT = os.environ["TG_CHAT"]
STATE = "state.txt"

async def main():
    client = TikTokLiveClient(unique_id="@" + USER)
    try:
        live = await client.is_live()
    except Exception as e:
        print("error:", e)
        return
    was = os.path.exists(STATE) and open(STATE).read().strip() == "1"
    if live and not was:
        requests.post(
            f"https://api.telegram.org/bot{TOKEN}/sendMessage",
            data={"chat_id": CHAT,
                  "text": f"🔴 {USER} لایو شد!\nhttps://www.tiktok.com/@{USER}/live"},
        )
    open(STATE, "w").write("1" if live else "0")

asyncio.run(main())
