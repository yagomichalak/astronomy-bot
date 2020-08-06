import discord
from discord.ext import commands
import requests
import json
import os
from datetime import datetime
import aiohttp
import io

class NASA(commands.Cog):
  '''
  A category based on NASA's API
  '''

  def __init__(self, client):
    self.client = client
    self.token = os.getenv('NASA_API_TOKEN')
    self.session = aiohttp.ClientSession(loop=client.loop)
  

  @commands.command()
  async def apod(self, ctx):
    '''
    Gets the Astronomy Picture of the Day (APOD)
    '''
    try:
      response = requests.get(f"https://api.nasa.gov/planetary/apod?api_key={self.token}")
    except requests.HTTPError as exception:
      return await ctx.send("**I couldn't do that for some reason, try again later!**")
    else:
      data = json.loads(response.text)
      try:
        embed = discord.Embed(title=data['title'], description=data['explanation'], color=ctx.author.color, timestamp=datetime.strptime(data['date'], '%Y-%m-%d'), url=data['hdurl'])
        embed.set_image(url=data['url'])
        embed.set_footer(text=data['copyright'])
      except Exception:
        return await ctx.send("**It seems we don't have one picture for today yet!**")
      else:
        await ctx.send(embed=embed)

  @commands.command(aliases=['s', 'google'])
  async def search(self, ctx, *, topic: str = None):
    '''
    Searches something on NASA's website.
    :param topic: The topic to search.
    '''

    if not topic:
      return await ctx.send("**Please, inform a topic to search!**")
    topic = topic.replace(' ', '%20')
    try:
        response = requests.get(f"https://images-api.nasa.gov/search?q={topic}")
    except requests.HTTPError as exception:
        return await ctx.send("I couldn't do that for some reason, try again later!")
    else:
        #print(dir(response.text))
        data = json.loads(response.text)
        list_data = data['collection']['items']
        if not list_data:
          return await ctx.send("**No results for this topic were found!**")
        try:
          data = list_data[0]
          ddata = data['data'][0]
          #print(data)
          embed = discord.Embed(title=ddata['title'], description=ddata['description'], color=ctx.author.color, timestamp=datetime.strptime(ddata['date_created'], '%Y-%m-%dT%H:%M:%SZ'))
          embed.set_image(url=data['links'][0]['href'].replace(' ', '%20'))
        except Exception:
          await ctx.send("**For some reason I can't use this one!**")
        else:
          await ctx.send(embed=embed)

  @commands.command()
  @commands.cooldown(1, 20, type=commands.BucketType.user)
  async def earth(self, ctx, lat: float = None, lon: float = None, dim: float = 0.025, date = datetime.utcnow().strftime('%Y-%m-%d')):
    '''
    Shows a view of the earth from a given latitude and longitude.
    :param lat: Latitude.
    :param lon: Longitude.
    :param dim: Width and hight in degrees (Default=0.025).
    :param date: The date (YYYY-MM-DD)(Default=today).
    '''
    if not lat:
      return await ctx.send("**You must inform the latitude!**")
    if not lon:
      return await ctx.send("**You must inform the longitude!**")
    root = 'https://api.nasa.gov/planetary/earth/imagery'
    try:
        link = f"{root}?lon={lon}&lat={lat}&date={date}&dim={dim}&api_key={self.token}"
        async with ctx.typing():
          async with self.session.get(link) as response:
            image = await response.read()

    except Exception as error:
      print(error)
      return await ctx.send("I couldn't do that for some reason, try again later!")
    else:
      embed = discord.Embed()
      await ctx.send("**Here's your view!!**", file=discord.File(io.BytesIO(image), 'earth.png'))

  @commands.command()
  @commands.cooldown(1, 10, type=commands.BucketType.user)
  async def mw(self, ctx):
    '''
    Gets Mars' weather from the last 7 days.
    '''
    root = "https://api.nasa.gov/insight_weather/?api_key=DEMO_KEY&feedtype=json&ver=1.0"

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

        await ctx.send(embed=embed)

  @commands.command(aliases=['ep', 'exo', 'xplanet'])
  @commands.cooldown(1, 10, type=commands.BucketType.user)
  async def exoplanet(self, ctx, index: int = None):
    '''
    Gets some information about an exoplanet, when given an index in the scope of the amount of exoplanets available in the database.
    '''
    root = 'https://exoplanetarchive.ipac.caltech.edu/cgi-bin/nstedAPI/nph-nstedAPI?table=exoplanets&format=json'
    async with ctx.typing():
      async with self.session.get(root) as response:
          data = json.loads(await response.read())
          lenex = len(data)

    if index is None:
      return await ctx.send(f"**{ctx.author.mention}, {lenex-1} exoplanets were found in our database, please, provide a number between 0 and {lenex-1}!\nEx: o!exoplanet `74`.**")

    if index < 0 or index > lenex -1:
      return await ctx.send(f"**{ctx.author.mention}, please, inform a number between 0 and {lenex}.**")


    data = data[index]
    embed = discord.Embed(
    title=f"Exoplanet -> {data['pl_hostname']}",
    description=f"Showing the exoplanet of index {index} out of {lenex}.",
    color=ctx.author.color,
    timestamp=ctx.message.created_at
    )

    embed.add_field(
        name="`Planets Columns`",
        value=f'''```apache\nPlanet Name: {data['pl_name']}\nPlanet Letter: {data['pl_letter']}\nDiscovery Method: {data['pl_discmethod']}\nControversial flag: {'yes' if data['pl_controvflag'] else 'no'}\nPlanets in the system: {data['pl_pnum']}\nOribt Period (days): {data['pl_orbper']}\nOrbit Semi-Major Axis (au): {data['pl_orbsmax']}\nEccentricity: {data['pl_orbeccen']}\nInclination (deg): {data['pl_orbincl']}\nPlanet Mass or M*sin(i) (Jupiter mass): {data['pl_bmassj']}\nPlanet Mass or M*sin(i) Provenance: {data['pl_bmassprov']}\nPlanet Radius (Jupiter radii): {data['pl_radj']}\nPlanet Density (g/cm*\*3): {data['pl_dens']}\nTTV Flag: {'yes' if data['pl_ttvflag'] else 'no'}\nKepler Field Flag: {'yes' if data['pl_kepflag'] else 'no'}\nK2 Mission Flag: {'yes' if data['pl_k2flag'] else 'no'}\nNumber of Notes: {data['pl_nnotes']}```''', inline=False
        )

    embed.add_field(
    name="`Stellar Columns`",
    value=f'''```apache\nDistance (pc): {data['st_dist']}\nOptical Magnitude:** {data['st_optmag']}\nOptical Magnitude Band: {data['st_optband']}\nEffective Temperature (K): {data['st_teff']}\nStellar Mass (solar mass): {data['st_mass']}\nG-band (Gaia) (mag): {data['gaia_gmag']}```''', inline=False
    )

    embed.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.avatar_url)
    await ctx.send(embed=embed)

def setup(client):
  client.add_cog(NASA(client))