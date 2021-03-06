'''
This whole file is garbage

You have been warned
'''
import asyncio
import os

from discord.ext import commands
import feedparser
import discord

from .util.checks import right_channel


class YouTube:
    '''
    Youtube related commands
    '''
    def __init__(self, bot):
        self.bot = bot
        self.task = self.bot.loop.create_task(self.youtube_feed())
        self.config = self.bot.config.get('youtube', {})

    def __unload(self):
        self.task.cancel()

    def __local_check(self, ctx):
        if ctx.guild is None or not right_channel(ctx):
            return False

        guild_id = ctx.bot.config.get('ids', {}).get('htstem_id', 0)
        return ctx.guild.id == guild_id if not ctx.bot.debug else True

    async def youtube_feed(self):
        # File managment could be improved
        # *cough* *cough* botterwhydidyouchangeit *cough*
        await self.bot.wait_until_ready()

        if not os.path.exists('state_cache/videoURLS.txt'):
            os.mknod('state_cache/videoURLS.txt')

        feed_url = self.config.get('feed_url', None)

        if feed_url is None:
            return

        with open('state_cache/videoURLS.txt') as f:
            urls = f.readlines()

        while True:
            async with self.bot.session.get(feed_url) as resp:
                feed = feedparser.parse(resp.read())

            videos = feed['entries']

            for video in videos:
                href = video['link']
                if href not in urls:
                    urls.append(href)

                    title = video['title']
                    self.bot.logger.info('New video: {} - {}'.format(title, href))

                    channel_id = self.config.get('announcement_channel', 0)
                    channel = self.bot.get_channel(channel_id)
                    role = discord.utils.get(channel.guild.roles, id=self.config.get('role_id', 0))

                    if None in (channel, role):
                        continue

                    await channel.send('{0.mention} `{1}` has uploaded a new YouTube video!\n"{2}" - {3}'
                                       .format(role, ' '.join(map(lambda x: x['name'], video['authors'])),
                                               title, href))

            with open('state_cache/videoURLS.txt', 'w') as f:
                f.writelines(urls)

            await asyncio.sleep(15)


def setup(bot):
    bot.add_cog(YouTube(bot))
