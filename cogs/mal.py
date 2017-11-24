from html.parser import HTMLParser

from discord.ext import commands
import discord

from .util.checks import right_channel
from .util import tokage


class MyAnimeList:
    def __init__(self, bot):
        self.bot = bot
        self.mal_client = tokage.Client()

    async def __local_check(self, ctx):
        return right_channel(ctx)

    @commands.command()
    async def mal(self, ctx, *, query:str):
        anime_id = await self.mal_client.search_id('anime', query)
        if anime_id is None:
            return await ctx.send('No anime found. Sorry.')

        anime = await self.mal_client.get_anime(anime_id)

        html = HTMLParser()
        title = html.unescape(anime.title)
        j_title = html.unescape(anime.japanese_title)
        rating = html.unescape(anime.rating)
        synopsis = html.unescape(anime.synopsis)

        embed = discord.Embed()
        embed=discord.Embed(
            title=j_title,
            url=anime.link,
            description=f'**{title}** ({rating})\n{synopsis}')
        embed.set_thumbnail(url=anime.image)
        embed.add_field(name="Score", value=f'{anime.score[0]} ({anime.score[1]} reviews)', inline=True)
        embed.add_field(name="Rank", value=f'#{anime.rank}', inline=True)
        embed.add_field(name="Popularity", value=f'#{anime.popularity}', inline=True)
        embed.add_field(name="Episodes", value=anime.episodes, inline=True)
        embed.add_field(name="Status", value=anime.status, inline=True)
        embed.add_field(name="Duration", value=anime.duration, inline=True)
        embed.add_field(name="First Aired", value=anime.air_start, inline=True)
        embed.add_field(name="Finished Airing", value=anime.air_end, inline=True)
        embed.set_footer(text=' | '.join(anime.genres))

        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(MyAnimeList(bot))
