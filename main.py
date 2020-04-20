import discord
from bot import Bot
import yaml
from utils import get_member_name
from converters import Player

options = yaml.load(open("config.yaml",'r'))
bot = Bot("!", options["scheme"].split(" "))

@bot.command()
async def newcaps(ctx):
    lobby_channel = next((i for i in ctx.guild.voice_channels if i.name == options['lobby']), None)
    a_channel = next((i for i in ctx.guild.voice_channels if i.name == options['team_a']), None)
    b_channel = next((i for i in ctx.guild.voice_channels if i.name == options['team_b']), None)
    players = lobby_channel.members
    await bot.new_game(players)
    await ctx.send(embed=await bot.generate_captains(a_channel,b_channel))
@bot.command()
async def draft(ctx,player_name : Player):
    temp_dict = {i.name : i for i in ctx.guild.voice_channels}
    channel_dict = {"A":temp_dict[options["team_a"]],"B":temp_dict[options["team_b"]]}
    await ctx.send(embed=await bot.draft_player(ctx.author,player_name,channel_dict))
@bot.command()
async def draft_for_bot(ctx,bot_name : Player, player_name : Player):
    temp_dict = {i.name : i for i in ctx.guild.voice_channels}
    channel_dict = {"A":temp_dict[options["team_a"]],"B":temp_dict[options["team_b"]]}
    await ctx.send(embed=await bot.draft_player(bot_name,player_name,channel_dict))
@bot.command()
async def setcaps(ctx,cap1 : Player, cap2 : Player):
    lobby_channel = next((i for i in ctx.guild.voice_channels if i.name == options['lobby']), None)
    players = lobby_channel.members
    await bot.new_game(players)
    await bot.set_captain(cap1,"A")
    await bot.set_captain(cap2,"B")
    embed = discord.Embed(title="Valorant 10 Man Bot",
            description="The captains are {} and {}".format(get_member_name(cap1,lower=False),get_member_name(cap2,lower=False)))
    await ctx.send(embed=embed)
@bot.command()
async def new(ctx):
    lobby_channel = next((i for i in ctx.guild.voice_channels if i.name == options['lobby']), None)
    embed = await bot.new_game(lobby_channel.members)
    await ctx.send(embed=embed)
@bot.command()
async def help(ctx):
    embed = discord.Embed(title="Valorant 10 Man Bot",
            description="The following commands are available\n\n :one: !newcaps : selects captains for current game\n\
                         :two: !draft <player name> : drafts player to your team (you must be captain)\n\
                         :three: !setcaps <captain1> <captain2> : manually set the captains \n\
                         :four: !new : starts a new game (does not set captains)")
    await ctx.send(embed=embed)
bot.run(options['token'])