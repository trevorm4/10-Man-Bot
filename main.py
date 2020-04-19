import discord
from bot import Bot
import yaml
from utils import get_member_name
bot = Bot("!")
options = yaml.load(open("config.yaml",'r'))
@bot.command()
async def newcaps(ctx):
    lobby_channel = [i for i in ctx.guild.voice_channels if i.name == options['lobby']][0]
    a_channel = [i for i in ctx.guild.voice_channels if i.name == options['team_a']][0]
    b_channel = [i for i in ctx.guild.voice_channels if i.name == options['team_b']][0]
    players = lobby_channel.members
    await bot.new_game(players)
    await ctx.send(embed=await bot.generate_captains(a_channel,b_channel))
@bot.command()
async def draft(ctx,player_name):
    temp_dict = {i.name : i for i in ctx.guild.voice_channels}
    channel_dict = {"A":temp_dict[options["team_a"]],"B":temp_dict[options["team_b"]]}
    await ctx.send(embed=await bot.draft_player(ctx.author,player_name,channel_dict))
@bot.command() 
async def ready(ctx):
    await ctx.send(embed=await bot.ready_up(ctx.author))
@bot.command()
async def setcaps(ctx,cap1,cap2):
    await bot.set_captain(cap1,"A")
    await bot.set_captain(cap2,"B")
    embed = discord.Embed(title="Valorant 10 Man Bot",
            description="The captains are @{} and @{}".format(get_member_name(cap1),get_member_name(cap2)))
    await ctx.send(embed=embed)
@bot.command()
async def new(ctx):
    lobby_channel = [i for i in ctx.guild.voice_channels if i.name == options['lobby']][0]
    print(lobby_channel)
    embed = await bot.new_game(lobby_channel.members)
    print(bot.nick_to_player)
    await ctx.send(embed=embed)


bot.run(options['token'])