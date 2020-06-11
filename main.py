import discord
from discord.ext import commands, tasks
import keep_alive
import os

client = commands.Bot(command_prefix='!')
client.remove_command('help')
token = os.getenv('TOKEN')

@client.event
async def on_ready():
  in_servers.start()
  print("Bot is ready!")


@tasks.loop(seconds=10)
async def in_servers():
  all_guilds = len(await client.fetch_guilds(limit=150).flatten())
  await client.change_presence(activity=discord.Streaming(name=f"on {all_guilds} planets", url="https://www.twitch.tv/nasa"))

@client.command()
async def ping(ctx):
  '''
  Show the latency.
  '''
  await ctx.send(f"**Command successfully tested! Ping: __{round(client.latency / 100)}__**")


@client.command()
@commands.cooldown(1, 10, type=commands.BucketType.guild)
async def info(ctx):
    '''
    Does something
    '''
    embed = discord.Embed(title='Artemis Bot', description="__**WHAT IS IT?:**__```Hello, the Artemis Bot is an open source bot based on astronomy, which its only purpose is to portray information about the universe.```", colour=discord.Colour.dark_purple(), url="https://discord.gg/8Bemp2a", timestamp=ctx.message.created_at)
    embed.add_field(name="📚 __**Topics**__",
                    value="More than 50 topics to explore.",
                    inline=False)
    embed.add_field(name="💻 __**Programmed in**__",
                    value="The Artemis bot was built in Python, and you can find its GitHub repository [here](https://github.com/yagomichalak/astronomy-bot)",
                    inline=False)
    embed.add_field(name="🌎 __**Global ranking**__ ", value="It has a global level ranking based on messages sent.", inline=False)
    embed.set_footer(text=ctx.guild.name,
                     icon_url='https://cdn.discordapp.com/attachments/719020754858934294/720294157406568458/universe_hub_server_icon.png')
    embed.set_thumbnail(
        url=client.user.avatar_url)
    embed.set_author(name='DNK#6725', url='https://discord.gg/7DyWxSt',
                     icon_url='https://cdn.discordapp.com/attachments/719020754858934294/720289112040669284/DNK_icon.png')
    await ctx.send(embed=embed)

@client.command()
async def load(ctx, extension: str):
  if not extension:
    return await ctx.send("**Please, inform an extension!**", delete_after=3)
  client.load_extension(f"cogs.{extension}")
  await ctx.send(f"**{extension} loaded!**", delete_after=3)


@client.command()
async def unload(ctx, extension: str):
  if not extension:
    return await ctx.send("**Please, inform an extension!**", delete_after=3)
  client.unload_extension(f"cogs.{extension}")
  await ctx.send(f"**{extension} unloaded!**", delete_after=3)


@client.command()
async def reload(ctx, extension: str):
  if not extension:
    return await ctx.send("**Please, inform an extension!**", delete_after=3)
  client.unload_extension(f"cogs.{extension}")
  client.load_extension(f"cogs.{extension}")
  await ctx.send(f"**{extension} reloaded!**", delete_after=3)


for file_name in os.listdir('./cogs'):
  if str(file_name).endswith(".py"):
    client.load_extension(f"cogs.{file_name[:-3]}")
    

keep_alive.keep_alive()

client.run(token)
