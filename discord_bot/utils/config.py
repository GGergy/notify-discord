import json


with open('discord_bot/assets/secure/config.json') as jsf:
    data = json.load(jsf)
    discord_key = data['discord_key']
    music_key = data['music_key']
