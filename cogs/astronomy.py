import discord
from discord.ext import commands, tasks
import os
from images.all_topics import topics, image_links
import textwrap

class Astronomy(commands.Cog):

  def __init__(self, client):
    self.client = client


  @commands.Cog.listener()
  async def on_ready(self):
    print("Astronomy cog is online!")

  
  async def read_topic(self, topic: str) -> list:
    with open(f"./texts/{topic}.txt", "r") as f:
      lines = f.readlines()
      return lines


  @commands.command()
  async def listUniverse(self, ctx) -> object:
    the_universe = discord.Embed(title="__**The Universe**__", description="The universe is big, and it is worth exploring and knowing more about it.", color=discord.Color.dark_purple(), timestamp=ctx.message.created_at)
    the_universe.set_author(name="The Big Bang", url=ctx.author.avatar_url)

    the_universe.add_field(name="__**Available topics:**__", value=topics, inline=True)
    the_universe.set_image(url='https://cdn.discordapp.com/attachments/719020754858934294/719022762743824445/space2.png')
    the_universe.set_thumbnail(url='https://cdn.discordapp.com/attachments/719020754858934294/719022762743824445/space2.png')
    the_universe.set_footer(text=ctx.guild.name, icon_url=ctx.guild.icon_url)

    return await ctx.send(embed=the_universe)


  @commands.command()
  async def whatIs(self, ctx, topic: str = None):
    if not topic:
      return await ctx.send("**Please, inform a topic!**")
    
    if not topic.title() in topics:
      return await ctx.send(f"**{topic.title()} is not a topic that I cover!**")

    result = await self.read_topic(topic.title())
    count = 0
    if count == 0:
      embed = discord.Embed(title=f"({topic.title()})",colour=discord.Colour.dark_purple(), timestamp=ctx.message.created_at)
      embed.set_author(name=ctx.guild.name, icon_url=ctx.guild.icon_url)
      embed.add_field(name="__**Definition:**__", value=f"```{' '.join(result)}```", inline=False)
      embed.set_thumbnail(url=image_links[topic.title()])
      embed.set_image(url=image_links[topic.title()])
      embed.set_footer(text=f"Requested by: {ctx.author.name}", icon_url=ctx.author.avatar_url)
      await ctx.send(embed=embed)

def setup(client):
  client.add_cog(Astronomy(client))