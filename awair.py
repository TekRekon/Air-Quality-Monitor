from discord.ext import commands, tasks
import aiohttp

import config


class Awair(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        self.autoHepaToggler.start()

    @commands.command()
    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.guild_only()
    @commands.is_owner()
    async def hepa(self, ctx, state):
        try:
            await Awair.switchHepa(state)
            await ctx.send(f'Switched HEPA to state: {state}')
        except Exception as e:
            await ctx.send(f'Error switching the HEPA filter: {e}-----{type(e)}-----{e.args}')

    @commands.command()
    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.guild_only()
    @commands.is_owner()
    async def monitor(self, ctx, state):
        try:
            if state == 'True':
                self.autoHepaToggler.start()
            else:
                self.autoHepaToggler.cancel()
            await ctx.send(f'Switched HEPA monitoring to state: {state}')
        except Exception as e:
            await ctx.send(f'Error switching the HEPA filter: {e}-----{type(e)}-----{e.args}')

    @staticmethod
    async def getSensorData():
        async with aiohttp.ClientSession(headers={'Authorization': config.bearer_token}) as session:
            async with session.get(
                    url=config.url) as r:
                if r.status == 429:
                    # Calls are being rate-limited
                    result = await r.json()
                    return result
                else:
                    result = await r.json()
                    return result

    @staticmethod
    async def switchHepa(state):
        async with aiohttp.ClientSession() as session:
            if state == "True":
                await session.post(config.device_one_on)
            else:
                await session.post(config.device_one_off)

    @tasks.loop(seconds=300.0)
    async def autoHepaToggler(self):
        # Get sensor dust/voc level and act on it
        dust_level = None
        voc_level = None
        dust_value = None
        voc_value = None
        try:
            f = await Awair.getSensorData()
            for sensor in f['data'][0]['indices']:
                if sensor['comp'] == 'pm25':
                    dust_level = sensor['value']
                if sensor['comp'] == 'voc':
                    voc_level = sensor['value']
            for sensor in f['data'][0]['sensors']:
                if sensor['comp'] == 'pm25':
                    dust_value = sensor['value']
                if sensor['comp'] == 'voc':
                    voc_value = sensor['value']

            if dust_level > 0 or voc_level > 2:
                await Awair.switchHepa("True")
            else:
                await Awair.switchHepa("False")

        # Data returned is empty if device is offline
        except IndexError:
            print('indexError in Awair')
        # Anomaly
        except TypeError:
            pass


def setup(bot):
    bot.add_cog(Awair(bot))
