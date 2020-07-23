import dbl
import discord
from discord.ext import commands
import os
on_vote_log_id = os.getenv('ON_VOTE_LOG_ID')

class TopGG(commands.Cog):
  """Handles interactions with the top.gg API"""

  def __init__(self, client):
      self.client = client
      self.token = os.getenv('DBL_TOKEN') # set this to your DBL token
      self.dblpy = dbl.DBLClient(self.client, self.token, autopost=True, webhook_path='/dblwebhook', webhook_auth='justatest', webhook_port=8080) # Autopost will post your guild count every 30 minutes
      #self.client.dispatch('on_dbl_vote')

  async def on_guild_post():
      print("Server count posted successfully")

  @commands.Cog.listener()
  async def on_dbl_vote(self, data):
    print("voted")
    vote_channel = self.client.get_channel(int(on_vote_log_id))
    member = self.client.get_user(data['user'])
    embed = discord.Embed(title="New vote!",
    description=f"{member} voted on your bot.",
    color=discord.Color.green())
    embed.set_thumbnail(url=member.avatar_url)
    await vote_channel.send(embed=embed)

  @commands.Cog.listener()
  async def on_dbl_test(self, data):
    print('ey')
    print(data)


  @commands.command()
  async def vote(self, ctx):
    '''
    Shows the amount of votes that the bot has, the amount of servers the bot is in and gives you a link to vote for the bot.
    '''
    #widget = await self.dblpy.generate_widget_large()
    widget = 'https://top.gg/api/widget/723699955008798752.png?topcolor=2C2F33&middlecolor=23272A&usernamecolor=FFFFFF&certifiedcolor=FFFFFF&datacolor=FFFFF0&labelcolor=99AAB5&highlightcolor=2C2F33'
    vote = 'https://top.gg/bot/723699955008798752/vote'
    embed = discord.Embed(title="__Vote on me!__",
    description=f"Click [here]({vote}) to vote."
    )
    embed.set_thumbnail(url=self.client.user.avatar_url)
    embed.set_image(url=widget)
    await ctx.send(embed=embed)


def setup(client):
  client.add_cog(TopGG(client))