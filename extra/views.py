import discord
from discord.ext import commands

from typing import Optional, Any, Union

class PaginatorView(discord.ui.View):
    """ View for the embed paginator. """

    def __init__(self, data, timeout: Optional[float] = 180, increment: int = 1, **kwargs: Any) -> None:
        """ Class init method. """

        super().__init__(timeout=timeout)
        self.data = data
        self.client = kwargs.get('client')
        self.req = kwargs.get('req', None)
        self.search = kwargs.get('search', None)
        self.result = kwargs.get('result', None)
        self.title = kwargs.get('title', None)
        self.change_embed = kwargs.get('change_embed')
        self.index: int = 0
        self.increment = increment

    @discord.ui.button(label="Left", emoji="⬅", style=discord.ButtonStyle.blurple, custom_id="left_button_id")
    async def button_left(self, button: discord.ui.button, interaction: discord.Interaction) -> None:
        """ Flips the page to the left. """

        await interaction.response.defer()
        
        if self.index > 0:
            self.index -= self.increment

        embed = await self.make_embed(interaction.user)
        await interaction.followup.edit_message(interaction.message.id, embed=embed)

    @discord.ui.button(label="Right", emoji="➡", style=discord.ButtonStyle.blurple, custom_id="right_button_id")
    async def button_right(self, button: discord.ui.button, interaction: discord.Interaction) -> None:
        """ Flips the page to the right. """

        await interaction.response.defer()

        if self.index < len(self.data) - self.increment:
            self.index += self.increment

        embed = await self.make_embed(interaction.user)
        await interaction.followup.edit_message(interaction.message.id, embed=embed)

    async def make_embed(self, member: Union[discord.Member, discord.User]) -> discord.Embed:
        """ Makes an embed for the next page.
        :param interaction: The interaction that triggered this. """

        embed = await self.change_embed(
            req=self.req, member=member, search=self.search, 
            example=self.data[self.index], offset=self.index+1, 
            lentries=len(self.data), entries=self.data, title=self.title, 
            result=self.result
        )
        return embed
