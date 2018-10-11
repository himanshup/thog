from discord.ext.commands import Bot
from discord import Game
from uszipcode import SearchEngine
from datetime import datetime
import discord
import requests
import asyncio
import os
import json
import re

TOKEN = os.environ['TOKEN']
# DARK_SKY_KEY = os.environ['DARK_SKY_KEY']
# RIOT_API_KEY = os.environ['RIOT_API_KEY']
# PUBG_API_KEY = os.environ['PUBG_API_KEY']
# FORTNITE_KEY = os.environ['FORTNITE_KEY']
BOT_PREFIX = ('.')

client = Bot(command_prefix=BOT_PREFIX)

players = {}
queues = {}


def checkQueue(id):
    if queues[id] != []:
        player = queues[id].pop(0)
        players[id] = player
        player.start()


@client.event
async def on_ready():
    await client.change_presence(game=Game(name="with humans"))


@client.event
async def on_member_join(member):
    await client.create_role(member.server, name=str(member.id))
    role = discord.utils.get(
        member.server.roles, name=str(member.id))
    await client.add_roles(member, role)


@client.event
async def on_member_remove(member):
    role = discord.utils.get(member.server.roles, name=str(member.id))
    await client.delete_role(member.server, role)


@client.command()
async def kick(username: discord.Member):
    await client.kick(username)
    await client.say('User has been kicked.')


@client.command()
async def ban(username: discord.Member, delete_message_days=0):
    await client.ban(username, delete_message_days)
    await client.say('User has been banned.')


@client.command(pass_context=True)
async def unban(ctx, username):
    bans = await client.get_bans(ctx.message.server)
    # Remove uneeded characters from input
    id = re.sub('[<>@]', '', username)
    for user in bans:
        if id == user.id:
            await client.unban(ctx.message.server, user)
            await client.say('Unbanned user.')


@client.command(pass_context=True)
async def play(ctx, url):
    server = ctx.message.server
    author = ctx.message.author
    voiceChannel = author.voice_channel
    vc = await client.join_voice_channel(voiceChannel)

    player = await vc.create_ytdl_player(url, after=lambda: checkQueue(server.id))
    players[server.id] = player
    player.start()


@client.command(pass_context=True)
async def queue(ctx, url):
    server = ctx.message.server
    author = ctx.message.author
    vc = client.voice_client_in(server)

    player = await vc.create_ytdl_player(url, after=lambda: checkQueue(server.id))

    if server.id in queues:
        queues[server.id].append(player)
    else:
        queues[server.id] = [player]
    await client.say('Queued the video.')


@client.command(pass_context=True)
async def stop(ctx):
    id = ctx.message.server.id
    server = ctx.message.server
    voice_client = client.voice_client_in(server)
    players[id].stop()
    await voice_client.disconnect()


@client.command(pass_context=True)
async def pause(ctx):
    id = ctx.message.server.id
    players[id].pause()


@client.command(pass_context=True)
async def resume(ctx):
    id = ctx.message.server.id
    players[id].resume()


@client.command(pass_context=True)
async def color(ctx, color):
    try:
        role = discord.utils.get(
            ctx.message.author.server.roles, name=str(ctx.message.author.id))
        if role:
            await client.edit_role(ctx.message.server, role, colour=discord.Colour(int(color, 16)))
        else:
            print('Role does not exist, creating it now...')
            await client.create_role(ctx.message.server, name=str(ctx.message.author.id), colour=discord.Colour(int(color, 16)))
            newRole = discord.utils.get(
                ctx.message.author.server.roles, name=str(ctx.message.author.id))
            await client.add_roles(ctx.message.author, newRole)
    except:
        await client.say('Please enter a Hex color.')


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


@client.command(name='lol', description='Get LoL summoner info by summoner name', brief='LoL Summoner info')
async def lol(name=None):
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
            return await client.say('No results for ' + name + ', try again (without spaces)')
        else:
            return await client.say('An error occured.')
    else:
        await client.say('Please enter a summoner name (without spaces) after the command.')


