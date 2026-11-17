import asyncio, os, re, json, subprocess
import xml.etree.ElementTree as ET
import requests
from TikTokLive import TikTokLiveClient

USER = os.environ["TIKTOK_USER"]
TOKEN = os.environ["TG_TOKEN"]
CHAT = os.environ["TG_CHAT"]
LIVE_FILE = "state.txt"
POST_FILE = "last_post.txt"


def read(p):
    return open(p).read().strip() if os.path.exists(p) else ""


def write(p, v):
    open(p, "w").write(v)


def send(text):
    requests.post(
        f"https://api.telegram.org/bot{TOKEN}/sendMessage",
        data={"chat_id": CHAT, "text": text},
        timeout=20,
    )


def latest_post():
    ids = {}
    for base in ["https://rsshub.app", "https://rsshub.rssforever.com"]:
        try:
            r = requests.get(
                f"{base}/tiktok/user/@{USER}",
                timeout=25,
                headers={"User-Agent": "Mozilla/5.0"},
            )
            if r.status_code != 200:
                continue
            root = ET.fromstring(r.content)
            for item in root.findall("./channel/item"):
                link = item.findtext("link") or ""
                m = re.search(r"/video/(\d+)", link)
                if m:
                    ids[int(m.group(1))] = link
            if ids:
                break
        except Exception as e:
            print("rss error:", base, e)
    if not ids:
        try:
            out = subprocess.run(
                ["yt-dlp", "--flat-playlist", "--playlist-end", "5", "-J",
                 f"https://www.tiktok.com/@{USER}"],
                capture_output=True, text=True, timeout=90,
            )
            data = json.loads(out.stdout)
            for e in data.get("entries", []):
                if str(e.get("id", "")).isdigit():
                    ids[int(e["id"])] = f"https://www.tiktok.com/@{USER}/video/{e['id']}"
        except Exception as e:
            print("ytdlp error:", e)
    if not ids:
        return None
    best = max(ids)
    return best, ids[best]


async def check_live():
    client = TikTokLiveClient(unique_id="@" + USER)
    try:
        live = await client.is_live()
    except Exception as e:
        print("live error:", e)
        return
    was = read(LIVE_FILE) == "1"
    if live and not was:
        send(f"🔴 {USER} لایو شد!\nhttps://www.tiktok.com/@{USER}/live")
    write(LIVE_FILE, "1" if live else "0")


def check_post():
    res = latest_post()
    if not res:
        print("post: no data")
        return
    pid, link = res
    last = read(POST_FILE)
    if last and pid > int(last):
        send(f"🎬 {USER} پست جدید گذاشت!\n{link}")
    if not last or pid > int(last):
        write(POST_FILE, str(pid))


asyncio.run(check_live())
check_post()
