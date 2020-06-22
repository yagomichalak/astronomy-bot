import discord
from discord.ext import commands, tasks
import keep_alive
import os

client = commands.Bot(command_prefix='o!')
client.remove_command('help')
token = os.getenv('TOKEN')

@client.event
async def on_ready():
  in_servers.start()
  print("Bot is ready!")

@client.event
async def on_command_error(ctx, error):

  if isinstance(error, commands.MissingPermissions):
    await ctx.send(error)

  if isinstance(error, commands.BotMissingPermissions):
    await ctx.send("**I don't have permissions to run this command!**")

  if isinstance(error, commands.CommandNotFound):
    await ctx.send(f"**There's no such command as `{ctx.message.content.split()[0]}`!**")

  if isinstance(error, commands.BadArgument):
    await ctx.send("**Bad argument!**")

  if isinstance(error, commands.CommandOnCooldown):
    await ctx.send(error)

  if isinstance(error, commands.NotOwner):
    await ctx.send("**You can't do that, you're not the owner!**")

  if isinstance(error, commands.MissingRequiredArgument):
    await ctx.send('**Make sure to inform all parameters!**')


@tasks.loop(seconds=10)
async def in_servers():
  all_guilds = len(await client.fetch_guilds(limit=150).flatten())
  await client.change_presence(activity=discord.Streaming(name=f"on {all_guilds} planets", url="https://www.twitch.tv/nasa"))

@client.command()
async def ping(ctx):
  '''
  Shows the latency.
  '''
  await ctx.send(f"**Command successfully tested! Ping: __{round(client.latency / 100)}__**")


@client.command()
@commands.cooldown(1, 10, type=commands.BucketType.guild)
async def info(ctx):
    '''
    Shows your astro-profile
    '''
    embed = discord.Embed(title='Artemis Bot', description="__**WHAT IS IT?:**__```Hello, the Artemis Bot is an open source bot based on astronomy, which its only purpose is to portray information about the universe.```", colour=discord.Colour.dark_purple(), url="https://discord.gg/8Bemp2a", timestamp=ctx.message.created_at)
    embed.add_field(name="📚 __**Topics**__",
                    value="More than 15 topics to explore.",
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
@commands.has_permissions(add_reactions=True, embed_links=True)
async def help(ctx, co: str = None) -> object:
  '''Provides a description of all commands and cogs.
  :param co: Cog or command that you want to see. (Optional)'''
  if not co:
    halp=discord.Embed(title='Cog Listing and Uncategorized Commands',
                              description='```Use o!help *cog* or help *command* to find out more about them!\n(BTW, the Cog Name Must Be in Title Case, Just Like this Sentence.)```', color=discord.Color.dark_purple(),timestamp=ctx.message.created_at)

    cogs_desc = []
    for x in client.cogs:
        cogs_desc.append(x)
    halp.add_field(name='__Cogs__',value=f"**>** {', '.join(cogs_desc)}",inline=False)

    cmds_desc = ''
    for y in client.walk_commands():
        if not y.cog_name and not y.hidden:
            if y.help:
              cmds_desc += (f"{y.name} - `{y.help}`"+'\n')
            else:
              cmds_desc += (f"{y.name}"+'\n')
    halp.add_field(name='__Uncategorized Commands__',value=cmds_desc[0:len(cmds_desc)-1],inline=False)

    await ctx.message.add_reaction(emoji='✉')
    #return await ctx.send(embed=halp)
    return await ctx.send('',embed=halp)


  # Checks if it's a command
  if command := client.get_command(co):
    command_embed = discord.Embed(title=f"__Command:__ {command.name}", description=f"__**Description:**__\n```{command.help}```", color=discord.Color.dark_purple(), timestamp=ctx.message.created_at)
    #print(command.__doc__)
    await ctx.send(embed=command_embed)

  # Checks if it's a cog
  elif cog := client.get_cog(co):
    cog_embed = discord.Embed(title=f"__Cog:__ {cog.qualified_name}", description=f"__**Description:**__\n```{cog.description}```", color=discord.Color.dark_purple(), timestamp=ctx.message.created_at)
    #name = command.qualified_name
    #print(command.description)
    for c in cog.get_commands():
        if not c.hidden:
            cog_embed.add_field(name=c.name,value=c.help,inline=False)

    await ctx.send(embed=cog_embed)

  # Otherwise, it's an invalid parameter (Not found)
  else:
    await ctx.send(f"**Invalid parameter! `{co}` is neither a command nor a cog!**")

@client.command(hidden=True)
@commands.is_owner()
async def load(ctx, extension: str):
  if not extension:
    return await ctx.send("**Please, inform an extension!**")
  try:
    client.load_extension(f"cogs.{extension}")
  except commands.ExtensionAlreadyLoaded:
    return await ctx.send(f"**The `{extension}` cog is already loaded!**")
  await ctx.send(f"**`{extension}` cog loaded!**")


@client.command(hidden=True)
@commands.is_owner()
async def unload(ctx, extension: str):
  if not extension:
    return await ctx.send("**Please, inform an extension!**")
  try:
    client.unload_extension(f"cogs.{extension}")
  except commands.ExtensionNotLoaded:
    return await ctx.send(f"**The `{extension}` cog is not even loaded!**")
  await ctx.send(f"**`{extension}` cog unloaded!**")


@client.command(hidden=True)
@commands.is_owner()
async def reload(ctx, extension: str):
  if not extension:
    return await ctx.send("**Please, inform an extension!**")
  try:
    client.unload_extension(f"cogs.{extension}")
    client.load_extension(f"cogs.{extension}")
  except commands.ExtensionNotLoaded:
    return await ctx.send(f"**The `{extension}` cog is not even loaded!**")
  await ctx.send(f"**`{extension}` cog reloaded!**")


for file_name in os.listdir('./cogs'):
  if str(file_name).endswith(".py"):
    client.load_extension(f"cogs.{file_name[:-3]}")
    

keep_alive.keep_alive()

client.run(token)