@client.command(name='pubg', description='Displays user stats for the current season (Solos, Duos, Squads)', brief='Displays PUBG stats')
async def pubg(name=None):
    if name:
        playerUrl = 'https://api.pubg.com/shards/pc-na/players?filter[playerNames]=' + name
        player = requests.get(playerUrl, headers={
            'accept': 'application/vnd.api+json', 'Authorization': PUBG_API_KEY})

        if ('errors' in player.json()):
            await client.say('No players found, try again (names are case sensitive).')
        else:
            uid = player.json()['data'][0]['id']
            name = player.json()['data'][0]['attributes']['name']

            embed = discord.Embed(
                title=name,
                description='Platform: PC',
                colour=discord.Colour.blue()
            )
            embed.set_thumbnail(
                url='https://pbs.twimg.com/profile_images/1010210923829587968/U94bbY2k_400x400.jpg')

            dataUrl = 'https://api.pubg.com/shards/steam/players/' + \
                uid + '/seasons/division.bro.official.pc-2018-01'
            response = requests.get(dataUrl, headers={
                'accept': 'application/vnd.api+json', 'Authorization': PUBG_API_KEY})
            data = response.json()['data']['attributes']['gameModeStats']
            # Solos
            wins = data['solo-fpp']['wins']
            losses = data['solo-fpp']['losses']
            top10 = data['solo-fpp']['top10s']
            kills = data['solo-fpp']['kills']
            assists = data['solo-fpp']['assists']
            damage = data['solo-fpp']['damageDealt']
            embed.add_field(name='----------SOLOS----------',
                            value=str(wins + losses) + ' Matches', inline=False)
            embed.add_field(name='Wins', value=str(wins), inline=True)
            embed.add_field(name='Losses', value=str(losses), inline=True)
            embed.add_field(name='Top 10', value=str(top10), inline=True)
            embed.add_field(name='Kills', value=str(kills), inline=True)
            embed.add_field(name='Assists', value=str(assists), inline=True)
            embed.add_field(name='Damage', value=str(damage), inline=True)
            # Duos
            winsDuos = data['duo-fpp']['wins']
            lossesDuos = data['duo-fpp']['losses']
            top10Duos = data['duo-fpp']['top10s']
            killsDuos = data['duo-fpp']['kills']
            assistsDuos = data['duo-fpp']['assists']
            damageDuos = data['duo-fpp']['damageDealt']
            embed.add_field(name='----------DUOS----------',
                            value=str(winsDuos + lossesDuos) + ' Matches', inline=False)
            embed.add_field(name='Wins', value=str(winsDuos), inline=True)
            embed.add_field(name='Losses', value=str(lossesDuos), inline=True)
            embed.add_field(name='Top 10', value=str(top10Duos), inline=True)
            embed.add_field(name='Kills', value=str(killsDuos), inline=True)
            embed.add_field(name='Assists', value=str(
                assistsDuos), inline=True)
            embed.add_field(name='Damage', value=str(damageDuos), inline=True)
            # Squads
            winsSquads = data['duo-fpp']['wins']
            lossesSquads = data['duo-fpp']['losses']
            top10Squads = data['duo-fpp']['top10s']
            killsSquads = data['duo-fpp']['kills']
            assistsSquads = data['duo-fpp']['assists']
            damageSquads = data['duo-fpp']['damageDealt']
            embed.add_field(name='----------SQUADS----------',
                            value=str(winsSquads + lossesSquads) + ' Matches', inline=False)
            embed.add_field(name='Wins', value=str(winsSquads), inline=True)
            embed.add_field(name='Losses', value=str(
                lossesSquads), inline=True)
            embed.add_field(name='Top 10', value=str(top10Squads), inline=True)
            embed.add_field(name='Kills', value=str(killsSquads), inline=True)
            embed.add_field(name='Assists', value=str(
                assistsSquads), inline=True)
            embed.add_field(name='Damage', value=str(
                damageSquads), inline=True)

            await client.say(embed=embed)
    else:
        await client.say('Please enter a pubg username after the command.')


