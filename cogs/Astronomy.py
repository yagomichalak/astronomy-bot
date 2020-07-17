import discord
from discord.ext import commands, tasks
import os
from images.all_topics import topics, image_links, galaxy
import textwrap
import sqlite3
from datetime import datetime
import random
from images.agencies import space_agencies
import asyncio
from images.movies import movies

class Astronomy(commands.Cog):
  '''
  All you need to know regarding astronomy.
  '''

  def __init__(self, client):
    self.client = client


  @commands.Cog.listener()
  async def on_ready(self):
    print("Astronomy cog is online!")
  
  @commands.Cog.listener()
  async def on_message(self, message):
    if message.author.bot:
      return
    
    if not await self.table_exists():
      return

    epoch = datetime.utcfromtimestamp(0)
    time_xp = (datetime.utcnow() - epoch).total_seconds()

    if not await self.check_user(message.author.id):
      await self.insert_user(message.author.id)

    await self.update_data(message.author, time_xp, message.channel)

  async def read_topic(self, topic: str) -> list:
    with open(f"./texts/{topic}.txt", "r") as f:
      lines = f.readlines()
      return lines


  @commands.command(aliases=['lu', 'listuniverse', 'topics'])
  async def listUniverse(self, ctx) -> object:
    '''
    Shows all topics available to see.
    '''
    the_universe = discord.Embed(title="__**The Universe**__", description="The universe is big, and it is worth exploring and knowing more about it.", color=discord.Color.dark_purple(), timestamp=ctx.message.created_at)
    the_universe.set_author(name="The Big Bang", url=ctx.author.avatar_url)

    the_universe.add_field(name="__**Available topics:**__", value=f"```{', '.join(sorted(topics))}```", inline=True)
    the_universe.set_image(url='https://cdn.discordapp.com/attachments/719020754858934294/719022762743824445/space2.png')
    the_universe.set_thumbnail(url='https://cdn.discordapp.com/attachments/719020754858934294/719022762743824445/space2.png')
    the_universe.set_footer(text=ctx.guild.name, icon_url=ctx.guild.icon_url)

    return await ctx.send(embed=the_universe)


  @commands.command(aliases=['wi', 'whatis', 'whats'])
  async def whatIs(self, ctx, topic: str = None) -> None:
    '''
    Shows some information about the given topic.
    :param topic: The topic to show.
    '''
    if not topic:
      return await ctx.send("**Please, inform a topic!**")
    
    if not topic.title() in topics:
      return await ctx.send(f"**`{topic.title()}` is not a topic that I cover!**")

    result = await self.read_topic(topic.title())
    links = image_links[topic.title()]
    embed = discord.Embed(title=f"({topic.title()})",colour=discord.Colour.dark_purple(), timestamp=ctx.message.created_at, url=links[1])
    embed.set_author(name=ctx.guild.name, icon_url=ctx.guild.icon_url)
    embed.add_field(name="__**Definition:**__", value=f"```{' '.join(result)}```", inline=False)
    embed.set_thumbnail(url=links[0])
    embed.set_image(url=links[0])
    embed.set_footer(text=f"Requested by: {ctx.author.name}", icon_url=ctx.author.avatar_url)
    await ctx.send(embed=embed)


  async def the_database(self):
    db = sqlite3.connect("universe.db")
    mycursor = db.cursor()
    return mycursor, db
    

  # Database commands
  @commands.command(hidden=True)
  @commands.is_owner()
  async def create_table(self, ctx):
    if await self.table_exists():
      return await ctx.send("**Table __Universe__ already exists!**")
    
    mycursor, db = await self.the_database()
    mycursor.execute("CREATE TABLE Universe (user_id INTEGER, user_lvl INTEGER default 1, user_xp INTEGER default 0, user_ts INTEGER default 0)")
    db.commit()
    mycursor.close()
    return await ctx.send("**Table __Universe__ created!**")

  @commands.command(hidden=True)
  @commands.is_owner()
  async def drop_table(self, ctx):
    if not await self.table_exists():
      return await ctx.send("**Table __Universe__ doesn't exist!**")
    
    mycursor, db = await self.the_database()
    mycursor.execute("DROP TABLE Universe")
    db.commit()
    mycursor.close()
    return await ctx.send("**Table __Universe__ dropped!**")

  @commands.command(hidden=True)
  @commands.is_owner()
  async def reset_table(self, ctx):
    if not await self.table_exists():
      return await ctx.send("**Table __Universe__ doesn't exist yet!**")
    
    mycursor, db = await self.the_database()
    mycursor.execute("DELETE FROM Universe")
    db.commit()
    mycursor.close()
    return await ctx.send("**Table __Universe__ reset!**")

  async def table_exists(self):
    mycursor, db = await self.the_database()
    mycursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='Universe'")
    table_info = mycursor.fetchall()
    mycursor.close()
    if len(table_info) == 0:
        return False
    else:
        return True


  async def insert_user(self, user_id: int):
    mycursor, db = await self.the_database()
    mycursor.execute(f"INSERT INTO Universe (user_id) VALUES ({user_id})")
    db.commit()
    mycursor.close()
    pass

  async def update_data(self, user: discord.Member, the_time: int, channel):
    user_id = user.id
    the_member = await self.get_user(user_id)
    if the_time - the_member[0][3] >= 3 or the_member[0][2] == 0:
      await self.update_user_xp_time(user_id, the_time)
      await self.update_user_xp(user_id, 5)
      return await self.level_up(user, channel)

  async def update_user_xp_time(self, user_id: int, the_time: int):
    mycursor, db = await self.the_database()
    mycursor.execute(f"UPDATE Universe SET user_ts = {the_time} WHERE user_id = {user_id}")
    db.commit()
    mycursor.close()

  async def update_user_xp(self, user_id: int, the_xp: int):
    mycursor, db = await self.the_database()
    mycursor.execute(f"UPDATE Universe SET user_xp = user_xp + {the_xp} WHERE user_id = {user_id}")
    db.commit()
    mycursor.close()


  async def check_user(self, user_id: int):
    mycursor, db = await self.the_database()
    mycursor.execute(f"SELECT * FROM Universe WHERE user_id = {user_id}")
    if mycursor.fetchall():
      return True
    else:
      return False

  async def get_user(self, user_id: int):
    mycursor, db = await self.the_database()
    mycursor.execute(f"SELECT * FROM Universe WHERE user_id = {user_id}")
    if the_user := mycursor.fetchall():
      return the_user
    else:
      return False

  async def level_up(self, user: discord.Member, channel):
    the_user = await self.get_user(user.id)
    lvl_end = int(the_user[0][2] ** (1 / 5))
    if the_user[0][1] < lvl_end:
        await self.update_user_lvl(user.id, the_user[0][1] + 1)
        astro = await self.get_astro(the_user[0][1] + 1, galaxy)
        if await self.disabled_server(channel.guild.id):
          return
        try:
          return await channel.send(f"**{user.mention} has leveled up to `{astro[0]}`!**")
        except Exception:
          pass

  async def update_user_lvl(self, user_id: int, user_lvl: int):
    mycursor, db = await self.the_database()
    mycursor.execute(f"UPDATE Universe SET user_lvl = {user_lvl} WHERE user_id = {user_id}")
    db.commit()
    mycursor.close()

  @commands.command()
  async def profile(self, ctx, member: discord.Member = None) -> object:
    '''
    Shows your astronomical profile.
    '''
    if not member:
      member = ctx.author
    
    the_user = await self.get_user(member.id)
    if not the_user:
      return await ctx.send(f"**{member} doesn't have a profile yet!**")
    astro = await self.get_astro(the_user[0][1], galaxy)
    embed = discord.Embed(title="__Profile__", colour=member.color, timestamp=ctx.message.created_at, url=astro[1][1])
    embed.add_field(name="__**Rank**__", value=f"{astro[0]}.", inline=False)
    embed.add_field(name="__**EXP**__", value=f"{the_user[0][2]} / {((the_user[0][1]+1)**5)}.", inline=False)
    embed.set_thumbnail(url=astro[1][0])
    embed.set_footer(text=f"{member}", icon_url=member.avatar_url)
    #embed.set_image(url='https://cdn.discordapp.com/attachments/719020754858934294/722519380914602145/mercury.png')
    #{user[0][1]} / {((user[0][2]+1)**5)}."
    return await ctx.send(embed=embed)

  @commands.command()
  async def source(self, ctx, command: str = None):
    """Displays my full source code or for a specific command.
    To display the source code of a subcommand you have to separate it by
    periods, e.g. tag.create for the create subcommand of the tag command.
    """
    source_url = 'https://github.com/yagomichalak/astronomy-bot'
    if command is None:
        await ctx.send(source_url)
        return

    code_path = command.split('.')
    obj = self.client
    for cmd in code_path:
        try:
            obj = obj.get_command(cmd)
            if obj is None:
                await ctx.send(await _(ctx, 'Could not find the command ') + cmd)
                return
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
        base = 'https://github.com/Rapptz/discord.py'
        final_url = '<{}/blob/master/{}#L{}>'.format(base, location, src.co_firstlineno)

    await ctx.send(final_url)

  async def get_astro(self, level, galaxy) -> str:
    i = 0
    has_planet = False
    for system in galaxy:
        for pi, p in reversed(list(system.items())):
            #print(pi, p)
            i += 1
            #print(f"Planet: {i} {p}")
            if i == level:
                #print(f"You're {system[pi]}")
                has_planet = [pi, system[pi]]
                break
        if has_planet:
            break

    else:
        has_planet = [level, f"Asteroid {level}"]
    return has_planet

  @commands.command(aliases=['scoreboard', 'sb', 'rank', 'ranking'])
  async def score(self, ctx):
    '''
    Shows the global scoreboard, regarding the experience points.
    '''
    users = await self.get_top_ten()
    spec_user = await self.get_user(ctx.author.id)
    scoreboard = discord.Embed(
      title='__**Astronomical Scoreboard**__',
      description='Top ten people in the world with more XP.',
      color=self.client.user.color,
      timestamp=ctx.message.created_at
      )
    scoreboard.set_thumbnail(url=ctx.guild.icon_url)
    scoreboard.set_footer(text=f"You: {spec_user[0][2]} XP", icon_url=ctx.author.avatar_url)

    for i, user in enumerate(users):
      member = self.client.get_user(user[0])
      scoreboard.add_field(name=f"{i+1} - __{member}__", value=f"`{user[2]}` XP", inline=False)
    await ctx.send(embed=scoreboard)
    #await ctx.send(users)

  async def get_top_ten(self):
    mycursor, db = await self.the_database()
    mycursor.execute('SELECT * FROM Universe ORDER BY user_xp DESC limit 10')
    users = mycursor.fetchall()
    mycursor.close()
    return users

  @commands.command()
  @commands.has_permissions(administrator=True)
  async def enable_levels(self, ctx):
    '''
    Enables leveling up messages for a specific server.
    '''
    if not await self.table_blocked_guilds_exists():
      return await ctx.send("**This feature is on maintenance!**")

    if await self.disabled_server(ctx.guild.id):
      await self.remove_disabled_server(ctx.guild.id)
      await ctx.send("**Levels enabled again for this server!**")
    else:
      await ctx.send("**Levels are already enabled for this server!**")

  @commands.command()
  @commands.has_permissions(administrator=True)
  async def disable_levels(self, ctx):
    '''
    Disables leveling up messages for a specific server.
    '''
    if not await self.table_blocked_guilds_exists():
      return await ctx.send("**This feature is on maintenance!**")
    if not await self.disabled_server(ctx.guild.id):
      await self.insert_disabled_server(ctx.guild.id)
      await ctx.send("**Levels disabled for this server!**")
    else:
      await ctx.send("**Levels are already disabled for this server!**")
  
  # Database commands
  @commands.command(hidden=True)
  @commands.is_owner()
  async def create_table_blocked_guilds(self, ctx):
    '''
    Creates the BlockedGuilds table.
    '''
    if await self.table_blocked_guilds_exists():
      return await ctx.send("**Table __BlockedGuilds__ already exists!**")
    
    mycursor, db = await self.the_database()
    mycursor.execute("CREATE TABLE BlockedGuilds (guild_id INTEGER NOT NULL)")
    db.commit()
    mycursor.close()
    return await ctx.send("**Table __BlockedGuilds__ created!**")

  @commands.command(hidden=True)
  @commands.is_owner()
  async def drop_table_blocked_guilds(self, ctx):
    '''
    Drops the BlockedGuilds table.
    '''
    if not await self.table_blocked_guilds_exists():
      return await ctx.send("**Table __BlockedGuilds__ doesn't exist!**")
    
    mycursor, db = await self.the_database()
    mycursor.execute("DROP TABLE BlockedGuilds")
    db.commit()
    mycursor.close()
    return await ctx.send("**Table __BlockedGuilds__ dropped!**")

  @commands.command(hidden=True)
  @commands.is_owner()
  async def reset_table_blocked_guilds(self, ctx):
    '''
    Resets the BlockedGuilds table.
    '''
    if not await self.table_blocked_guilds_exists():
      return await ctx.send("**Table __BlockedGuilds__ doesn't exist yet!**")
    
    mycursor, db = await self.the_database()
    mycursor.execute("DELETE FROM BlockedGuilds")
    db.commit()
    mycursor.close()
    return await ctx.send("**Table __BlockedGuilds__ reset!**")

  async def table_blocked_guilds_exists(self):
    mycursor, db = await self.the_database()
    mycursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='BlockedGuilds'")
    table_info = mycursor.fetchall()
    mycursor.close()
    if len(table_info) == 0:
        return False
    else:
        return True

  async def insert_disabled_server(self, gid: int):
    mycursor, db = await self.the_database()
    mycursor.execute(f"INSERT INTO BlockedGuilds (guild_id) VALUES ({gid})")
    db.commit()
    mycursor.close()
  
  async def remove_disabled_server(self, gid: int):
    mycursor, db = await self.the_database()
    mycursor.execute(f"DELETE FROM BlockedGuilds WHERE guild_id = {gid}")
    db.commit()
    mycursor.close()

  async def disabled_server(self, gid: int):
    mycursor, db = await self.the_database()
    mycursor.execute(f"SELECT * FROM BlockedGuilds WHERE guild_id = {gid}")
    the_guild = mycursor.fetchall()
    mycursor.close()
    if len(the_guild) > 0:
      return True
    else:
      return False

  @commands.command()
  async def random(self, ctx):
    '''
    Fetches a random topic from the system.
    '''
    topic = random.choice(list(image_links))
    await self.whatIs(ctx, topic)

  @commands.command()
  @commands.cooldown(1, 5, type=commands.BucketType.user)
  async def agency(self, ctx, *, country: str = None):
    '''
    Shows all space agencies in the world or a specific one.
    :param country: The country of that agency.
    '''
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
        embed.set_footer(text=f"Requested by: {ctx.author}", icon_url=ctx.author.avatar_url)
        await ctx.send(embed=embed)

    else:
      embed = discord.Embed(title="__Space Agencies__",
      description='All space agencies in the world.',
      color=ctx.author.color,
      timestamp=ctx.message.created_at,
      url='https://en.wikipedia.org/wiki/List_of_government_space_agencies#List_of_space_agencies'
      )

      msg = await ctx.send(embed=embed)
      await asyncio.sleep(0.5)

      def check(reaction, user):
        return str(reaction.message.id) == str(msg.id) and user == ctx.author and str(reaction.emoji) in ['⬅️', '➡️']


      await msg.add_reaction('⬅️')
      await msg.add_reaction('➡️')
      lensa = len(list(space_agencies))
      index = 0
      while True:
        for i in range(6):
          #print(i)
          try:
            key = list(space_agencies)[index + i]
            value = space_agencies[key]
          except IndexError:
            break
          else:
            #print(f"key {key}")
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
  @commands.cooldown(1, 5, type=commands.BucketType.user)
  async def movie(self, ctx, *, title: str = None):
    '''
    Shows some movies about astronomy and space. Or a specific one.
    :param title: The name/title of the movie.
    '''
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
      embed.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.avatar_url)
      await ctx.send(embed=embed)


    else:
      refs = ['https://spacenews.com/11-must-see-space-movies-for-anyone-serious-about-space/', 'https://www.theringer.com/2017/9/11/16285932/25-best-space-movies-ranked']
      refs = [f"[link{i+1}]({r})" for i, r in enumerate(refs)]
      embed = discord.Embed(title="🎥 __Movies About Astronomy and Space__ 🎥",
      description=f"Refs: {', '.join(refs)}",
      color=ctx.author.color,
      timestamp=ctx.message.created_at,)

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
    
def setup(client):
  #client.add_command(help)
  client.add_cog(Astronomy(client))
