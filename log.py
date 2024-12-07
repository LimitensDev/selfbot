from discord import SyncWebhook
import discord
import json
import datetime
from datetime import datetime

with open('config.json', 'r') as file:
    data = json.load(file)

webhook_url = data["webhook"]


def send_webhook(data: str):
    try:
        webhook = SyncWebhook.from_url(webhook_url)
        webhook.send(embed=discord.Embed(title=(datetime.now().strftime('%Y-%m-%d %H:%M:%S')), description=data, color=discord.Color.dark_grey()))
        return True
    except:
        return False
