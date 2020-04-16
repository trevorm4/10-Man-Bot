import discord
from bot import Bot
import yaml
bot = Bot("!")
options = yaml.load(open("config.yaml",'r'))
@bot.command()
async def newcaps(ctx):
    lobby_channel = [i for i in ctx.guild.voice_channels if i.name == options['lobby']][0]
    players = lobby_channel.members
    bot.new_game(players)
    await ctx.send(embed=await bot.generate_captains())
@bot.command()
async def draft(ctx,player_name):
    await ctx.send(embed=await bot.draft_player(ctx.author,player_name))
@bot.command() 
async def ready(ctx):
    await ctx.send(embed=await bot.ready_up(ctx.author))

bot.run(options['token'])