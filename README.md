# Winston

Discord bot with video game (LoL, PUBG, Fortnite) and other random commands. You can use `.` as a prefix for commands.

## Usage

| Commands             | Description                                               |
| -------------------- | --------------------------------------------------------- |
| `.weather <zipcode>` | Displays current weather and daily forecast               |
| `.lol <name>`        | Displays ranked information on a summoner (rank, w/l, lp) |
| `.pubg <name>`       | Displays PUBG stats (Solo, Duo, Squads)                   |
| `.fortnite <name>`   | Displayed Fortnite stats (Solo, Duo, Squads)              |
| `.play <url>`        | Plays a YouTube video in a voice channel                  |
| `.queue <url>`       | Adds a YouTube video to the queue                         |
| `.pause`             | Pauses the current playing video                          |
| `.resume`            | Resumes the video                                         |
| `.stop`              | Stops the current playing video                           |
| `.color <hex>`       | Changes your role color(must be hex, ex: 4F5D2F)          |
| `.kick <@username>`  | Kicks the mentioned user                                  |
| `.ban <@username>`   | Bans the mentioned user                                   |
| `.unban <@username>` | Removes the mentioned user for the banlist                |

## Run locally

```
git clone https://github.com/himanshup/winston.git
cd winston
pip install -r requirements.txt
```

1. [Create a bot account](https://discordpy.readthedocs.io/en/rewrite/discord.html) and copy the token
2. Create accounts to get a Dark Sky, LoL, PUBG, and Fortnite API key
3. Create a .env file and add your API keys (TOKEN is the token from step 1):

```
TOKEN=''
DARK_SKY_KEY=''
RIOT_API_KEY=''
PUBG_API_KEY=''
FORTNITE_KEY=''
```

4. Run `python bot.py` and your bot should be online

## Credits

Thanks to [fortnitetracker](https://fortnitetracker.com/) for letting me use their API! :)
