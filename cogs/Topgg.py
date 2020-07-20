import dbl
import discord
from discord.ext import commands
import os

class TopGG(commands.Cog):
    """Handles interactions with the top.gg API"""

    def __init__(self, client):
        self.client = client
        self.token = os.getenv('DBL_TOKEN') # set this to your DBL token
        self.dblpy = dbl.DBLClient(self.client, self.token, autopost=True) # Autopost will post your guild count every 30 minutes

    async def on_guild_post():
        print("Server count posted successfully")

def setup(client):
    client.add_cog(TopGG(client))