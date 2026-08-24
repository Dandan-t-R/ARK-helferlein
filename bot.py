import discord, json, requests
from bs4 import BeautifulSoup

# Config laden
cfg = json.load(open("config.json"))
TOKEN = cfg["token"]
SOURCES = cfg["sources"]

# Channel-Daten laden
try:
    channels = json.load(open("channels.json"))
except:
    channels = {}

def save_channels():
    json.dump(channels, open("channels.json", "w"), indent=4)

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
    print("Helper ist online !")

@client.event
async def on_message(msg):
    if msg.author == client.user:
        return

    guild_id = str(msg.guild.id)

    # Kanal setzen
    if msg.content.lower() == "!setchannel":
        channels[guild_id] = msg.channel.id
        save_channels()
        await msg.channel.send("Kanal gesetzt.")
        return

    # Wenn kein Kanal gesetzt ist → nichts tun
    if guild_id not in channels:
        return

    # Nur im gesetzten Kanal reagieren
    if msg.channel.id != channels[guild_id]:
        return

    q = msg.content.lower()
    hits = []

    for url, text in DATA.items():
        if q in text:
            i = text.find(q)
            hits.append(f"{url}\n{text[i:i+300]}")

    if hits:
    formatted = []
    for url, text in DATA.items():
        if q in text:
            i = text.find(q)
            summary = text[i:i+180].split(".")[0] + "."
            site = url.split("/")[2]  # nur Domain
            formatted.append(f"🦖 **{summary}**\n➡️ [{site}]({url})")

    await msg.channel.send("\n\n".join(formatted) + "\n\n" + cfg["signature"])

else:
    await msg.channel.send(cfg["no_hits"] + "\n\n" + cfg["signature"])
    
        
client.run(TOKEN)
