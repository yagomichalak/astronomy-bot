import discord
from discord.ext import commands, tasks
from discord import slash_command, Option, OptionChoice

from images.all_topics import topics, image_links, galaxy
from images.agencies import space_agencies
from images.movies import movies

from extra import utils

from datetime import datetime
import os
import sqlite3
import json
import praw
import asyncio
import random
import wikipedia
import aiohttp
from typing import List, Tuple, Any, Union, Optional

TEST_GUILDS: List[int] = [int(os.getenv('SERVER_ID'))]

class Astronomy(commands.Cog):
	""" A category for astronomy related commands and features. """

	def __init__(self, client: commands.Bot) -> None:
		""" Class init method. """

		self.client = client
		self.reddit = praw.Reddit(
			client_id=os.getenv('REDDIT_CLIENT_ID'), # Client id
			client_secret=os.getenv('REDDIT_CLIENT_SECRET'), # My client secret
			user_agent=os.getenv('REDDIT_USER_AGENT'), # My user agent. It can be anything
			username='', # Not needed
			password='') # Not needed
		self.session = aiohttp.ClientSession(loop=client.loop)


	@commands.Cog.listener()
	async def on_ready(self) -> None:
		""" Tells when the cog is ready to go. """

		print("Astronomy cog is online!")

	async def read_topic(self, topic: str) -> List[str]:
		""" Reads a specific topic.
		:param topic: The topic to read. """

		with open(f"./texts/{topic}.txt", "r") as f:
			lines = f.readlines()
		return lines


	@slash_command(name="list_universe", guild_ids=TEST_GUILDS)
	async def _list_universe(self, ctx) -> None:
		""" Shows all topics available to see. """

		await ctx.defer()
		current_time = await utils.get_time_now()
		the_universe = discord.Embed(
			title="__**The Universe**__",
			description="The universe is big, and it is worth exploring and knowing more about it.",
			color=discord.Color.dark_purple(),
			timestamp=current_time
		)
		the_universe.add_field(name="__**Available topics:**__", value=f"```{', '.join(sorted(topics))}```", inline=True)
		the_universe.set_image(url='https://cdn.discordapp.com/attachments/719020754858934294/719022762743824445/space2.png')
		the_universe.set_thumbnail(url='https://cdn.discordapp.com/attachments/719020754858934294/719022762743824445/space2.png')
		the_universe.set_author(name="The Big Bang", url=ctx.author.display_avatar)
		the_universe.set_footer(text=ctx.guild.name, icon_url=ctx.guild.icon.url)

		await ctx.respond(embed=the_universe)

	@commands.command(aliases=['wi', 'whatis', 'whats'])
	async def whatIs(self, ctx, topic: str = None) -> None:
		""" Shows some information about the given topic.
		:param topic: The topic to show. """

		if not topic:
			return await ctx.send("**Please, inform a topic!**")
		
		if not topic.title() in topics:
			return await ctx.send(f"**`{topic.title()}` is not a topic that I cover!**")

		result = await self.read_topic(topic.title())
		links = image_links[topic.title()]
		embed = discord.Embed(
			title=f"({topic.title()})",
			color=discord.Color.dark_purple(),
			timestamp=ctx.message.created_at,
			url=links[1]
		)
		embed.set_author(name=ctx.guild.name, icon_url=ctx.guild.icon.url)
		embed.add_field(name="__**Definition:**__", value=f"```{' '.join(result)}```", inline=False)
		embed.set_thumbnail(url=links[0])
		embed.set_image(url=links[0])
		embed.set_footer(text=f"Requested by: {ctx.author.name}", icon_url=ctx.author.display_avatar)
		await ctx.send(embed=embed)

	async def the_database(self) -> Tuple[Any, Any]:
		""" Gets the database connection. """

		db = sqlite3.connect("universe.db")
		mycursor = db.cursor()
		return mycursor, db
		

	# Database commands
	@commands.command(hidden=True)
	@commands.is_owner()
	async def create_table(self, ctx) -> None:
		""" Creates the Universe table in the database. """

		if await self.table_exists():
			return await ctx.send("**Table __Universe__ already exists!**")
		
		mycursor, db = await self.the_database()
		mycursor.execute("""
			CREATE TABLE Universe (
				user_id INTEGER NOT NULL,,
				user_lvl INTEGER DEFAULT 1,
				user_xp INTEGER DEFAULT 0,
				user_ts INTEGER DEFAULT 0,
				PRIMARY KEY(user_id)
			)""")
		db.commit()
		mycursor.close()
		db.close()
		return await ctx.send("**Table __Universe__ created!**")

	@commands.command(hidden=True)
	@commands.is_owner()
	async def drop_table(self, ctx) -> None:
		""" Drops the Universe table from the database. """

		if not await self.table_exists():
			return await ctx.send("**Table __Universe__ doesn't exist!**")
		
		mycursor, db = await self.the_database()
		mycursor.execute("DROP TABLE Universe")
		db.commit()
		mycursor.close()
		db.close()
		return await ctx.send("**Table __Universe__ dropped!**")

	@commands.command(hidden=True)
	@commands.is_owner()
	async def reset_table(self, ctx) -> None:
		""" Resets the Unvierse table in the database. """

		if not await self.table_exists():
			return await ctx.send("**Table __Universe__ doesn't exist yet!**")
		
		mycursor, db = await self.the_database()
		mycursor.execute("DELETE FROM Universe")
		db.commit()
		mycursor.close()
		db.close()
		return await ctx.send("**Table __Universe__ reset!**")

	async def table_exists(self) -> bool:
		""" Checks whether the Universe table exists in the datable. """

		mycursor, db = await self.the_database()
		mycursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='Universe'")
		exists = mycursor.fetchone()
		mycursor.close()
		db.close()
		return True if exists else False

	async def insert_user(self, user_id: int) -> None:
		""" Inserts a user into the Universe table.
		:param user_id: The user ID. """

		mycursor, db = await self.the_database()
		mycursor.execute(f"INSERT INTO Universe (user_id) VALUES ({user_id})")
		db.commit()
		mycursor.close()
		db.close()

	async def update_data(self, user: discord.Member, the_time: int, channel: Union[discord.TextChannel, discord.Thread]) -> None:
		""" Updates the user data.
		:param user: The user to update.
		:param the_time: The current timestamp.
		:param channel: The context channel. """
		
		user_id = user.id
		the_member = await self.get_user(user_id)
		if the_time - the_member[3] >= 3 or the_member[2] == 0:
			await self.update_user_xp_time(user_id, the_time)
			await self.update_user_xp(user_id, 5)
			return await self.level_up(user, channel)

	async def update_user_xp_time(self, user_id: int, the_time: int) -> None:
		""" Updates the user XP time in the database.
		:param user_id: The user ID.
		:param the_time: The current timestamp. """

		mycursor, db = await self.the_database()
		mycursor.execute("UPDATE Universe SET user_ts = ? WHERE user_id = ?", (the_time, user_id))
		db.commit()
		mycursor.close()
		db.close()

	async def update_user_xp(self, user_id: int, the_xp: int) -> None:
		""" Updates the user XP in the database.
		:param user_id: The user ID.
		:param the_xp: The XP addition. """

		mycursor, db = await self.the_database()
		mycursor.execute("UPDATE Universe SET user_xp = user_xp + ? WHERE user_id = ?", (the_xp, user_id))
		db.commit()
		mycursor.close()
		db.close()


	async def check_user(self, user_id: int) -> bool:
		""" Checks whether the user exists in the Universe table.
		:param user_id: The user ID. """

		mycursor, db = await self.the_database()
		mycursor.execute("SELECT * FROM Universe WHERE user_id = ?", (user_id,))
		user = mycursor.fetchone()
		mycursor.close()
		db.close()
		return True if user else False

	async def get_user(self, user_id: int) -> List[int]:
		""" Gets a user from the Universe table.
		:param user_id: The user ID. """

		mycursor, db = await self.the_database()
		mycursor.execute("SELECT * FROM Universe WHERE user_id = ?", (user_id,))
		the_user = mycursor.fetchone()
		mycursor.close()
		db.close()
		return the_user

	async def level_up(self, user: discord.Member, channel: Union[discord.TextChannel, discord.Thread]) -> None:
		""" Checks whether the user can level up.
		:param user: The user to check.
		:param channel: The channel to send the message, if leveled up. """

		the_user = await self.get_user(user.id)
		lvl_end = int(the_user[2] ** (1 / 5))
		if the_user[1] < lvl_end:
			await self.update_user_lvl(user.id, the_user[1] + 1)
			astro = await self.get_astro(the_user[1] + 1, galaxy)
			if not await self.allowed_server(channel.guild.id):
				return
			try:
				await channel.send(f"**{user.mention} has leveled up to `{astro[0]}`!**")
			except Exception:
				pass

	async def update_user_lvl(self, user_id: int, user_lvl: int) -> None:
		""" Updates the user level.
		:param user_id: The user ID.
		:param user_lvl: The new user level. """

		mycursor, db = await self.the_database()
		mycursor.execute("UPDATE Universe SET user_lvl = ? WHERE user_id = ?", (user_lvl, user_id))
		db.commit()
		mycursor.close()
		db.close()

	# @commands.command()
	# async def profile(self, ctx, member: discord.Member = None) -> object:
	#   '''
	#   Shows your astronomical profile.
	#   '''
	#   if not member:
	#     member = ctx.author
		
	#   the_user = await self.get_user(member.id)
	#   if not the_user:
	#     return await ctx.send(f"**{member} doesn't have a profile yet!**")
	#   astro = await self.get_astro(the_user[0][1], galaxy)
	#   embed = discord.Embed(title="__Profile__", colour=member.color, timestamp=ctx.message.created_at, url=astro[1][1])
	#   embed.add_field(name="__**Rank**__", value=f"{astro[0]}.", inline=False)
	#   embed.add_field(name="__**EXP**__", value=f"{the_user[0][2]} / {((the_user[0][1]+1)**5)}.", inline=False)
	#   embed.set_thumbnail(url=astro[1][0])
	#   embed.set_footer(text=f"{member}", icon_url=member.display_avatar)
	#   #embed.set_image(url='https://cdn.discordapp.com/attachments/719020754858934294/722519380914602145/mercury.png')
	#   #{user[0][1]} / {((user[0][2]+1)**5)}."
	#   return await ctx.send(embed=embed)

	@commands.command()
	async def source(self, ctx, command: Optional[str] = None):
		""" Displays my full source code or for a specific command.
		To display the source code of a subcommand you have to separate it by
		periods, e.g. tag.create for the create subcommand of the tag command. """

		source_url = 'https://github.com/yagomichalak/astronomy-bot'
		if command is None:
			return await ctx.send(source_url)

		code_path = command.split('.')
		obj = self.client
		for cmd in code_path:
			try:
				obj = obj.get_command(cmd)
				if obj is None:
					return await ctx.send(await _(ctx, 'Could not find the command ') + cmd)
			except AttributeError:
				await ctx.send((await _(ctx, '{0.name} command has no subcommands')).format(obj))
				return

		# since we found the command we're looking for, presumably anyway, let's
		# try to access the code itself
		src = obj.callback.__code__

		if not obj.callback.__module__.startswith('discord'):
			# not a built-in command
			location = os.path.relpath(src.co_filename).replace('\\', '/')
			final_url = '<{}/tree/master/{}#L{}>'.format(source_url, location, src.co_firstlineno)
		else:
			location = obj.callback.__module__.replace('.', '/') + '.py'
			base = 'https://github.com/Pycord-Development/pycord'
			final_url = '<{}/blob/master/{}#L{}>'.format(base, location, src.co_firstlineno)

		await ctx.send(final_url)

	async def get_astro(self, level, galaxy) -> str:
		""" Gets information from an astro.
		:param level: The user level.
		:param galaxy: The galaxy. """

		i = 0
		has_planet = False
		for system in galaxy:
			for pi, p in reversed(list(system.items())):
				i += 1
				if i == level:
					has_planet = [pi, system[pi]]
					break
			if has_planet:
				break

		else:
			has_planet = [level, f"Asteroid {level}"]
		return has_planet

	@commands.command(aliases=['scoreboard', 'sb', 'rank', 'ranking'])
	async def score(self, ctx):
		""" Shows the global scoreboard, regarding the experience points. """

		users = await self.get_top_ten()
		spec_user = await self.get_user(ctx.author.id)
		scoreboard = discord.Embed(
			title='__**Astronomical Scoreboard**__',
			description='Top ten people in the world with more XP.',
			color=self.client.user.color,
			timestamp=ctx.message.created_at
		)
		scoreboard.set_thumbnail(url=ctx.guild.icon.url)
		scoreboard.set_footer(text=f"You: {spec_user[2]} XP", icon_url=ctx.author.display_avatar)

		for i, user in enumerate(users):
			member = self.client.get_user(user[0])
			scoreboard.add_field(name=f"{i+1} - __{member}__", value=f"`{user[2]}` XP", inline=False)
		await ctx.send(embed=scoreboard)

	async def get_top_ten(self) -> List[List[int]]:
		""" Gets the top ten people with XP in the Universe table. """

		mycursor, db = await self.the_database()
		mycursor.execute("SELECT * FROM Universe ORDER BY user_xp DESC limit 10")
		users = mycursor.fetchall()
		mycursor.close()
		db.close()
		return users

	@commands.command(hidden=True)
	@commands.is_owner()
	async def create_table_allowed_guilds(self, ctx) -> None:
		""" Creates the AllowedGuilds table. """

		if await self.table_allowed_guilds_exists():
			return await ctx.send("**Table __AllowedGuilds__ already exists!**")
		
		mycursor, db = await self.the_database()
		mycursor.execute("CREATE TABLE AllowedGuilds (guild_id INTEGER NOT NULL)")
		db.commit()
		mycursor.close()
		db.close()
		await ctx.send("**Table __AllowedGuilds__ created!**")

	@commands.command(hidden=True)
	@commands.is_owner()
	async def drop_table_allowed_guilds(self, ctx) -> None:
		""" Drops the AllowedGuilds table. """

		if not await self.table_allowed_guilds_exists():
			return await ctx.send("**Table __AllowedGuilds__ doesn't exist!**")
		
		mycursor, db = await self.the_database()
		mycursor.execute("DROP TABLE AllowedGuilds")
		db.commit()
		mycursor.close()
		db.close()
		await ctx.send("**Table __AllowedGuilds__ dropped!**")

	@commands.command(hidden=True)
	@commands.is_owner()
	async def reset_table_allowed_guilds(self, ctx):
		""" Resets the AllowedGuilds table. """

		if not await self.table_allowed_guilds_exists():
			return await ctx.send("**Table __AllowedGuilds__ doesn't exist yet!**")
		
		mycursor, db = await self.the_database()
		mycursor.execute("DELETE FROM AllowedGuilds")
		db.commit()
		mycursor.close()
		db.close()
		await ctx.send("**Table __AllowedGuilds__ reset!**")

	async def table_allowed_guilds_exists(self) -> bool:
		""" Checks whether the AllowedGuilds table exists in the database. """

		mycursor, db = await self.the_database()
		mycursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='AllowedGuilds'")
		exists = mycursor.fetchone()
		mycursor.close()
		db.close()
		return True if exists else False

	async def insert_allowed_server(self, gid: int) -> None:
		""" Inserts an allowed server into the database.
		:param gid: The server ID. """

		mycursor, db = await self.the_database()
		mycursor.execute("INSERT INTO AllowedGuilds (guild_id) VALUES (?)", (gid,))
		db.commit()
		mycursor.close()
		db.close()

	async def remove_allowed_server(self, gid: int) -> None:
		""" Deletes a server from the allowed guilds.
		:param gid: The server ID. """

		mycursor, db = await self.the_database()
		mycursor.execute("DELETE FROM AllowedGuilds WHERE guild_id = ?", (gid,))
		db.commit()
		mycursor.close()
		db.close()

	async def allowed_server(self, gid: int) -> bool:
		""" Checks whether a server is an allowed server.
		:param gid: The server ID. """

		mycursor, db = await self.the_database()
		mycursor.execute("SELECT * FROM AllowedGuilds WHERE guild_id = ?", (gid,))
		exists = mycursor.fetchone()
		mycursor.close()
		db.close()
		return True if exists else False

	@commands.command()
	async def random(self, ctx):
		""" Fetches a random topic from the system. """

		topic = random.choice(list(image_links))
		await self.whatIs(ctx, topic)

	@commands.command()
	@commands.cooldown(1, 10, type=commands.BucketType.user)
	async def agency(self, ctx, *, country: str = None):
		""" Shows all space agencies in the world or a specific one.
		:param country: The country of that agency. """

		if country:
			try:
				ca = space_agencies[country.title()]
			except KeyError:
				await ctx.send(f"**{ctx.author.mention}, '`{country}`' is either not a country or doesn't have a space agency!**")
			else:
				website = f"[Yes!]({ca[5]})" if ca[5] else 'No!'
				embed = discord.Embed(
				title=f"{ca[0]} __{country.title()}'s Space Agency__", description=f"**Acronym**: [{ca[1]}]({ca[3]})\n**Meaning**: {ca[2]}\n**Website?** {website}",
				timestamp=ctx.message.created_at,
				color=ctx.author.color
				)
				embed.set_footer(text=f"Requested by: {ctx.author}", icon_url=ctx.author.display_avatar)
				await ctx.send(embed=embed)

		else:
			embed = discord.Embed(
				title="__Space Agencies__",
				description='All space agencies in the world.',
				color=ctx.author.color,
				timestamp=ctx.message.created_at,
				url='https://en.wikipedia.org/wiki/List_of_government_space_agencies#List_of_space_agencies'
			)

			msg = await ctx.send(embed=embed)
			await asyncio.sleep(0.5)

			def check(reaction, user) -> bool:
				return str(reaction.message.id) == str(msg.id) and user == ctx.author and str(reaction.emoji) in ['⬅️', '➡️']

			await msg.add_reaction('⬅️')
			await msg.add_reaction('➡️')
			lensa = len(list(space_agencies))
			index = 0
			while True:
				for i in range(6):
					try:
						key = list(space_agencies)[index + i]
						value = space_agencies[key]
					except IndexError:
						break
					else:
						website = f"[Website]({value[5]})" if value[5] else ''
						embed.add_field(
						name=f"{value[0]} {key} ({value[4]})", 
						value=f"{value[2]} ([{value[1]}]({value[3]})). {website}", 
						inline=True)
						embed.set_footer(text=f"({index+1} - {index+1+i}) of {lensa}")

					await msg.edit(embed=embed)
					embed.clear_fields()
					try:
						reaction, user = await self.client.wait_for('reaction_add', timeout=60, check=check)
					except asyncio.TimeoutError:
						await msg.remove_reaction('⬅️', self.client.user)
						await msg.remove_reaction('➡️', self.client.user)
						break
					else:
						if str(reaction.emoji) == "➡️":
							await msg.remove_reaction(reaction.emoji, user)
							if index + 6 < lensa:
								index += 6
							continue
						elif str(reaction.emoji) == "⬅️":
							await msg.remove_reaction(reaction.emoji, user)
							if index > 0:
								index -= 6
							continue

	@commands.command()
	@commands.cooldown(1, 10, type=commands.BucketType.user)
	async def movie(self, ctx, *, title: str = None) -> None:
		""" Shows some movies about astronomy and space. Or a specific one.
		:param title: The name/title of the movie. """

		if title:
			all_titles = movies.keys()
			for t in all_titles:
				if str(title).lower() == str(t).lower():
					the_movie = t
					break
			else:
				return await ctx.send(f"**{ctx.author.mention}, '`{title.title()}`' is either not a movie or not a movie that's in my list!**")

			m = movies[the_movie]
			embed = discord.Embed(
				title=f"🎥 __{the_movie}__ ({m[1]})",
				description=f"{m[0]}",
				timestamp=ctx.message.created_at,
				color=ctx.author.color,
				url=m[2]
			)
			embed.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.display_avatar)
			await ctx.send(embed=embed)

		else:
			refs = ['https://spacenews.com/11-must-see-space-movies-for-anyone-serious-about-space/', 'https://www.theringer.com/2017/9/11/16285932/25-best-space-movies-ranked']
			refs = [f"[link{i+1}]({r})" for i, r in enumerate(refs)]
			embed = discord.Embed(
				title="🎥 __Movies About Astronomy and Space__ 🎥",
				description=f"Refs: {', '.join(refs)}",
				color=ctx.author.color,
				timestamp=ctx.message.created_at
			)

			msg = await ctx.send(embed=embed)

			def check(reaction, user):
				return str(reaction.message.id) == str(msg.id) and user == ctx.author and str(reaction.emoji) in ['⬅️', '➡️']

			await msg.add_reaction('⬅️')
			await msg.add_reaction('➡️')
			lenmo = len(list(movies))
			index = 0
			while True:
				for i in range(2):
					try:
						key = list(movies)[index + i]
						value = movies[key]
					except IndexError:
						break
					else:
						embed.add_field(
						name=f"{index+1+i}# {key} ({value[1]})",
						value=f"{value[0]}. [[+]]({value[2]})",
						inline=True
						)

						embed.set_footer(text=f"({index+1} - {index+1+i}) of {lenmo}")

					await msg.edit(embed=embed)
					embed.clear_fields()
					try:
						reaction, user = await self.client.wait_for('reaction_add', timeout=60, check=check)
					except asyncio.TimeoutError:
						await msg.remove_reaction('⬅️', self.client.user)
						await msg.remove_reaction('➡️', self.client.user)
						break
					else:
						if str(reaction.emoji) == "➡️":
							await msg.remove_reaction(reaction.emoji, user)
							if index + 2 < lenmo:
								index += 2
							continue
						elif str(reaction.emoji) == "⬅️":
							await msg.remove_reaction(reaction.emoji, user)
							if index > 0:
								index -= 2
							continue

	@commands.command(hidden=True, aliases=['ge', 'give_xp', 'gxp'])
	@commands.is_owner()
	async def give_exp(self, ctx, member: discord.Member = None, xp: int = None) -> None:
		""" (Owner) Gives exp to a member.
		:param member: The member to give XP.
		:param xp: the amount of xp to give to the member. """

		if not member:
			return await ctx.send("**Inform a member to give xp!**")

		if not xp:
			return await ctx.send("**Inform an amount of xp!**")

		if xp <= 0:
			return await ctx.send("**Inform an amount of xp greater than 0!**")

		if not await self.check_user(member.id):
			await self.insert_user(member.id)

		await self.update_user_xp(member.id, xp)
		await ctx.send(f"**Given {xp}XP to {member.mention}!**")

	@commands.command(hidden=True)
	@commands.is_owner()
	async def all_guilds(self, ctx) -> None:
		""" Shows all guilds, with member count. """

		info = [f"Server: {g.name}, Member count {g.member_count}" for g in self.client.guilds]
		info1 = '\n'.join(info[:35])
		info1 = f"```{info1}```"
		await ctx.send(info1)
		info2 = '\n'.join(info[35:])
		info2 = f"```{info2}```"
		await ctx.send(info2)

	@commands.command(aliases=['ra'])
	@commands.cooldown(1, 10, commands.BucketType.user)
	async def reddit(self, ctx) -> None:
		""" Shows a random post from the astronomy subreddit. """

		post_submissions = self.reddit.subreddit('astronomy').hot()
		post_to_pick = random.randint(1, 100)
		for i in range(0, post_to_pick):
			submissions = next(x for x in post_submissions if not x.stickied)

		await ctx.send(submissions.url)

	@commands.command(aliases=['wk','w', 'wiki'])
	@commands.cooldown(1, 10, type=commands.BucketType.user)
	async def wikipedia(self, ctx, *, topic: str = None) -> None:
		""" Searches something on Wikipedia.
		:param topic: The topic to search. """

		if not topic:
			return await ctx.send(f"**{ctx.author.mention}, please, inform a topic to search!**")
		try:
			result = wikipedia.summary(topic)
		except Exception as error:
			return await ctx.send("**I couldn't find anything for this topic!**")
		if (len(result) <= 2048):
			embed = discord.Embed(title=f"(Wikipedia) - __{topic.title()}__:", description=result, colour=discord.Colour.green())
			return await ctx.send(embed=embed)

		embedList = []
		n = 2048
		embedList = [result[i:i + n] for i in range(0, len(result), n)]

		for num, item in enumerate(embedList, start=1):
			if (num == 1):
				embed = discord.Embed(title=f"(Wikipedia) - __{topic.title()}__:", description=item, colour=discord.Colour.green())
				embed.set_footer(text="Page {}".format(num))
				await ctx.send(embed=embed)
			else:
				embed = discord.Embed(description=item, colour=discord.Colour.green())
				embed.set_footer(text="Page {}".format(num))
				await ctx.send(embed=embed)

	@commands.command(aliases=['cord', 'cords', 'coordinate'])
	@commands.cooldown(1, 10, type=commands.BucketType.user)
	async def coordinates(self, ctx, lat: float = None, lon: float = None):
		""" Shows some info of given coordinates.
		:param lat: The latitude.
		:param long: The longitude. """

		root = 'https://api.wheretheiss.at/v1/coordinates'
		if not lat:
			return await ctx.send("**Inform the latitude!**")

		if not lon:
			return await ctx.send("**Inform the longitude!**")

		try:
			async with self.session.get(f"{root}/{lat},{lon}") as response:
				response = await response.read()
				response = json.loads(response)
				embed = discord.Embed(
					title=f"{lat}, {lon}",
					description=f"**__Timezone ID__:** {response['timezone_id']}\n**__Offset__:** {response['offset']}\n**__Country Code__:** {response['country_code']}\n",
					color=ctx.author.color,
					timetstamp=ctx.message.created_at,
					url=response['map_url']
				)
			await ctx.send(embed=embed)
		except Exception:
			await ctx.send("**I can't work with these cords!**")


	@commands.command()
	@commands.cooldown(1, 10, type=commands.BucketType.user)
	async def iss(self, ctx):
		""" Shows information related to ISS' location. """

		root = 'https://api.wheretheiss.at/v1/satellites/25544'
		root2 = 'https://api.wheretheiss.at/v1/coordinates'
		async with self.session.get(root) as response:
			if not response.status == 200:
				return await ctx.send("**For some reason I couldn't do it! Try again later**")
		data = json.loads(await response.read())

		async with self.session.get(f"{root2}/{data['latitude']},{data['longitude']}") as response:
			if response.status == 200:
				cords = await response.read()
				cords = json.loads(cords)
				location = f"{cords['timezone_id']} ({cords['country_code']})"
				map_url = cords['map_url']
			else:
				location = '?'
				map_url = None

		embed = discord.Embed(
			title="__Internation Space Station (ISS)__",
			description="Current information about ISS' location.",
			color=ctx.author.color,
			url=map_url,
			timestamp=datetime.fromtimestamp(data['timestamp'])
		)
		embed.add_field(
			name="@ `Geographical Status`",
			value=f'''```apache\nLatitude: {data['latitude']}\nLongitude: {data['longitude']}\nAltitude: {data['altitude']}\nLocation: {location}```''', inline=False
		)
		embed.add_field(
			name="@ `General Status`",
			value=f'''```apache\nVelocity: {data['velocity']}\nVisibility: {data['visibility']}\nDaynum: {data['daynum']}\nFootprint: {data['footprint']}```''', inline=False
		)
		embed.add_field(
			name="@ `Solar status`",
			value=f'''```apache\nSolar latitude: {data['solar_lat']}\nSolar longitude: {data['solar_lon']}```''', inline=False
		)
		embed.set_footer(
			text=f"Units: {data['units']}"
		)
		await ctx.send(embed=embed)

	@commands.command(aliases=['ul', 'upcoming', 'launches'])
	async def upcoming_launches(self, ctx):
		""" Shows information about upcoming launches. """

		link = 'https://ll.thespacedevs.com/2.0.0/launch/upcoming/?format=json&limit=10&offset=10'

		async with self.session.get(link) as response:
			info = json.loads(await response.read())
			info = info['results']

		index = 0
		launch_msg = await ctx.send(embed=discord.Embed(title='🚀'))

		def check(reaction, user) -> bool:
			return str(reaction.message.id) == str(launch_msg.id) and user == ctx.author and str(reaction.emoji) in ['⬅️', '➡️']

		await asyncio.sleep(0.5)
		while True:
			lensa = len(info)
			data = info[index]
			embed = discord.Embed(
				title=f"{data['name']} ({index+1}/{lensa})",
				color=ctx.author.color
			)
			try:
				embed.add_field(
					name="__`General`__",
					value=f'''
					**Window start:** {data['window_start']}
					**Window end:** {data['window_end']}
					**Inhold:** {data['inhold']}
					**Time TBD:** {data['tbdtime']}
					**Date TBD:** {data['tbddate']}
					**Probability:** {data['probability']}
					''', inline=True)
			except Exception:
				pass
			try:
				embed.add_field(
					name="__`Launch service provider`__", 
					value=f'''
					**ID:** {data['launch_service_provider']['id']}
					**Name:** {data['launch_service_provider']['name']}
					**Type:** {data['launch_service_provider']['type']}
					''', inline=True)
			except Exception:
				pass
			try:
				embed.add_field(
					name="__`Rocket`__", 
					value=f'''
					**ID:** {data['rocket']['id']}
					**Config. ID:** {data['rocket']['configuration']['id']}
					**Name:** {data['rocket']['configuration']['name']}
					**Family:** {data['rocket']['configuration']['family']}
					**Full name:** {data['rocket']['configuration']['full_name']}
					**Variant:** {data['rocket']['configuration']['variant']}
					''', inline=True)
			except Exception:
				pass

			try:
				embed.add_field(
					name="__`Mission`__", 
					value=f'''
					**ID:** {data['mission']['id']}
					**Name:** {data['mission']['name']}
					**Type:** {data['mission']['type']}
					''',  inline=True)
				embed.description=f"```{data['mission']['description']}```"
			except Exception:
				pass

			try:
				embed.add_field(
					name="__`Pad`__", 
					value=f"""
					**ID:** {data['pad']['id']}
					**Name:** {data['pad']['name']}
					**Wiki:** [here]({data['pad']['wiki_url']})
					**Latitude:** {data['pad']['latitude']}
					**Longitude:** {data['pad']['longitude']}
					**Location ID:** {data['pad']['location']['id']}
					**Location name:** {data['pad']['location']['name']} ([map]({data['pad']['map_url']}))
					""",  inline=True)
			except Exception:
				print('a')
				pass

			if image := data['image']:
				try:
					embed.set_image(url=image)
				except Exception:
					pass

			if thumb := data['pad']['map_image']:
				try:
					embed.set_thumbnail(url=thumb)
				except Exception:
					print('a')
					pass

			await launch_msg.edit(embed=embed)
			await launch_msg.add_reaction('⬅️')
			await launch_msg.add_reaction('➡️')
			try:
				reaction, user = await self.client.wait_for('reaction_add', timeout=60, check=check)
			except asyncio.TimeoutError:
				await launch_msg.remove_reaction('⬅️', self.client.user)
				await launch_msg.remove_reaction('➡️', self.client.user)
				break
			else:
				if str(reaction.emoji) == "➡️":
					await launch_msg.remove_reaction(reaction.emoji, user)
					if index + 1 < lensa:
						index += 1
					continue
				elif str(reaction.emoji) == "⬅️":
					await launch_msg.remove_reaction(reaction.emoji, user)
					if index > 0:
						index -= 1
					continue

	@commands.command(aliases=['an'])
	@commands.cooldown(1, 10, commands.BucketType.user)
	async def astronaut(self, ctx, status: str = None, nationality: str = '', *, name: str = ''):
		""" Shows information about astronauts.
		:param status: The status ID of the astronaut(s) [Optional].
		:param nationality: The nationality of the astronaut(s) [Optional].
		:param name: The name of the astronaut(s) [Optional]. """


		statuses = {
			"1": "Active",
			"2": "Retired",
			"4": "Lost In Flight",
			"5": "Lost In Training",
			"6": "Died While In Active Service",
			"7": "Dismissed",
			"8": "Resigned during Training"
		}
		if not status in statuses:
			embed = discord.Embed(
				title="__Status Table__",
				color=ctx.author.color, 
				timestamp=ctx.message.created_at)
			msg = "**Available values:**\n```apache\n"
			for k, v in statuses.items():
				msg += f'''{k} = "{v}"\n'''
			else:
				msg += "```"
				embed.description = f"{msg}"
				return await ctx.send(embed=embed)


		root = f'https://ll.thespacedevs.com/2.0.0/astronaut/?status={status}&nationality={nationality.title()}&name={name.title()}'
		async with self.session.get(root) as response:
			if response.status == 200:
				response = json.loads(await response.read())['results']
				lenau = len(response)
				if not lenau:
					return await ctx.send("**No results found for these parameters!**")
			else:
				return await ctx.send("**I can't work with these parameters!**")

		index = 0
		the_msg = await ctx.send(embed=discord.Embed(title="👨‍🚀"))
		member = ctx.author
		def check(r, u) -> bool:
			return u == member and str(r.message.id) == str(the_msg.id) and str(r.emoji) in ['⬅️', '➡️']

		await asyncio.sleep(1)
		await the_msg.add_reaction('⬅️')
		await the_msg.add_reaction('➡️')
		while True:
			data = response[index]
			embed = discord.Embed(
				title=f"{data['name']} ({index+1}/{lenau})",
				description=f"```{data['bio']}```",
				color=ctx.author.color,
				url=data['wiki']
			)

			embed.add_field(
				name="__`Status`__", 
				value=f"""
				**Status:** {data['status']['name']} | **Status ID:** {data['status']['id']}
				**Birth Date:** {data['date_of_birth']}
				**Death Date:** {data['date_of_death']}
				**Nationality:** {data['nationality']}    
				""",
				inline=False)

			embed.add_field(
				name=f"__`General`__",
				value=f'''
				**First Flight:** {data['first_flight']}
				**Last Flight:** {data['last_flight']}
				**Twitter?** {f"[Yes!]({data['twitter']})" if data['twitter'] else 'No!'} | **Instagram?** {f"[Yes!]({data['instagram']})" if data['instagram'] else 'No!'}
				''', inline=False)

			embed.add_field(
				name=f"__`Agency`__",
				value=f"""
				**ID:** {data['agency']['id']} \t|\t **Name:** {data['agency']['name']}
				**Featured:** {data['agency']['type']} | **Country Code:** {data['agency']['country_code']}
				**Abbreviation:** {data['agency']['abbrev']} | **Administrator:** {data['agency']['administrator']}
				**Launchers:** {data['agency']['launchers']} | **Spacecraft:** {data['agency']['spacecraft']}
				**Founding Year:** {data['agency']['founding_year']} | **Parent:** {data['agency']['parent']}
				""",
				inline=False
			)
			embed.set_thumbnail(url=data['profile_image_thumbnail'])
			await the_msg.edit(embed=embed)
			try:
				reaction, user = await self.client.wait_for('reaction_add', timeout=60, check=check)
			except asyncio.TimeoutError:
				await the_msg.remove_reaction('➡️', self.client.user)
				await the_msg.remove_reaction('⬅️', self.client.user)
				break
			else:
				await the_msg.remove_reaction(reaction.emoji, user)
				if str(reaction.emoji) == "➡️":
					if index < lenau - 1:
						index += 1
					continue
				elif str(reaction.emoji) == "⬅️":
					if index > 0:
						index -= 1

	@commands.command()
	@commands.cooldown(1, 10, commands.BucketType.user)
	async def location(self, ctx, country_code: str = ''):
		""" Shows launch and landing status about some locations.
		:param country_code: The acronym of the country (e.g = USA)[Optional]. """

		root = 'https://ll.thespacedevs.com/2.0.0/location'

		async with self.session.get(f"{root}/?country_code={country_code.upper()}") as response:
			if response.status == 200:
				response = json.loads(await response.read())['results']
				lenlo = len(response)
				if not lenlo:
					return await ctx.send("**No results found for this country!**")
			else:
				return await ctx.send("**I can't work with this country code!**")

		index = 0
		the_msg = await ctx.send(embed=discord.Embed(title='🗺️'))

		def check(r, u) -> bool:
			return u == ctx.author and str(r.message.id) == str(the_msg.id) and str(r.emoji) in ['⬅️', '➡️']

		await asyncio.sleep(1)
		await the_msg.add_reaction('⬅️')
		await the_msg.add_reaction('➡️')

		while True:
			data = response[index]
			embed = discord.Embed(
			title=f"{data['name']} ({index + 1}/{lenlo})",
			description=f"""
			**Coutry Code:** {data['country_code']}
			**Total Launch Count:** {data['total_launch_count']}
			**Total Landing Count:** {data['total_landing_count']}
			""", color=ctx.author.color, timestamp=ctx.message.created_at)

			embed.set_image(url=data['map_image'])
			embed.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.display_avatar)

			await the_msg.edit(embed=embed)
			try:
				reaction, member = await self.client.wait_for('reaction_add', timeout=60, check=check)
			except asyncio.TimeoutError:
				await the_msg.remove_reaction('➡️', self.client.user)
				await the_msg.remove_reaction('⬅️', self.client.user)
			else:
				await the_msg.remove_reaction(reaction.emoji, member)
				if str(reaction.emoji) == '➡️' :
					if index < lenlo -1:
						index += 1
					continue
				elif str(reaction.emoji) == '⬅️':
					if index > 0:
						index -= 1
					continue

def setup(client: commands.Bot) -> None:
	""" Cog's setup function. """

	client.add_cog(Astronomy(client))
