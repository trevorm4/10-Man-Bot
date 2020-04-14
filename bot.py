import discord
from discord.ext import commands

bot = commands.Bot(command_prefix='!')
g = None

@bot.command(pass_context=True)
async def test(ctx, arg):
    global g
    g = arg
    embed = discord.Embed(title="test",description="global is now {}".format(g))
    await ctx.send(embed=embed)
@bot.command(pass_context=True)
async def read(ctx):
    global g
    author = ctx.author
    guild = ctx.guild
    await author.move_to(guild.voice_channels[-1])
    await ctx.send("your value is {} and your author is {} and channels are {}".format(g,author,guild.voice_channels))

bot.run('Njk5MDk3MjA4NjI4NDQ1MjA0.XpV_rQ.X-mwvgrFOWcAIrctatcgyO_Scwg')

