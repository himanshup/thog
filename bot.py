from discord.ext.commands import Bot
from discord import Game
from uszipcode import SearchEngine
from datetime import datetime
from pubg_python import PUBG, Shard
import discord
import requests
import asyncio
import os
import json

TOKEN = os.environ['TOKEN']
DARK_SKY_KEY = os.environ['DARK_SKY_KEY']
RIOT_API_KEY = os.environ['RIOT_API_KEY']
PUBG_API_KEY = os.environ['PUBG_API_KEY']
FORTNITE_KEY = os.environ['FORTNITE_KEY']
BOT_PREFIX = ('?', '!', '.')

client = Bot(command_prefix=BOT_PREFIX)


@client.event
async def on_ready():
    await client.change_presence(game=Game(name="with humans"))


@client.command(name='weather', description='Get weather forecast when given a zipcode.', brief='Weather forecast')
async def weather(zipcode=None):
    if zipcode:
        search = SearchEngine(simple_zipcode=True)
        results = search.by_zipcode(zipcode)
        if str(results.zipcode) == 'None':
            await client.say('No results, try again.')
        else:
            data = results.to_dict()

            url = "https://api.darksky.net/forecast/" + DARK_SKY_KEY + "/" + str(
                data['lat']) + "," + str(data['lng'])

            response = requests.get(url)
            temp = response.json()['currently']['temperature']
            icon = response.json()['currently']['icon']
            dailySummary = response.json()['daily']['summary']
            daily = response.json()['daily']['data']
            embed = discord.Embed(
                title=data['post_office_city'],
                description='Currently: ' + str(int(round(temp))) + chr(176),
                colour=discord.Colour.blue()
            )

            embed.add_field(name='Daily Forecast',
                            value=dailySummary, inline=False)

            for temp in daily:
                embed.add_field(name=str(datetime.utcfromtimestamp(temp['time']).strftime('%A %m/%d')), value='High: ' + str(
                    int(round(temp['temperatureHigh']))) + chr(176) + ' \nLow: ' + str(int(round(temp['temperatureLow']))) + chr(176), inline=True)

            embed.set_thumbnail(
                url='https://darksky.net/images/weather-icons/' + icon + '.png')

            await client.say(embed=embed)
    else:
        await client.say('Please enter a zipcode after the command (ex: ?weather 12345)')


@client.command(name='lolprofile', description='Get LoL summoner info by summoner name', brief='LoL Summoner info')
async def lolprofile(name=None):
    if name:
        # Gets summoner info (id, account id, name, level, icon) for future api calls
        url = 'https://na1.api.riotgames.com/lol/summoner/v3/summoners/by-name/' + \
            name + '?api_key=' + RIOT_API_KEY
        response = requests.get(url)
        # Check if summoner name exists
        if str(response) == '<Response [200]>':
            summonerName = response.json()['name']
            summonerId = str(response.json()['id'])
            accountId = str(response.json()['accountId'])
            icon = response.json()['profileIconId']
            level = str(response.json()['summonerLevel'])

            embed = discord.Embed(
                title=summonerName,
                description='Level ' + level,
                colour=discord.Colour.blue()
            )
            embed.set_thumbnail(
                url='http://ddragon.leagueoflegends.com/cdn/8.19.1/img/profileicon/' + str(icon) + '.png')

            # Uses summoner id from first call to get ranked info (rank, wins, losses, etc)
            rankInfoUrl = 'https://na1.api.riotgames.com/lol/league/v3/positions/by-summoner/' + \
                summonerId + '?api_key=' + RIOT_API_KEY
            rankInfo = requests.get(rankInfoUrl)
            # If the user isn't ranked, it will instead embed an unranked icon
            if len(rankInfo.json()) < 1:
                rankIcon = 'https://res.cloudinary.com/dmrien29n/image/upload/v1534829199/provisional.png'
                embed.set_image(url=rankIcon)
                embed.add_field(name='Unranked', value='Unranked')
                await client.say(embed=embed)
            else:
                # Loop through the ranked info and find the data where queue type is equal to ranked solo
                for info in rankInfo.json():
                    if info['queueType'] == 'RANKED_SOLO_5x5':
                        rankData = info

                leagueName = rankData['leagueName']
                tier = rankData['tier']
                rank = rankData['rank']
                queue = rankData['queueType']
                lp = rankData['leaguePoints']
                wins = rankData['wins']
                losses = rankData['losses']
                wratio = int(round(100 * wins / (wins + losses)))
                rankIcon = 'https://res.cloudinary.com/dmrien29n/image/upload/v1534829199/' + tier + '.png'

                embed.set_image(url=rankIcon)
                embed.add_field(name=tier + ' ' + rank, value=str(lp) + ' LP / ' + str(wins) +
                                'W ' + str(losses) + 'L\n' + 'Win Ratio ' + str(wratio) + '%\n' + leagueName)

                await client.say(embed=embed)
        elif str(response) == '<Response [404]>':
            await client.say('No results for ' + name + ', try again (without spaces)')
        else:
            await client.say('An error occured.')
    else:
        await client.say('Please enter a summoner name (without spaces) after the command.')


@client.command()
async def pubg(name):
    api = PUBG(PUBG_API_KEY, Shard.PC_NA)


@client.command()
async def fortnite():
    url = 'https://api.fortnitetracker.com/v1/profile/pc/ninja'
    response = requests.get(url, headers={'TRN-Api-Key': FORTNITE_KEY})
    print(response.json())
    await client.say(response.json())


client.run(TOKEN)
