import discord
from discord.ext import commands
import requests
import json
import os
from datetime import datetime

class NASA(commands.Cog):
  '''
  A category based on NASA's API
  '''

  def __init__(self, client):
    self.client = client
    self.token = os.getenv('NASA_API_TOKEN')
  

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
      # print(data)
      # if data['code'] == 404:
      #   return await ctx.send("**No picture for today yet!**")
      embed = discord.Embed(title=data['title'], description=data['explanation'], color=ctx.author.color, timestamp=datetime.strptime(data['date'], '%Y-%m-%d'), url=data['hdurl'])
      embed.set_image(url=data['url'])
      embed.set_footer(text=data['copyright'])
      await ctx.send(embed=embed)


def setup(client):
  client.add_cog(NASA(client))