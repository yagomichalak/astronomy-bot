import discord
from discord import slash_command, Option
from discord.ext import commands

import requests
import json
import os
from datetime import datetime
import aiohttp
import io
from typing import Optional, List
from extra import utils
from extra.views import PaginatorView

TEST_GUILDS: List[int] = [int(os.getenv('SERVER_ID'))]

class NASA(commands.Cog):
	""" A category based on NASA's API """

	def __init__(self, client: commands.Bot) -> None:
		""" Class init method. """

		self.client = client
		self.token = os.getenv('NASA_API_TOKEN')
		self.session = aiohttp.ClientSession(loop=client.loop)

	@commands.Cog.listener()
	async def on_ready(self) -> None:
		""" Tells when the cog is ready to go. """

		print('NASA cog is online!')
  
	@slash_command()
	async def apod(self, ctx) -> None:
		""" Gets the Astronomy Picture of the Day (APOD). """

		await ctx.defer()

		try:
			response = requests.get(f"https://api.nasa.gov/planetary/apod?api_key={self.token}")
		except requests.HTTPError:
			return await ctx.respond("**I couldn't do that for some reason, try again later!**")
		else:
			data = json.loads(response.text)
		try:
			embed = discord.Embed(title=data['title'], description=data['explanation'], color=ctx.author.color, timestamp=datetime.strptime(data['date'], '%Y-%m-%d'))
			if hdurl := data.get('hdurl'):
				embed.url=hdurl
				embed.set_image(url=data['url'])
			if copyright := data['copyright']:
				embed.set_footer(text=copyright)
		except Exception:
			pass

		try:
			await ctx.respond(embed=embed)
		except Exception:
			return await ctx.respond("**It seems we don't have a picture for today yet!**")

	@slash_command()
	async def search(self, ctx, 
		topic: Option(str, name="topic", description="The topic to search.", required=True)
	) -> None:
		""" Searches something on NASA's website. """

		await ctx.defer()

		topic = topic.replace(' ', '%20')

		try:
			response = requests.get(f"https://images-api.nasa.gov/search?q={topic}")
		except requests.HTTPError:
			return await ctx.respond("I couldn't do that for some reason, try again later!")
		else:
			data = json.loads(response.text)
			list_data = data['collection']['items']
			if not list_data:
				return await ctx.respond("**No results for this topic were found!**")
			try:
				data = list_data[0]
				ddata = data['data'][0]
				embed = discord.Embed(title=ddata['title'], description=ddata['description'], color=ctx.author.color, timestamp=datetime.strptime(ddata['date_created'], '%Y-%m-%dT%H:%M:%SZ'))
				embed.set_image(url=data['links'][0]['href'].replace(' ', '%20'))
			except Exception:
				await ctx.respond("**For some reason I can't use this one!**")
			else:
				await ctx.respond(embed=embed)

	@slash_command(guild_ids=TEST_GUILDS)
	@commands.cooldown(1, 20, type=commands.BucketType.user)
	@utils.not_ready()
	async def earth(self, ctx, 
		lat: Option(float, name="latitude", description="The latitude of the coordinates.", required=True), 
		lon: Option(float, name="longitude", description="The longitude of the coordinates.", required=True), 
		dim: Option(float, name="dimension", description="The dimension of the coordinates.", default=0.025),
		date: Option(str, name="date", description="The data the picture was taken. (YYYY-MM-DD)", default=datetime.utcnow().strftime('%Y-%m-%d'))
	) -> None:
		""" Shows a view of the earth from a given latitude and longitude. """

		await ctx.defer()

		root = 'https://api.nasa.gov/planetary/earth/imagery'
		try:
			link = f"{root}?lon={lon}&lat={lat}&date={date}&dim={dim}&api_key={self.token}"
			async with self.session.get(link) as response:
				image = await response.read()

		except Exception as error:
			print(error)
			return await ctx.respond("I couldn't do that for some reason, try again later!")
		else:
			await ctx.respond("**Here's your view!!**", file=discord.File(io.BytesIO(image), 'earth.png'))

	@slash_command(name="mars_weather", guild_ids=TEST_GUILDS)
	@commands.cooldown(1, 10, type=commands.BucketType.user)
	@utils.not_ready()
	async def _mars_weather(self, ctx) -> None:
		""" Gets Mars' weather from the last 7 days. """

		await ctx.defer()
		root = f"https://api.nasa.gov/insight_weather/?api_key={self.token}&feedtype=json&ver=1.0"

		try:
			response = requests.get(root)
		except Exception as error:
			print(error)
		else:
			all_data = json.loads(response.text)
			days = list(all_data.keys())[:-2]
			embed = discord.Embed(
				title="Mars Weather (F°)",
				description="Mars' air temperature of the last 7 days", 
				color=ctx.author.color)
			for day in days:
				sol = day
				day = all_data[day]
				embed.add_field(name=f":sunny: Sol ({sol})", value=f"```ini\n[Max]: {day['AT']['mx']}\n[Min]: {day['AT']['mn']}\n[First UTC]: {day['First_UTC']}\n[Last UTC]: {day['Last_UTC']}```", inline=True)
				return await ctx.respond(embed=embed)
			else:
				await ctx.respond(content="**It looks like we don't have the last 7 days Mars Weather... Sorry!**")

	@slash_command(guild_ids=TEST_GUILDS)
	@commands.cooldown(1, 10, type=commands.BucketType.user)
	@utils.not_ready()
	async def exoplanet(self, ctx, 
		index: Option(int, name="index", description="The index of the exoplanet.", required=False)
	) -> None:
		""" Gets some info about an exoplanet. """

		await ctx.defer()

		root = 'https://exoplanetarchive.ipac.caltech.edu/TAP/sync?query=select+*+from+ps&format=json'
		async with self.session.get(root) as response:
			json_data = await response.read()
			data = json.loads(json_data[537:])
			lenex = len(data)		

		if index is None:
			return await ctx.respond(f"**{ctx.author.mention}, {lenex-1} exoplanets were found in our database, please, provide a number between 0 and {lenex-1}!\nEx: o!exoplanet `74`.**")

		if index < 0 or index > lenex -1:
			return await ctx.respond(f"**{ctx.author.mention}, please, inform a number between 0 and {lenex-1}.**")

		current_time = await utils.get_time_now()
		data = data[index]
		embed = discord.Embed(
			title=f"Exoplanet -> {data['pl_hostname']}",
			description=f"Showing the exoplanet of index {index} out of {lenex}.",
			color=ctx.author.color,
			timestamp=current_time
		)

		embed.add_field(
			name="`Planets Columns`",
			value=f'''```apache\nPlanet Name: {data['pl_name']}\nPlanet Letter: {data['pl_letter']}\nDiscovery Method: {data['pl_discmethod']}\nControversial flag: {'yes' if data['pl_controvflag'] else 'no'}\nPlanets in the system: {data['pl_pnum']}\nOribt Period (days): {data['pl_orbper']}\nOrbit Semi-Major Axis (au): {data['pl_orbsmax']}\nEccentricity: {data['pl_orbeccen']}\nInclination (deg): {data['pl_orbincl']}\nPlanet Mass or M*sin(i) (Jupiter mass): {data['pl_bmassj']}\nPlanet Mass or M*sin(i) Provenance: {data['pl_bmassprov']}\nPlanet Radius (Jupiter radii): {data['pl_radj']}\nPlanet Density (g/cm*\*3): {data['pl_dens']}\nTTV Flag: {'yes' if data['pl_ttvflag'] else 'no'}\nKepler Field Flag: {'yes' if data['pl_kepflag'] else 'no'}\nK2 Mission Flag: {'yes' if data['pl_k2flag'] else 'no'}\nNumber of Notes: {data['pl_nnotes']}```''', inline=False
			)

		embed.add_field(
			name="`Stellar Columns`",
			value=f'''```apache\nDistance (pc): {data['st_dist']}\nOptical Magnitude:** {data['st_optmag']}\nOptical Magnitude Band: {data['st_optband']}\nEffective Temperature (K): {data['st_teff']}\nStellar Mass (solar mass): {data['st_mass']}\nG-band (Gaia) (mag): {data['gaia_gmag']}```''', inline=False
		)

		embed.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.display_avatar)
		await ctx.respond(embed=embed)

def setup(client: commands.Bot) -> None:
	""" Cog's setup function. """

	client.add_cog(NASA(client))