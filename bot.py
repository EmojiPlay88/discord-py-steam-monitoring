from types import NoneType
import discord
import main
import asyncio
import json
from discord.ext import commands
from discord.ext.commands import Bot

with open("bottoken.txt", "r") as file:
    token = file.read()
intents = discord.Intents.all()
bot = Bot(intents=intents, command_prefix="!")

def loadjson():
    try:
        with open("channels.json", "r") as file:
            users = json.load(file)
            return users
    except Exception:
        with open("channels.json", "w") as file:
            json.dump({}, file)

async def steammonitoring():
    channels = loadjson()
    while True:
        games = main.checkforgames()
        if games != None:
            for guildid in channels:
                channel = bot.get_channel(channels.get(guildid))
                await channel.send(embed=games)
        await asyncio.sleep(5)

def checkpermissions(userid, guildid):
    guild = bot.get_guild(guildid)
    user = guild.get_member(userid)
    for role in user.roles:
        if role.permissions.administrator:
            return True
    return False

class MainCommands(commands.Cog):
    def __init__(self):
        self.bot = bot

    @commands.hybrid_command(name="adduser")
    async def adduser(self, ctx, user):
        """Add the user to Steam monitoring list (REMEMBER TO INSERT THE DEFAULT STEAMID)"""
        if user != int and ctx.author != bot:
            await ctx.reply("Please enter a correct steamid")
        if checkpermissions(ctx.author.id, ctx.guild.id):
            main.adduser(user)
            await ctx.reply("Adding the user to steam monitoring list")
        else:
            await ctx.reply("You don't have administrator permissions")

    @commands.hybrid_command(name="removeuser")
    async def removeuser(self, ctx, user):
        """Remove the user from Steam monitoring list (REMEMBER TO INSERT THE DEFAULT STEAMID)"""
        if user != int:
            await ctx.reply("Please enter a correct steamid")
        if checkpermissions(ctx.author.id, ctx.guild.id):
            main.removeuser(user)
            await ctx.reply("Removing the user from steam monitoring list")
        else:
            await ctx.reply("You don't have administrator permissions")

    @commands.hybrid_command(name="setchannel")
    async def setchannel(self, ctx, channel:discord.TextChannel):
        """Set a channel where automatic messages will be sent"""
        if checkpermissions(ctx.author.id, ctx.guild.id):
            channelsfile = loadjson()
            if ctx.guild.id not in channelsfile:
                channelsfile[str(ctx.guild.id)] = channel.id
                with open("channels.json", "w") as file:
                    json.dump(channelsfile, file, indent=4)
                await ctx.reply("Setting the channel")
        else:
            await ctx.reply("You don't have administrator permissions")

    @commands.hybrid_command(name="playinglist")
    async def playinglist(self, ctx):
        """Список всех людей которые прямо сейчас в игре"""
        embed = main.playinglist()
        if type(embed) == NoneType:
            embed = discord.Embed(title="Список игроков", description="Похоже прямо сейчас никто не играет...", colour=0x39a323)
        await ctx.reply(embed=embed)

@bot.event
async def on_ready():
    loadjson()
    await bot.add_cog(MainCommands())
    await bot.tree.sync()
    print(f'Logged as {bot.user} (ID: {bot.user.id})')
    bot.loop.create_task(steammonitoring())

bot.run(token)