@client.command(name='fortnite', description='Displays user stats for the current season (Solos, Duos, Squads)', brief='Displays Fortnite stats')
async def fortnite(name=None):
    if name:
        url = 'https://api.fortnitetracker.com/v1/profile/pc/' + name
        response = requests.get(url, headers={'TRN-Api-Key': FORTNITE_KEY})
        data = response.json()

        if ('error' in data):
            return await client.say('Player Not Found.')
        if ('curr_p2' in data['stats']) or ('curr_p10' in data['stats']) or ('curr_p9' in data['stats']):
            name = data['epicUserHandle']
            platform = data['platformNameLong']
            embed = discord.Embed(
                title=name,
                description='Platform: ' + platform,
                colour=discord.Colour.blue()
            )
            embed.set_thumbnail(
                url='https://yt3.ggpht.com/a-/AN66SAxcsemSomK02qGAmiXnXzm0GR8LrSwHPMc-=s900-mo-c-c0xffffffff-rj-k-no')

            if ('curr_p2' in data['stats']):
                # Solos
                wins = data['stats']['curr_p2']['top1']['value']
                rating = data['stats']['curr_p2']['trnRating']['value']
                kd = data['stats']['curr_p2']['kd']['value']
                winRatio = data['stats']['curr_p2']['winRatio']['value']
                kills = data['stats']['curr_p2']['kills']['value']
                top10 = data['stats']['curr_p2']['top10']['value']
                kpg = data['stats']['curr_p2']['kpg']['value']
                matches = data['stats']['curr_p2']['matches']['value']
                embed.add_field(name='----------SOLOS----------',
                                value=matches + ' Matches', inline=False)
                embed.add_field(name='Rating', value=rating, inline=True)
                embed.add_field(name='Wins', value=wins, inline=True)
                embed.add_field(name='Kills', value=kills, inline=True)
                embed.add_field(name='Win %', value=winRatio, inline=True)
                embed.add_field(name='K/D', value=kd, inline=True)
                embed.add_field(name='Kills Per Game', value=kpg, inline=True)
            elif ('curr_p10' in data['stats']):
                # Duos
                winsDuos = data['stats']['curr_p10']['top1']['value']
                ratingDuos = data['stats']['curr_p10']['trnRating']['value']
                kdDuos = data['stats']['curr_p10']['kd']['value']
                winRatioDuos = data['stats']['curr_p10']['winRatio']['value']
                killsDuos = data['stats']['curr_p10']['kills']['value']
                top10Duos = data['stats']['curr_p10']['top10']['value']
                kpgDuos = data['stats']['curr_p10']['kpg']['value']
                matchesDuos = data['stats']['curr_p10']['matches']['value']
                embed.add_field(name='----------DUOS----------',
                                value=matchesDuos + ' Matches', inline=False)
                embed.add_field(name='Rating', value=ratingDuos, inline=True)
                embed.add_field(name='Wins', value=winsDuos, inline=True)
                embed.add_field(name='Kills', value=killsDuos, inline=True)
                embed.add_field(name='Win %', value=winRatioDuos, inline=True)
                embed.add_field(name='K/D', value=kdDuos, inline=True)
                embed.add_field(name='Kills Per Game',
                                value=kpgDuos, inline=True)
            elif ('curr_p9' in data['stats']):
                # Squads
                winsSquads = data['stats']['curr_p9']['top1']['value']
                ratingSquads = data['stats']['curr_p9']['trnRating']['value']
                kdSquads = data['stats']['curr_p9']['kd']['value']
                winRatioSquads = data['stats']['curr_p9']['winRatio']['value']
                killsSquads = data['stats']['curr_p9']['kills']['value']
                top10Squads = data['stats']['curr_p9']['top10']['value']
                kpgSquads = data['stats']['curr_p9']['kpg']['value']
                matchesSquads = data['stats']['curr_p9']['matches']['value']
                embed.add_field(name='----------SQUADS----------',
                                value=matchesSquads + ' Matches', inline=False)
                embed.add_field(name='Rating', value=ratingSquads, inline=True)
                embed.add_field(
                    name='Wins', value=winsSquads, inline=True)
                embed.add_field(
                    name='Kills', value=killsSquads, inline=True)
                embed.add_field(
                    name='Win %', value=winRatioSquads, inline=True)
                embed.add_field(
                    name='K/D', value=kdSquads, inline=True)
                embed.add_field(name='Kills Per Game',
                                value=kpgSquads, inline=True)

            embed.set_footer(
                text='Information provided by fortnitetracker.com')
            await client.say(embed=embed)
        else:
            await client.say(name + ' has no player data.')
    else:
        await client.say('Please enter an Epic username after the command.')

client.run(TOKEN)
