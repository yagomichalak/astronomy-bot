import discord
from discord.ext import commands, tasks
import inspect
import io
import textwrap
import traceback
from contextlib import redirect_stdout
import os
from itertools import cycle
from re import match
from dotenv import load_dotenv
load_dotenv()

intents = discord.Intents.default()
client = commands.Bot(command_prefix='o!', intents=intents)
client.remove_command('help')
token = os.getenv('TOKEN')
on_guild_log_id = os.getenv('ON_GUILD_LOG_ID')
status = cycle(['member', 'server'])

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

  # Tells that the command doesn't exist
  # if isinstance(error, commands.CommandNotFound):
  #   await ctx.send(f"**There's no such command as `{ctx.message.content.split()[0]}`!**")


  if isinstance(error, commands.BadArgument):
    await ctx.send("**Invalid parameters!**")

  if isinstance(error, commands.CommandOnCooldown):
    secs = error.retry_after
    if int(secs) >= 60:
      await ctx.send(f"You are on cooldown! Try again in {secs/60:.1f} minutes!")
    else:
      await ctx.send(error)
      

  if isinstance(error, commands.NotOwner):
    await ctx.send("**You can't do that, you're not the owner!**")

  if isinstance(error, commands.MissingRequiredArgument):
    await ctx.send('**Make sure to inform all parameters!**')

  print(error)

@client.event
async def on_guild_join(guild):
  general = guild.system_channel
  embed = discord.Embed(
      title="Hello world!",
      description=f"Another glitch in the matrix has been spotted, and that's the **Earth {len(client.guilds)}**, AKA **{guild.name}**!",
      color=client.user.color
      )

  # Sends an embedded message in the new server
  if general and general.permissions_for(guild.me).send_messages:
    try:
      await general.send(embed=embed)
    except Exception:
      print('No perms to send a welcome message!')

  #Logs it in the bot's support server on_guild log
  guild_log = client.get_channel(int(on_guild_log_id))
  if guild_log:
    embed.set_thumbnail(url=guild.icon_url)
    await guild_log.send(embed=embed)
  

@client.event
async def on_guild_remove(guild):
  embed = discord.Embed(title="Goodbye world!",
      description=f"We lost contact with the **Earth {len(client.guilds)+1}**, AKA **{guild.name}**!",
      color=discord.Color.red()
      )
  embed.set_thumbnail(url=guild.icon_url)
  #Logs it in the bot's support server on_guild log
  guild_log = client.get_channel(int(on_guild_log_id))
  if guild_log:
    await guild_log.send(embed=embed)

@client.event
async def on_message(message):
  if message.author.bot:
    return

  if match(f"<@!?{client.user.id}>", message.content) is not None:
    await message.channel.send(f"**{message.author.mention}, my prefix is `{client.command_prefix}`**")

  await client.process_commands(message)
  


@tasks.loop(seconds=30)
async def in_servers():
  ns = next(status)
  if ns == 'member':
    # ns = f"for {len([x for l in [g.members for g in client.guilds] for x in l])} users!"
    ns = 'for the humanity!'

  elif ns == 'server':
    ns = f"on {len(client.guilds)} servers!"

  #all_guilds = len(await client.fetch_guilds(limit=150).flatten())
  try:
    await client.change_presence(activity=discord.Streaming(name=ns, url="https://www.twitch.tv/nasa"))
  except Exception:
    pass

@client.command()
async def ping(ctx):
  '''
  Shows the latency.
  '''
  await ctx.send(f"**Ping: __{round(client.latency * 1000)}__ ms**")


@client.command()
@commands.cooldown(1, 10, type=commands.BucketType.guild)
async def info(ctx):
  '''
  Shows some information about the bot itself.
  '''
  embed = discord.Embed(title='Artemis Bot', description="__**WHAT IS IT?:**__```Hello, the Artemis Bot is an open source bot based on astronomy, which its only purpose is to portray information about the universe.```", colour=discord.Colour.dark_purple(), url="https://theartemisbot.herokuapp.com", timestamp=ctx.message.created_at)
  embed.add_field(name="📚 __**Topics**__",
                value="`27` topics about the universe to explore.",
                inline=True)
  embed.add_field(name="💻 __**Programmed in**__",
                value="The Artemis bot was built in Python, and you can find its GitHub repository [here](https://github.com/yagomichalak/astronomy-bot).",
                inline=True)
  embed.add_field(name="🚀 __**Space Agencies**__", 
                value="You can see all `88` space agencies listed nicely.",
                inline=True)
  embed.add_field(name="🎥 __**Movies**__",
                value="A special list with `34` movies about astronomy and space in general.",
                inline=True)
  embed.add_field(name="🎮 __**Minigames**__",
                value="It currently has a quiz game and a short story, choice-based game.",
                inline=True)
  embed.add_field(name="🌎 __**Global ranking**__ ", 
                value="It has a global level ranking system universe themed.",       inline=True)
  embed.set_footer(text=ctx.guild.name,
                icon_url='https://cdn.discordapp.com/attachments/719020754858934294/720294157406568458/universe_hub_server_icon.png')
  embed.set_thumbnail(
    url=client.user.avatar_url)
  embed.set_author(name='DNK#6725', url='https://discord.gg/7DyWxSt',
                icon_url='https://cdn.discordapp.com/attachments/719020754858934294/720289112040669284/DNK_icon.png')
  await ctx.send(embed=embed)

