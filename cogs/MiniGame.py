import discord
from discord.ext import commands
import asyncio

class MiniGame(commands.Cog):
  '''
  Minigame related commands.
  '''

  def __init__(self, client):
    self.client = client

  @commands.Cog.listener()
  async def on_ready(self):
    print('MiniGame cog is online!')

  @commands.group(aliases=['p', 'game'])
  async def play(self, ctx):
    '''
    Plays a game.
    '''
    if ctx.invoked_subcommand is None:
      games = ['space_traveling']
      embed = discord.Embed(
        title="__**Let's play!**__",
        description=f"What do you wanna play?\n\n**->** {', '.join(games)}",
        color=ctx.author.color
        )
      embed.set_footer(text=f"Ex: o!play game_name")
      await ctx.send(embed=embed)

  @play.command(aliases=['st', 'space'])
  @commands.cooldown(1, 600, type=commands.BucketType.user)
  async def space_traveling(self, ctx):

    def check(reaction, user):
        return user == ctx.author and str(reaction.emoji) in '1️⃣2️⃣'
    msg = await ctx.send(embed=discord.Embed(title='🎮'))
    await self.make_embed(ctx, msg, '''You started your journey in space and right after that you see two paths.

Would you like to go **left** or **right**?''')
    await msg.add_reaction('1️⃣')
    await msg.add_reaction('2️⃣')
    reaction, user = await self.get_reaction_response(ctx.author, check, msg)
    if reaction and reaction.emoji == '1️⃣':
      await self.make_embed(ctx, msg, '''You went to the left with your spaceship and saw what apparently is a black hole.

-> **Go straight** to the black hole or **go around** it in a safe distance?
''')
      reaction, user = await self.get_reaction_response(ctx.author, check, msg)
      if reaction and reaction.emoji == '1️⃣':
        await self.make_embed(ctx, msg, '''You went straight to the black hole, you and your spaceship distorted like modeling clay and no traces of you were left behind. Game over.
''')
        return
      elif reaction and reaction.emoji == '2️⃣':
        await self.make_embed(ctx, msg, '''You went around the black hole in a safe distance and continued traveling. You saw two brown undefined astros, a tiny one on your left and an astonishing big one on your right.

-> **Go left** or **go right**?
''')
        reaction, user = await self.get_reaction_response(ctx.author, check, msg)
        if reaction and reaction.emoji == '1️⃣':
          await self.make_embed(ctx, msg, '''You went to the left, in the direction of that tiny brown undefined astro and realized that it wasn't actually that small, in fact, it was an asteroid that looked even bigger than the other astro and it was increasing its size every second, because that thing was going in your direction at full speed. You immediately panicked and before you said your last word, that asteroid struck and smashed you and your spaceship like an 18-wheeler truck would smash a branch of a tree. One thing is for sure, your last word started with an F. Game over.''')
          return
        elif reaction and reaction.emoji == '2️⃣':
          await self.make_embed(ctx, msg, '''You went to the right with your spaceship, in the direction of that big brown astro, that happened to be a free-floating planet with a brown back, nonetheless it was warm and had water enough to sustain life. Luckily, you found another traveler that happened to be of your opposite gender, you both agreed that it was time to reproduce for the good of humanity. Congratulations, you won!''')
          # Won
    elif reaction and reaction.emoji == '2️⃣':
      await self.make_embed(ctx, msg, '''You went to the right with your spaceship and found a new star system.

-> **Go in there** or **travel past by it**?''')
      reaction, user = await self.get_reaction_response(ctx.author, check, msg)
      if reaction and reaction.emoji == '1️⃣':
        await self.make_embed(ctx, msg, '''You went into the star system, but its orbit was so weird that it changed its rotation frequently, your spaceship got attracted by that star system's inconsistent gravitational orbit and rapidly found yourself flying straight into its star and melted like cheese in the summer of Mexico. Game over.''')
        return
      elif reaction and reaction.emoji == '2️⃣':
        await self.make_embed(ctx, msg, '''You traveled past that star system and found another one on your right, but there was nothing but emptiness on your left.

-> Go **left** or go **right**?
''')
        reaction, user = await self.get_reaction_response(ctx.author, check, msg)
        if reaction and reaction.emoji == '1️⃣':
          await self.make_embed(ctx, msg, '''You went to the left, but as expected, there was nothing but emptiness. You noticed that you wouldn't find anything more than this and tried to turn around and go back, however your ship didn't make its way back because it ran out of gas. You found yourself stuck in the middle of nowhere with no gas and 13 days worth of food... you tasted death each bite of your food. Game over.''')
          return
        elif reaction and reaction.emoji == '2️⃣':
          await self.make_embed(ctx, msg, '''You went to the right and entered in that star system, you got signals coming from one of its planets, you then went closer to it and decided to land on it, talking to the people that were there, you discovered that it was a planet called Earth and its star system had a star called Sun. People were so surprised with your arrive, because you seemed to be way more advanced in technology than those people. Considering that you were from another galaxy, you didn't speak their dominant language, that was called English, so you had to communicate with them through pictograms, onomatopoeia and mimic. You helped them for years, telling them your discoveries, giving them a bit of your knowledge acquired throughout your career, long journeys and endless researches, and you eventually learned English as well. Congratulations, you passed!''')
          # Won


  async def get_reaction_response(self, member, check, msg):
    try:
      reaction, user = await self.client.wait_for('reaction_add', timeout=60.0, check=check)
    except asyncio.TimeoutError:
      timeout = discord.Embed(title='Timeout',
                  description='You took too long to answer the question, try again later.',
                  colour=discord.Colour.dark_red())
      await msg.edit(embed=timeout)
      return None, None
    else:
      await msg.remove_reaction(reaction.emoji, user)
      return reaction, user

  async def make_embed(self, ctx, msg, description: str):
    space_embed = discord.Embed(
      title='__**Space Traveling**__', 
      description=description,
      color=ctx.author.color,
      timestamp=ctx.message.created_at
      )
    space_embed.set_thumbnail(url=ctx.author.avatar_url)
    await msg.edit(embed=space_embed)

    

def setup(client):
  client.add_cog(MiniGame(client))