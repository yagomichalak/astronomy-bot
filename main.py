import discord
from discord.ext import commands, tasks
from discord.utils import escape_mentions
from discord import slash_command
import os
from extra import utils
from itertools import cycle
from re import match
from dotenv import load_dotenv
load_dotenv()

client = commands.Bot(command_prefix='o!', intents=discord.Intents.default(), help_command=None)
on_guild_log_id: int = int(os.getenv('ON_GUILD_LOG_ID'))
status = cycle(['slash', ])#'member', 'server',])

@client.event
async def on_ready() -> None:
	""" Tells when the bot is ready to go. """
	in_servers.start()
	print("Bot is ready!")

@client.event
async def on_command_error(ctx, error) -> None:
	""" On error command handler. """

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
async def on_application_command_error(ctx, error) -> None:
	""" On error command handler. """

	if isinstance(error, commands.MissingPermissions):
		await ctx.send(error)

	if isinstance(error, commands.BotMissingPermissions):
		await ctx.respond("**I don't have permissions to run this command!**")

	if isinstance(error, commands.BadArgument):
		await ctx.respond("**Invalid parameters!**")

	if isinstance(error, commands.CommandOnCooldown):
		secs = error.retry_after
		if int(secs) >= 60:
			await ctx.respond(f"You are on cooldown! Try again in {secs/60:.1f} minutes!")
		else:
			await ctx.respond(error)
		
	if isinstance(error, commands.NotOwner):
		await ctx.respond("**You can't do that, you're not the owner!**")

	if isinstance(error, commands.MissingRequiredArgument):
		await ctx.respond('**Make sure to inform all parameters!**')

	print(error)

@client.event
async def on_guild_join(guild) -> None:
	""" Logs when the bot joins a new server. """

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
	guild_log = client.get_channel(on_guild_log_id)
	if guild_log:
		embed.set_thumbnail(url=guild.icon.url)
		await guild_log.send(embed=embed)

@client.event
async def on_guild_remove(guild) -> None:
	""" Logs when the bot leaves a server. """

	embed = discord.Embed(
		title="Goodbye world!",
		description=f"We lost contact with the **Earth {len(client.guilds)+1}**, AKA **{guild.name}**!",
		color=discord.Color.red()
	)
	embed.set_thumbnail(url=guild.icon.url)
	#Logs it in the bot's support server on_guild log
	guild_log = client.get_channel(on_guild_log_id)
	if guild_log:
		await guild_log.send(embed=embed)

@client.event
async def on_message(message) -> None:
	""" Checks whether someone pinged the bot. """

	if message.author.bot:
		return

	if match(f"<@!?{client.user.id}>", message.content) is not None:
		await message.channel.send(f"**{message.author.mention}, my prefix is `/`**")

	await client.process_commands(message)


@tasks.loop(seconds=30)
async def in_servers() -> None:
	""" Updates the server and member count. """
	
	ns = next(status)
	if ns == 'slash':
		ns = f"slash commands. /"
		return await client.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name=ns))
	elif ns == 'member':
		# ns = f"for {len([x for l in [g.members for g in client.guilds] for x in l])} users!"
		ns = 'for shumanity!'

	elif ns == 'server':
		ns = f"on {len(client.guilds)} servers!"

	#all_guilds = len(await client.fetch_guilds(limit=150).flatten())
	try:
		await client.change_presence(activity=discord.Streaming(name=ns, url="https://www.twitch.tv/nasa"))
	except Exception:
		pass

@discord.slash_command()
async def ping(ctx) -> None:
	""" Shows the latency. """

	await ctx.respond(f"**Ping: __{round(client.latency * 1000)}__ ms**")


@client.command()
@commands.cooldown(1, 10, type=commands.BucketType.guild)
async def info(ctx):
	""" Shows some information about the bot itself. """

	await ctx.defer()
	current_time = await utils.get_time_now()
	embed = discord.Embed(title='Artemis Bot', description="__**WHAT IS IT?:**__```Hello, the Artemis Bot is an open source bot based on astronomy, which its only purpose is to portray information about the universe.```", colour=discord.Colour.dark_purple(), url="https://theartemisbot.herokuapp.com", timestamp=current_time)
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
	embed.set_footer(text=ctx.guild.name,
				icon_url='https://cdn.discordapp.com/attachments/719020754858934294/720294157406568458/universe_hub_server_icon.png')
	embed.set_thumbnail(
	url=client.user.display_avatar)
	embed.set_author(name='DNK#6725', url='https://discord.gg/languages',
				icon_url='https://cdn.discordapp.com/attachments/719020754858934294/720289112040669284/DNK_icon.png')
	await ctx.respond(embed=embed)

@slash_command()
async def invite(ctx):
	""" Sends the bot's invite. """

	invite = 'https://discord.com/api/oauth2/authorize?client_id=723699955008798752&permissions=2147534912&scope=bot%20applications.commands'
	await ctx.respond(f"Here's my invite:\n{invite}", ephemeral=True)



@slash_command()
async def servers(ctx) -> None:
	""" Shows how many servers the bot is in. """

	await ctx.respond(f"**I'm currently in {len(client.guilds)} servers!**")

@slash_command()
async def support(ctx) -> None:
	""" Support for the bot and its commands. """

	link = 'https://discord.gg/6GXvrck'
	current_time = await utils.get_time_now()

	embed = discord.Embed(
		title="__Support__",
		description=f"For any support; in other words, questions, suggestions or doubts concerning the bot and its commands, contact me **DNK#6725**, or join our support server by clicking [here]({link})",
		timestamp=current_time,
		url=link,
		color=ctx.author.color
	)
	await ctx.respond(embed=embed)

@slash_command(aliases=['patron'])
async def patreon(ctx) -> None:
	""" Support the creator on Patreon. """

	link = 'https://www.patreon.com/dnk'
	current_time = await utils.get_time_now()

	embed = discord.Embed(
		title="__Patreon__",
		description=f"If you want to finacially support my work and motivate me to keep adding more features, put more effort and time into this and other bots, click [here]({link})",
		color=ctx.author.color,
		timestamp=current_time,
		url=link
	)
	await ctx.respond(embed=embed, ephemeral=True)


for file_name in os.listdir('./cogs'):
	if str(file_name).endswith(".py"):
		client.load_extension(f"cogs.{file_name[:-3]}")

client.run(os.getenv('TOKEN'))
