import requests
import discord
import json

with open("apikey.txt", "r") as file:
    apikey = file.read()
gamesplayed = {}

def loadjson():
    try:
        with open("users.json", "r") as file:
            users = json.load(file)
            return users
    except Exception:
        with open("users.json", "w") as file:
            json.dump({"users" : []}, file)

def adduser(id):
    userfile = loadjson()
    if str(id) not in userfile["users"]:
        userfile["users"].append(str(id))
        with open("users.json", "w") as file:
            json.dump(userfile, file, indent=4)

def removeuser(id):
    userfile = loadjson()
    if str(id) in userfile["users"]:
        userfile["users"].remove(str(id))
        with open("users.json", "w") as file:
            json.dump(userfile, file, indent=4)

loadjson()
userids = loadjson()["users"]
steamuserstr = ",".join(userids)

def checkforgames(): #this code is so ass
    if loadjson()["users"] is not None:
        request = requests.get(f'https://api.steampowered.com/ISteamUser/GetPlayerSummaries/v0002/?key={apikey}&steamids={steamuserstr}').json()
        embed = None
        for player in request["response"]["players"]:
            if "gameid" in player and player["steamid"] not in gamesplayed:
                gamerequest = requests.get(f"https://store.steampowered.com/api/appdetails/?appids={player['gameid']}").json()
                gamesplayed[player["steamid"]] = {"gameid" : player['gameid'], "nickname" : player['personaname'], "gamename" : gamerequest[player['gameid']]['data']['name'], "headerurl" : gamerequest[player['gameid']]['data']['header_image'], 'userpfp' : player["avatarfull"]}
                print("adding the player to currently playing list")
                print(f"{player['personaname']} is playing {gamerequest[player['gameid']]['data']['name']}")
                embed = discord.Embed(colour=0x39a323, title="Чел зашёл в игру!!!", description=f'**{gamesplayed[player['steamid']]['nickname']} только что начал играть в [{gamesplayed[player['steamid']]['gamename']}](https://store.steampowered.com/app/{player['gameid']}).**')
                embed.set_thumbnail(url=gamesplayed[player["steamid"]]["headerurl"])
                embed.set_author(name=gamesplayed[player["steamid"]]['nickname'],icon_url=gamesplayed[player["steamid"]]["userpfp"])
                return embed
            if "gameid" not in player and player["steamid"] in gamesplayed:
                print(f"{gamesplayed[player['steamid']]['nickname']} is no longer playing {gamesplayed[player['steamid']]['gamename']}")
                embed = discord.Embed(colour=0xd11b1b, title="Чел вышел из игры", description=f'**{gamesplayed[player['steamid']]['nickname']} перестал играть в [{gamesplayed[player['steamid']]['gamename']}](https://store.steampowered.com/app/{gamesplayed[player['steamid']]['gameid']}).**')
                embed.set_thumbnail(url=gamesplayed[player["steamid"]]["headerurl"])
                embed.set_author(name=gamesplayed[player["steamid"]]['nickname'],icon_url=gamesplayed[player["steamid"]]["userpfp"])
                gamesplayed.pop(player["steamid"])
                print("removing the player from currenltly playing list")
                return embed
            if "gameid" in player and player["steamid"] in gamesplayed and player["gameid"] != gamesplayed[player["steamid"]]["gameid"]:
                gamerequest = requests.get(f"https://store.steampowered.com/api/appdetails/?appids={player['gameid']}").json()
                embed = discord.Embed(colour=0x39a323, title="Чел зашёл в другую игру!!!", description=f'**{gamesplayed[player['steamid']]['nickname']} перестал играть в [{gamesplayed[player['steamid']]['gamename']}](https://store.steampowered.com/app/{player['gameid']}).**')
                embed.set_author(name=gamesplayed[player["steamid"]]['nickname'],icon_url=gamesplayed[player["steamid"]]["userpfp"])
                gamesplayed[player["steamid"]] = {"gameid" : player['gameid'], "nickname" : player['personaname'], "gamename" : gamerequest[player['gameid']]['data']['name'], "headerurl" : gamerequest[player['gameid']]['data']['header_image'], 'userpfp' : player["avatarfull"]}
                print("adding the player to currently playing list")
                print(f"{player['personaname']} is playing {gamerequest[player['gameid']]['data']['name']}")
                embed.add_field(name="", value=f"**И только что зашёл в [{gamesplayed[player["steamid"]]["gamename"]}](https://store.steampowered.com/app/{player['gameid']}).**")
                embed.set_thumbnail(url=gamesplayed[player["steamid"]]["headerurl"])
                return embed

def playinglist():
    embed = discord.Embed(colour=0x39a323, title="Список игроков", description="Список всех людей которые прямо сейчас в игре")
    if gamesplayed:
        for person in gamesplayed:
            player = gamesplayed.get(person)
            embed.add_field(name=f"{player["nickname"]}", inline=True, value=f"> [{player['gamename']}](https://store.steampowered.com/app/{player['gameid']})")
        return embed
    return None