import discord, json, requests
from bs4 import BeautifulSoup

cfg = json.load(open("config.json"))
TOKEN = cfg["token"]
SOURCES = cfg["sources"]
CHANNEL_ID = cfg["channel_id"]

def fetch(url):
    try:
        soup = BeautifulSoup(requests.get(url, timeout=10).text, "html.parser")
        return soup.get_text(" ").lower()
    except:
        return ""

DATA = {u: fetch(u) for u in SOURCES}
client = discord.Client(intents=discord.Intents.default())

@client.event
async def on_ready():
    print("Helper ist online und bereit.")

@client.event
async def on_message(msg):
    if msg.author == client.user:
        return
    if msg.channel.id != CHANNEL_ID:
        return

    q = msg.content.lower()
    hits = []
    for url, text in DATA.items():
        if q in text:
            i = text.find(q)
            hits.append(f"{url}\n{text[i:i+300]}")
    await msg.channel.send("\n\n".join(hits) if hits else "Keine Infos gefunden.")

client.run(TOKEN)
