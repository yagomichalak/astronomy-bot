import discord
from discord.ext import commands, tasks
import keep_alive
import os

client = commands.Bot(command_prefix='!')
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
  await ctx.send(f"**Command successfully tested! Ping: '__{round(client.latency / 100)}__'**")

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