import discord
from discord.ext import commands, tasks
from discord.utils import escape_mentions
from discord import slash_command, Option, OptionChoice

from images.all_topics import topics, image_links, galaxy
from images.agencies import space_agencies
from images.movies import movies

from extra import utils
from extra.views import PaginatorView

from datetime import datetime
import os
import sqlite3
import json
import praw
import asyncio
import random
import wikipedia
import aiohttp
from typing import List, Dict, Any, Union

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

	@slash_command(name="list_universe")
	@commands.cooldown(1, 10, type=commands.BucketType.user)
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

	@slash_command()
	@commands.cooldown(1, 10, type=commands.BucketType.user)
	async def what_is(self, ctx, 
		topic: Option(str, name="topic", description="The topic to show.", required=True)
	 ) -> None:
		""" Shows some information about the given topic. """

		await ctx.defer()
		
		if not topic.title() in topics:
			return await ctx.respond(f"**`{topic.title()}` is not a topic that I cover!**")

		current_time = await utils.get_time_now()
		result = await self.read_topic(topic.title())
		links = image_links[topic.title()]
		embed = discord.Embed(
			title=f"({topic.title()})",
			color=discord.Color.dark_purple(),
			timestamp=current_time,
			url=links[1]
		)
		embed.set_author(name=ctx.guild.name, icon_url=ctx.guild.icon.url)
		embed.add_field(name="__**Definition:**__", value=f"```{' '.join(result)}```", inline=False)
		embed.set_thumbnail(url=links[0])
		embed.set_image(url=links[0])
		embed.set_footer(text=f"Requested by: {ctx.author.name}", icon_url=ctx.author.display_avatar)
		await ctx.respond(embed=embed)

	@slash_command()
	@commands.cooldown(1, 10, type=commands.BucketType.user)
	async def random(self, ctx):
		""" Fetches a random topic from the system. """

		topic = random.choice(list(image_links))
		await self.what_is(ctx, topic)

	@slash_command()
	@commands.cooldown(1, 10, type=commands.BucketType.user)
	async def agency(self, ctx, 
		country: Option(str, name="country", description="The country of that agency.", required=False)
	) -> None:
		""" Shows all space agencies in the world or a specific one. """

		await ctx.defer()
		current_time = await utils.get_time_now()

		if country:
			try:
				ca = space_agencies[country.title()]
			except KeyError:
				await ctx.respond(f"**{ctx.author.mention}, '`{country}`' is either not a country or doesn't have a space agency!**")
			else:
				website = f"[Yes!]({ca[5]})" if ca[5] else 'No!'
				embed = discord.Embed(
					title=f"{ca[0]} __{country.title()}'s Space Agency__", description=f"**Acronym**: [{ca[1]}]({ca[3]})\n**Meaning**: {ca[2]}\n**Website?** {website}",
					timestamp=current_time,
					color=ctx.author.color
				)
				embed.set_footer(text=f"Requested by: {ctx.author}", icon_url=ctx.author.display_avatar)
				await ctx.respond(embed=embed)

		else:

			additional = {
				'client': self.client,
				'change_embed': self.make_agency_embed
			}
			view = PaginatorView(list(movies.items()), increment=6, **additional)
			embed = await view.make_embed(ctx.author)
			await ctx.respond(embed=embed, view=view)

	async def make_agency_embed(self, req: str, member: Union[discord.Member, discord.User], search: str, example: Any,
		offset: int, lentries: int, entries: Dict[str, Any], title: str = None, result: str = None) -> discord.Embed:
		""" Makes a paginated embed for the agency command. """

		current_time = await utils.get_time_now()

		embed = discord.Embed(
			title="__Space Agencies__",
			description='All space agencies in the world.',
			color=member.color,
			timestamp=current_time,
			url='https://en.wikipedia.org/wiki/List_of_government_space_agencies#List_of_space_agencies'
		)

		for i in range(6):
			try:
				key = list(space_agencies)[offset -1 +i]
				value = space_agencies[key]
			except IndexError:
				break
			else:
				website = f"[Website]({value[5]})" if value[5] else ''
				embed.add_field(
					name=f"{value[0]} {key} ({value[4]})", 
					value=f"{value[2]} ([{value[1]}]({value[3]})). {website}", 
					inline=True)
				embed.set_footer(text=f"({offset} - {offset+i}) of {lentries}")


		return embed

	@slash_command()
	@commands.cooldown(1, 10, type=commands.BucketType.user)
	async def movie(self, ctx, title: Option(str, name="title", description="The name/title of the movie.", required=False)) -> None:
		""" Shows some movies about astronomy and space. Or a specific one. """

		await ctx.defer()
		current_time = await utils.get_time_now()

		if title:
			all_titles = movies.keys()
			for t in all_titles:
				if str(title).lower() == str(t).lower():
					the_movie = t
					break
			else:
				return await ctx.respond(f"**{ctx.author.mention}, '`{title.title()}`' is either not a movie or not a movie that's in my list!**")

			m = movies[the_movie]
			embed = discord.Embed(
				title=f"🎥 __{the_movie}__ ({m[1]})",
				description=f"{m[0]}",
				timestamp=current_time,
				color=ctx.author.color,
				url=m[2]
			)
			embed.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.display_avatar)
			await ctx.respond(embed=embed)

		else:
			refs = ['https://spacenews.com/11-must-see-space-movies-for-anyone-serious-about-space/', 'https://www.theringer.com/2017/9/11/16285932/25-best-space-movies-ranked']
			refs = [f"[link{i+1}]({r})" for i, r in enumerate(refs)]

			additional = {
				'client': self.client,
				'result': ', '.join(refs),
				'change_embed': self.make_movie_embed
			}
			view = PaginatorView(list(movies.items()), **additional)
			embed = await view.make_embed(ctx.author)
			await ctx.respond(embed=embed, view=view)

			
	async def make_movie_embed(self, req: str, member: Union[discord.Member, discord.User], search: str, example: Any,
		offset: int, lentries: int, entries: Dict[str, Any], title: str = None, result: str = None) -> discord.Embed:
		""" Makes a paginated embed for the movie command. """

		current_time = await utils.get_time_now()

		embed = discord.Embed(
			title="🎥 __Movies About Astronomy and Space__ 🎥",
			description=f"Refs: {result}",
			color=member.color,
			timestamp=current_time
		)
		entries = dict(entries)
		try:
			key = list(entries)[offset - 1]
			value = entries[key]
		except IndexError:
			pass
		else:
			embed.add_field(
				name=f"{offset}# {key} ({value[1]})",
				value=f"{value[0]}. [[+]]({value[2]})",
				inline=True
			)

			embed.set_footer(text=f"{offset}/{lentries}")

		return embed

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

	@slash_command()
	@commands.cooldown(1, 10, commands.BucketType.user)
	async def reddit(self, ctx) -> None:
		""" Shows a random post from the astronomy subreddit. """

		await ctx.defer()
		post_submissions = self.reddit.subreddit('astronomy').hot()
		post_to_pick = random.randint(1, 100)
		for i in range(0, post_to_pick):
			submissions = next(x for x in post_submissions if not x.stickied)

		await ctx.respond(submissions.url)

	@slash_command()
	@commands.cooldown(1, 10, type=commands.BucketType.user)
	async def coordinates(self, ctx, 
		lat: Option(float, name="latitude", description="The latitude.", required=True), 
		lon: Option(float, name="longitude", description="The longitude", required=True)
		) -> None:
		""" Shows some info about the given coordinates. """

		await ctx.defer()
		root = 'https://api.wheretheiss.at/v1/coordinates'
		current_time = await utils.get_time_now()

		try:
			async with self.session.get(f"{root}/{lat},{lon}") as response:
				response = await response.read()
				response = json.loads(response)
				embed = discord.Embed(
					title=f"{lat}, {lon}",
					description=f"**__Timezone ID__:** {response['timezone_id']}\n**__Offset__:** {response['offset']}\n**__Country Code__:** {response['country_code']}\n",
					color=ctx.author.color,
					timestamp=current_time,
					url=response['map_url']
				)
			await ctx.respond(embed=embed)
		except Exception as e:
			print(e)
			await ctx.respond("**I can't work with these cords!**")

	@slash_command()
	@commands.cooldown(1, 10, type=commands.BucketType.user)
	async def iss(self, ctx):
		""" Shows information related to ISS' location. """

		await ctx.defer()
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
		await ctx.respond(embed=embed)

	@slash_command()
	@commands.cooldown(1, 10, type=commands.BucketType.user)
	async def upcoming_launches(self, ctx):
		""" Shows information about upcoming launches. """

		await ctx.defer()
		link = 'https://ll.thespacedevs.com/2.0.0/launch/upcoming/?format=json&limit=10&offset=10'

		async with self.session.get(link) as response:
			info = json.loads(await response.read())
			info = info['results']

		additional = {
			'client': self.client,
			'change_embed': self.make_upcoming_launches_embed
		}
		view = PaginatorView(info, **additional)
		embed = await view.make_embed(ctx.author)
		await ctx.respond(embed=embed, view=view)

	async def make_upcoming_launches_embed(self, req: str, member: Union[discord.Member, discord.User], search: str, example: Any,
		offset: int, lentries: int, entries: Dict[str, Any], title: str = None, result: str = None) -> discord.Embed:
		""" Makes a paginated embed for the upcoming_launches command. """
	
		embed = discord.Embed(
			title=f"{example['name']} ({offset}/{lentries})",
			color=member.color
		)
		try:
			embed.add_field(
				name="__`General`__",
				value=f'''
				**Window start:** {example['window_start']}
				**Window end:** {example['window_end']}
				**Inhold:** {example['inhold']}
				**Time TBD:** {example['tbdtime']}
				**Date TBD:** {example['tbddate']}
				**Probability:** {example['probability']}
				''', inline=True)
		except Exception:
			pass
		try:
			embed.add_field(
				name="__`Launch service provider`__", 
				value=f'''
				**ID:** {example['launch_service_provider']['id']}
				**Name:** {example['launch_service_provider']['name']}
				**Type:** {example['launch_service_provider']['type']}
				''', inline=True)
		except Exception:
			pass
		try:
			embed.add_field(
				name="__`Rocket`__", 
				value=f'''
				**ID:** {example['rocket']['id']}
				**Config. ID:** {example['rocket']['configuration']['id']}
				**Name:** {example['rocket']['configuration']['name']}
				**Family:** {example['rocket']['configuration']['family']}
				**Full name:** {example['rocket']['configuration']['full_name']}
				**Variant:** {example['rocket']['configuration']['variant']}
				''', inline=True)
		except Exception:
			pass

		try:
			embed.add_field(
				name="__`Mission`__", 
				value=f'''
				**ID:** {example['mission']['id']}
				**Name:** {example['mission']['name']}
				**Type:** {example['mission']['type']}
				''',  inline=True)
			embed.description=f"```{example['mission']['description']}```"
		except Exception:
			pass

		try:
			embed.add_field(
				name="__`Pad`__", 
				value=f"""
				**ID:** {example['pad']['id']}
				**Name:** {example['pad']['name']}
				**Wiki:** [here]({example['pad']['wiki_url']})
				**Latitude:** {example['pad']['latitude']}
				**Longitude:** {example['pad']['longitude']}
				**Location ID:** {example['pad']['location']['id']}
				**Location name:** {example['pad']['location']['name']} ([map]({example['pad']['map_url']}))
				""",  inline=True)
		except Exception:
			pass

		if image := example['image']:
			try:
				embed.set_image(url=image)
			except Exception:
				pass

		if thumb := example['pad']['map_image']:
			try:
				embed.set_thumbnail(url=thumb)
			except Exception:
				pass

		return embed

	@slash_command()
	@commands.cooldown(1, 10, commands.BucketType.user)
	async def astronaut(self, ctx, 
		status: Option(str, name="status", description="The status of the astronaut(s).", required=True, choices=[
			OptionChoice(name="Active", value="1"),
			OptionChoice(name="Retired", value="2"),
			OptionChoice(name="Lost In Flight", value="4"),
			OptionChoice(name="Lost In Training", value="5"),
			OptionChoice(name="Died While In Active Service", value="6"),
			OptionChoice(name="Dismissed", value="7"),
			OptionChoice(name="Resigned during Training", value="8")
		], default=''), 
		nationality: Option(str, name="nationality", description="The nationality of the astronaut(s).", required=False, default=''),
		name: Option(str, name="name", description="The name of the astronaut(s).", required=False, default='')
	) -> None:
		""" Shows information about astronauts. """

		await ctx.defer()

		root = f'https://ll.thespacedevs.com/2.0.0/astronaut/?status={status}&nationality={nationality.title()}&name={name.title()}'
		async with self.session.get(root) as response:
			if response.status == 200:
				response = json.loads(await response.read())['results']
				lenau = len(response)
				if not lenau:
					return await ctx.respond("**No results found for these parameters!**")
			else:
				return await ctx.respond("**I can't work with these parameters!**")

		additional = {
			'client': self.client,
			'req': root,
			'change_embed': self.make_astronaut_embed
		}
		view = PaginatorView(response, **additional)
		embed = await view.make_embed(ctx.author)
		await ctx.respond(embed=embed, view=view)

	async def make_astronaut_embed(self, req: str, member: Union[discord.Member, discord.User], search: str, example: Any,
		offset: int, lentries: int, entries: Dict[str, Any], title: str = None, result: str = None) -> discord.Embed:
		""" Makes a paginated embed for the astronaut command. """

		current_time = await utils.get_time_now()

		embed = discord.Embed(
			title=f"{example['name']} ({offset}/{lentries})",
			description=f"```{example['bio']}```",
			color=member.color,
			timestamp=current_time,
			url=example['wiki']
		)

		embed.add_field(
			name="__`Status`__", 
			value=f"""
			**Status:** {example['status']['name']} | **Status ID:** {example['status']['id']}
			**Birth Date:** {example['date_of_birth']}
			**Death Date:** {example['date_of_death']}
			**Nationality:** {example['nationality']}    
			""",
			inline=False)

		embed.add_field(
			name=f"__`General`__",
			value=f'''
			**First Flight:** {example['first_flight']}
			**Last Flight:** {example['last_flight']}
			**Twitter?** {f"[Yes!]({example['twitter']})" if example['twitter'] else 'No!'} | **Instagram?** {f"[Yes!]({example['instagram']})" if example['instagram'] else 'No!'}
			''', inline=False)

		embed.add_field(
			name=f"__`Agency`__",
			value=f"""
			**ID:** {example['agency']['id']} \t|\t **Name:** {example['agency']['name']}
			**Featured:** {example['agency']['type']} | **Country Code:** {example['agency']['country_code']}
			**Abbreviation:** {example['agency']['abbrev']} | **Administrator:** {example['agency']['administrator']}
			**Launchers:** {example['agency']['launchers']} | **Spacecraft:** {example['agency']['spacecraft']}
			**Founding Year:** {example['agency']['founding_year']} | **Parent:** {example['agency']['parent']}
			""",
			inline=False
		)
		embed.set_thumbnail(url=example['profile_image_thumbnail'])
		return embed

	@slash_command()
	@commands.cooldown(1, 10, commands.BucketType.user)
	async def location(self, ctx, 
		country_code: Option(str, name="country_code", description="The country acronym (e.g = USA)", required=False, default='')
	) -> None:
		""" Shows launch and landing status about some locations. """

		await ctx.defer()
		root = 'https://ll.thespacedevs.com/2.0.0/location'

		async with self.session.get(f"{root}/?country_code={country_code.upper()}") as response:
			if response.status == 200:
				response = json.loads(await response.read())['results']
				lenlo = len(response)
				if not lenlo:
					return await ctx.respond("**No results found for this country!**")
			else:
				return await ctx.respond("**I can't work with this country code!**")

		additional = {
			'client': self.client,
			'req': root,
			'change_embed': self.make_location_embed
		}
		view = PaginatorView(response, **additional)
		embed = await view.make_embed(ctx.author)
		await ctx.respond(embed=embed, view=view)

	async def make_location_embed(self, req: str, member: Union[discord.Member, discord.User], search: str, example: Any,
		offset: int, lentries: int, entries: Dict[str, Any], title: str = None, result: str = None) -> discord.Embed:
		""" Makes a paginated embed for the location command. """

		current_time = await utils.get_time_now()

		embed = discord.Embed(
		title=f"{example['name']} ({offset}/{lentries})",
		description=f"""
		**Coutry Code:** {example['country_code']}
		**Total Launch Count:** {example['total_launch_count']}
		**Total Landing Count:** {example['total_landing_count']}
		""", color=member.color, timestamp=current_time)

		embed.set_image(url=example['map_image'])
		embed.set_footer(text=f"Requested by {member}", icon_url=member.display_avatar)

		return embed

def setup(client: commands.Bot) -> None:
	""" Cog's setup function. """

	client.add_cog(Astronomy(client))