@client.command()
async def invite(ctx):
  '''
  Sends the bot's invite.
  '''
  invite = 'https://discord.com/oauth2/authorize?client_id=723699955008798752&permissions=126016&scope=bot'
  await ctx.send(f"Here's my invite:\n{invite}")


@client.command(hidden=True)
@commands.is_owner()
async def eval(ctx, *, body=None):
  """ (OWNER) Executes a given command from Python onto Discord.
  :param body: The body of the command. """

  await ctx.message.delete()
  if not body:
    return await ctx.send("**Please, inform the code body!**")

  """Evaluates python code"""
  env = {
    'ctx': ctx,
    'client': client,
    'channel': ctx.channel,
    'author': ctx.author,
    'guild': ctx.guild,
    'message': ctx.message,
    'source': inspect.getsource
  }

  def cleanup_code(content):
    """Automatically removes code blocks from the code."""
    # remove ```py\n```
    if content.startswith('```') and content.endswith('```'):
      return '\n'.join(content.split('\n')[1:-1])

    # remove `foo`
    return content.strip('` \n')

  def get_syntax_error(e):
    if e.text is None:
      return f'```py\n{e.__class__.__name__}: {e}\n```'
    return f'```py\n{e.text}{"^":>{e.offset}}\n{e.__class__.__name__}: {e}```'

  env.update(globals())

  body = cleanup_code(body)
  stdout = io.StringIO()
  err = out = None

  to_compile = f'async def func():\n{textwrap.indent(body, "  ")}'

  def paginate(text: str):
    '''Simple generator that paginates text.'''
    last = 0
    pages = []
    for curr in range(0, len(text)):
      if curr % 1980 == 0:
        pages.append(text[last:curr])
        last = curr
        appd_index = curr
    if appd_index != len(text)-1:
      pages.append(text[last:curr])
    return list(filter(lambda a: a != '', pages))

  try:
    exec(to_compile, env)
  except Exception as e:
    err = await ctx.send(f'```py\n{e.__class__.__name__}: {e}\n```')
    return await ctx.message.add_reaction('\u2049')

  func = env['func']
  try:
    with redirect_stdout(stdout):
      ret = await func()
  except Exception as e:
    value = stdout.getvalue()
    err = await ctx.send(f'```py\n{value}{traceback.format_exc()}\n```')
  else:
    value = stdout.getvalue()
    if ret is None:
      if value:
        try:

          out = await ctx.send(f'```py\n{value}\n```')
        except:
          paginated_text = paginate(value)
          for page in paginated_text:
            if page == paginated_text[-1]:
              out = await ctx.send(f'```py\n{page}\n```')
              break
            await ctx.send(f'```py\n{page}\n```')
    else:
      try:
        out = await ctx.send(f'```py\n{value}{ret}\n```')
      except:
        paginated_text = paginate(f"{value}{ret}")
        for page in paginated_text:
          if page == paginated_text[-1]:
            out = await ctx.send(f'```py\n{page}\n```')
            break
          await ctx.send(f'```py\n{page}\n```')


@client.command()
async def help(ctx, cmd: str = None):
  '''
  Shows some information about commands and categories.
  '''
  if not cmd:
      embed = discord.Embed(
      title="All commands and categories",
      description=f"```ini\nUse {client.command_prefix}help command or {client.command_prefix}help category to know more about a specific command or category\n\n[Examples]\n[1] Category: {client.command_prefix}help Astronomy\n[2] Command : {client.command_prefix}help listUniverse```",
      timestamp=ctx.message.created_at,
      color=ctx.author.color
      )

      for cog in client.cogs:
          cog = client.get_cog(cog)
          commands = [c.name for c in cog.get_commands() if not c.hidden]
          if commands:
            embed.add_field(
            name=f"__{cog.qualified_name}__",
            value=f"`Commands:` {', '.join(commands)}",
            inline=False
            )

      cmds = []
      for y in client.walk_commands():
          if not y.cog_name and not y.hidden:
              cmds.append(y.name)
      embed.add_field(
      name='__Uncategorized Commands__', 
      value=f"`Commands:` {', '.join(cmds)}", 
      inline=False)
      await ctx.send(embed=embed)

  else:
    # Checks if it's a command
    if command := client.get_command(cmd.lower()):
      command_embed = discord.Embed(title=f"__Command:__ {command.name}", description=f"__**Description:**__\n```{command.help}```", color=ctx.author.color, timestamp=ctx.message.created_at)
      return await ctx.send(embed=command_embed)

    for cog in client.cogs:
      if str(cog).lower() == str(cmd).lower():
          cog = client.get_cog(cog)
          cog_embed = discord.Embed(title=f"__Cog:__ {cog.qualified_name}", description=f"__**Description:**__\n```{cog.description}```", color=ctx.author.color, timestamp=ctx.message.created_at)
          for c in cog.get_commands():
              if not c.hidden:
                  cog_embed.add_field(name=c.name,value=c.help,inline=False)

          return await ctx.send(embed=cog_embed)

    # Otherwise, it's an invalid parameter (Not found)
    else:
      await ctx.send(f"**Invalid parameter! `{cmd}` is neither a command nor a cog!**")


