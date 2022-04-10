import dbl
import discord
from discord.ext import commands

import os
from random import randint

on_vote_log_id: int = int(os.getenv('ON_VOTE_LOG_ID'))

class TopGG(commands.Cog):
	""" Handles interactions with the top.gg API. """

	def __init__(self, client) -> None:
		""" Class init method. """

		self.client = client
		self.token = os.getenv('DBL_TOKEN') # set this to your DBL token
		self.dblpy = dbl.DBLClient(self.client, self.token, autopost=True, webhook_path='/dblwebhook', webhook_auth=os.getenv('DBL_WEBHOOK_PASSWORD'), webhook_port=5000) # Autopost will post your guild count every 30 minutes
		#self.client.dispatch('on_dbl_test')

	async def on_guild_post() -> None:
		""" Tells when the server counter was updated. """

		print("Server count posted successfully")

	@commands.Cog.listener()
	async def on_dbl_vote(self, data) -> None:
		""" Logs when someone votes for the bot. """

		print("Vote!")
		vote_channel = self.client.get_channel(on_vote_log_id)
		member = await self.client.fetch_user(int(data['user']))
		embed = discord.Embed(
			title="New vote!",
			description=f"{member} voted on your bot.",
			color=discord.Color.green()
		)
		if member:
			embed.set_thumbnail(url=member.display_avatar)
		await vote_channel.send(embed=embed)

	@commands.Cog.listener()
	async def on_dbl_test(self, data) -> None:
		""" Tests the webhook. """

		print('Test vote!')
		self.client.get_user(int(data['user']))

	@commands.command()
	async def vote(self, ctx) -> None:
		""" Shows the amount of votes that the bot has, the amount of servers the bot is in and gives you a link to vote for the bot. """

		#widget = await self.dblpy.generate_widget_large()
		widget = f'https://top.gg/api/widget/723699955008798752.png?{randint(0, 2147483647)}topcolor=2C2F33&middlecolor=23272A&usernamecolor=FFFFF0&certifiedcolor=FFFFFF&datacolor=F0F0F0&labelcolor=99AAB5&highlightcolor=2C2F33'
		vote = 'https://top.gg/bot/723699955008798752/vote'
		embed = discord.Embed(title="__Vote on me!__",
			description=f"You can vote every 12 hours by clicking [here]({vote})."
		)
		embed.set_thumbnail(url=self.client.user.display_avatar)
		embed.set_image(url=widget)
		await ctx.send(embed=embed)


def setup(client: commands.Bot) -> None:
	""" Cog's setup function. """

	client.add_cog(TopGG(client))