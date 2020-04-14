import discord
from discord.ext import commands
import yaml
import random

bot = commands.Bot(command_prefix='!')
options = yaml.load(open("config.yaml",'r'))
team_a = []
team_b = []
ready_dict = {}
nick_to_player = {}
captain_a = None
captain_b = None

@bot.command()
async def newcaps(ctx):
    global ready_dict
    global nick_to_player
    global captain_a
    global captain_b
    global team_a
    global team_b
    lobby_channel = [i for i in ctx.guild.voice_channels if i.name == options['lobby']][0]
    players = lobby_channel.members
    if len(players) != 10:
        embed = discord.Embed(title="Valorant 10 Man bot",description="Sorry, you need 10 players and you currently have {} players".format(len(players)))
        await ctx.send(embed=embed)
        return
    ready_dict = {k:False for k in players}
    nick_to_player = {k.nick : k for k in players}
    caps = random.sample(players,2)
    embed = discord.Embed(title="Valorant 10 Man bot",description="The captains are now @{} and @{}".format(caps[0].nick,caps[1].nick))
    captain_a = caps[0]
    captain_b = caps[1]
    team_a = [captain_a.nick]
    team_b = [captain_b.nick]
    await ctx.send(embed=embed)

@bot.command()
async def ready(ctx):
    global ready_dict
    ready_dict[ctx.author] = True
    embed = discord.Embed(title="Valorant 10 Man bot",description="{} is now ready".format(ctx.author.nick))
@bot.command()
async def unready(ctx):
    global ready_dict
    ready_dict[ctx.author] = False
    embed = discord.Embed(title="Valorant 10 Man bot",description="{} is now NOT ready".format(ctx.author.nick))

@bot.command()
async def draft(ctx,nick):
    global nick_to_player
    global team_a
    global team_b
    global captain_a
    global captain_b
    global options
    remaining = await get_remaining()
    team_chosen = None
    if nick not in nick_to_player.keys():
        embed = discord.Embed(title="Valorant 10 Man bot",description="{} is not a valid player, please try again".format(nick))
        await ctx.send(embed=embed)
        return
    elif nick not in remaining:
        embed = discord.Embed(title="Valorant 10 Man bot",description="{} was drafted already.\n The remaining players are {}".format(nick,remaining))
        await ctx.send(embed=embed)
        return
    else:        
        if ctx.author == captain_a:
            if len(team_a) > len(team_b): # player a should never have more players when choosing
                embed = discord.Embed(title="Valorant 10 Man bot",description="You've already drafted this turn, please wait for the other captain")
                await ctx.send(embed=embed)
                return
            team_a.append(nick)
            team_chosen = "a"
        elif ctx.author == captain_b:
            if len(team_b) > len(team_a): # Team 2 should never have more players when choosing
                embed = discord.Embed(title="Valorant 10 Man bot",description="You've already drafted this turn, please wait for the other captain")
                await ctx.send(embed=embed)
                return
            team_b.append(nick)
            team_chosen = "b"
        else:
            embed = discord.Embed(title="Valorant 10 Man bot",description="You are not a captain.\n The captains are {} and {}".format(captain_a.nick,captain_b.nick))
            await ctx.send(embed=embed)
            return
    await move_player(ctx,nick,options["team_{}".format(team_chosen)])
    if len(team_a) == 5 and len(team_b) == 5:
        embed = discord.Embed(title="Valorant 10 Man bot",description="All the players have been drafted, captains should now use !start to start the game")
        await ctx.send(embed=embed)

@bot.command()
async def start(ctx):
    global captain_a
    global captain_b
    global options
    if ctx.author == captain_a:
        await move_player(ctx, author.nick, options["team_a"])
    elif ctx.author == captain_b:
        await move_player(ctx,author.nick,options["team_b"])
    else:
        embed = discord.Embed(title="Valorant 10 Man bot",description="You're not a captain!")
        await ctx.send(embed=embed)


async def get_remaining():
    global team_a
    global team_b
    players = list(nick_to_player.keys())
    remaining = []
    for p in players:
        if p not in team_a and p not in team_b:
            remaining.append(p)
    return remaining

async def move_player(ctx,nick,channel_name):
    global nick_to_player
    channel = [i for i in ctx.guild.voice_channels if i.name == channel_name][0]
    await nick_to_player[nick].move_to(channel)
bot.run(options['token'])