@client.command()
async def servers(ctx):
  '''
  Shows how many servers the bot is in.
  '''
  await ctx.send(f"**I'm currently in {len(client.guilds)} servers!**")

@client.command(hidden=True)
@commands.is_owner()
async def load(ctx, extension: str):
  '''
  (Owner) loads a cog.
  '''
  if not extension:
    return await ctx.send("**Please, inform an extension!**")
  for cog in os.listdir('./cogs'):
      if str(cog[:-3]).lower() == str(extension).lower():
        try:
          client.load_extension(f"cogs.{cog[:-3]}")
        except commands.ExtensionAlreadyLoaded:
          return await ctx.send(f"**The `{extension}` cog is already loaded!**")
        return await ctx.send(f"**`{extension}` cog loaded!**")
  else:
    await ctx.send(f"**`{extension}` is not a cog!**")


@client.command(hidden=True)
@commands.is_owner()
async def unload(ctx, extension: str):
  '''
  (Owner) unloads a cog.
  '''
  if not extension:
    return await ctx.send("**Please, inform an extension!**")
  for cog in client.cogs:
      if str(cog).lower() == str(extension).lower():
        try:
          client.unload_extension(f"cogs.{cog}")
        except commands.ExtensionNotLoaded:
          return await ctx.send(f"**The `{extension}` cog is not even loaded!**")
        return await ctx.send(f"**`{extension}` cog unloaded!**")
  else:
    await ctx.send(f"**`{extension}` is not a cog!**")


@client.command(hidden=True)
@commands.is_owner()
async def reload(ctx, extension: str):
  '''
  (Owner) reloads a cog.
  '''
  if not extension:
    return await ctx.send("**Please, inform an extension!**")
  
  for cog in client.cogs:
      if str(cog).lower() == str(extension).lower():
        try:
          client.unload_extension(f"cogs.{cog}")
          client.load_extension(f"cogs.{cog}")
        except commands.ExtensionNotLoaded:
          return await ctx.send(f"**The `{extension}` cog is not even loaded!**")
        return await ctx.send(f"**`{extension}` cog reloaded!**")
  else:
    await ctx.send(f"**`{extension}` is not a cog!**")


@client.command(hidden=True)
@commands.is_owner()
async def reload_all(ctx):
  '''
  (Owner) reloads all cogs.
  '''
  for file_name in os.listdir('./cogs'):
    try:
      if str(file_name).endswith(".py"):
        client.unload_extension(f"cogs.{file_name[:-3]}")
        client.load_extension(f"cogs.{file_name[:-3]}")
    except commands.ExtensionNotLoaded:
      pass
  await ctx.send(f"**Cogs reloaded!**")

@client.command()
async def support(ctx):
  '''
  Support for the bot and its commands.
  '''
  link = 'https://discord.gg/6GXvrck'

  embed = discord.Embed(
  title="__Support__",
  description=f"For any support; in other words, questions, suggestions or doubts concerning the bot and its commands, contact me **DNK#6725**, or join our support server by clicking [here]({link})",
  timestamp=ctx.message.created_at,
  url=link,
  color=ctx.author.color
  )
  await ctx.send(embed=embed)

@client.command(aliases=['patron'])
async def patreon(ctx):
  """ Support the creator on Patreon. """

  link = 'https://www.patreon.com/dnk'

  embed = discord.Embed(
  title="__Patreon__",
  description=f"If you want to finacially support my work and motivate me to keep adding more features, put more effort and time into this and other bots, click [here]({link})",
  timestamp=ctx.message.created_at,
  url=link,
  color=ctx.author.color
  )
  await ctx.send(embed=embed)


for file_name in os.listdir('./cogs'):
  if str(file_name).endswith(".py"):
    client.load_extension(f"cogs.{file_name[:-3]}")
    

# keep_alive.keep_alive()

client.run(token)
