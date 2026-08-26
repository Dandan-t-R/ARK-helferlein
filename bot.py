import discord, json, requests
from bs4 import BeautifulSoup
from deep_translator import GoogleTranslator
import os

# Config laden
cfg = json.load(open("config.json"))

# Token aus Render Environment
TOKEN = os.getenv("TOKEN")

# Quellen aus config.json
SOURCES_INFO = cfg["sources_info"]
SOURCES_ID = cfg["sources_id"]
SOURCES_TAMING = cfg["sources_taming"]
SOURCES_STAT = cfg["sources_stat"]
SOURCES_CRAFT = cfg["sources_craft"]
SOURCES_CONFIG = cfg["sources_config"]

# Prefixes für Kurzbefehle / Aliase
PREFIXES = {
    # Info / allgemeine Kurzinfos
    "!i": "info",
    "!info": "info",
    "!infos": "info",
    "!search": "info",
    "!dino": "info",
    "!iteminfo": "info",

    # ID / Codes / Spawn / Give
    "!id": "id",
    "!code": "id",
    "!give": "id",
    "!spawn": "id",
    "!item": "id",

    # Taming / KO / Methoden (strikt Dododex/Steam)
    "!t": "taming",
    "!taming": "taming",
    "!tame": "taming",
    "!tamen": "taming",
    "!tameinfo": "taming",

    # Stat / Taming-Werte / KO-Werte (strikt Dododex/Steam)
    "!stat": "stat",
    "!stats": "stat",
    "!tamecalc": "stat",
    "!dex": "stat",

    # Craft / Rezepte / Herstellung
    "!c": "craft",
    "!craft": "craft",
    "!crafting": "craft",
    "!crafts": "craft",
    "!herstellen": "craft",
    "!brauen": "craft",
    "!kochen": "craft",
    "!recipe": "craft",

    # Config / Settings / INI / Server
    "!co": "config",
    "!config": "config",
    "!cfg": "config",
    "!settings": "config",
    "!ini": "config"
}

def fetch(url):
    try:
        soup = BeautifulSoup(requests.get(url, timeout=10).text, "html.parser")
        return soup.get_text(" ").lower()
    except:
        return ""

# Datencontainer
DATA = {
    "info": {},
    "id": {},
    "taming": {},
    "stat": {},
    "craft": {},
    "config": {}
}

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print("Helferlein ist online!")

    # Quellen laden
    DATA["info"] = {u: fetch(u) for u in SOURCES_INFO}
    DATA["id"] = {u: fetch(u) for u in SOURCES_ID}
    DATA["taming"] = {u: fetch(u) for u in SOURCES_TAMING}
    DATA["stat"] = {u: fetch(u) for u in SOURCES_STAT}
    DATA["craft"] = {u: fetch(u) for u in SOURCES_CRAFT}
    DATA["config"] = {u: fetch(u) for u in SOURCES_CONFIG}

@client.event
async def on_message(msg):
    if msg.author == client.user:
        return

    text = msg.content.lower().strip()
    parts = text.split()

    if len(parts) == 0:
        return

    cmd = parts[0]

    # Prefix prüfen
    if cmd not in PREFIXES:
        return

    category = PREFIXES[cmd]

    # Suchbegriff (Mehrwort)
    query = " ".join(parts[1:])
    if len(query) < 2:
        await msg.channel.send("Bitte mehr eingeben, z.B. `!info rex boss`")
        return

    hits = []
    for url, content in DATA[category].items():
        if query in content:
            i = content.find(query)
            snippet = content[i:i+300]
            hits.append((url, snippet))

    if not hits:
        await msg.channel.send(cfg["no_hits"] + "\n\n" + cfg["signature"])
        return

    formatted = []
    for url, snippet in hits:
        summary = snippet[:180].split(".")[0] + "."
        summary = GoogleTranslator(source='auto', target='de').translate(summary)
        site = url.split("/")[2]
        formatted.append(f"🦖 **{summary}**\n➡️ [{site}]({url})")

    output = "\n\n".join(formatted)

    # Kürzen für Discord
    if len(output) > 1800:
        output = output[:1800] + "\n\n…gekürzt…"

    await msg.channel.send(output + "\n\n" + cfg["signature"])

client.run(TOKEN)

