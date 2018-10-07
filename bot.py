from discord.ext.commands import Bot
from discord import Game
from uszipcode import SearchEngine
from datetime import datetime
import requests
import asyncio
import os
import json

TOKEN = os.environ['TOKEN']
DARK_SKY_API_TOKEN = os.environ['DARK_SKY_API_TOKEN']
BOT_PREFIX = ('?', '!')

client = Bot(command_prefix=BOT_PREFIX)


@client.event
async def on_ready():
    await client.change_presence(game=Game(name="with humans"))


@client.command()
async def weather(zipcode):
    search = SearchEngine(simple_zipcode=True)
    zipcode = search.by_zipcode(zipcode)
    data = zipcode.to_dict()

    url = "https://api.darksky.net/forecast/" + DARK_SKY_API_TOKEN + "/" + str(
        data['lat']) + "," + str(data['lng'])
    response = requests.get(url)
    value = response.json()['currently']['temperature']
    await client.say('Current temp in ' + data['post_office_city'] + ' is ' +
                     str(value))


client.run(TOKEN)
