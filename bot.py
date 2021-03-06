import discord
import os
import asyncio
import time
from discord.ext import commands
from settings import DISCORD_TOKEN
from core.nations import Nations
from core.wars import Wars
from core.warchest import WarChest
from embed.display_error import DisplayError
from embed.display_nation import DisplayNation
from embed.display_nation_wars import DisplayNationWars
from embed.display_warchest import DisplayWarChest
from embed.display_find_counter import DisplayFindCounter

class Bot(commands.Bot):
    def __init__(self, **options):
        super().__init__(command_prefix='=')
        super().remove_command('help')

        super().add_command(self.ping)
        super().add_command(self.display_nation)
        super().add_command(self.display_nation_wars)
        super().add_command(self.display_required_warchest)
        # super().add_command(self.find_raid_target)
        super().add_command(self.find_counters)

    @classmethod
    def start_bot(bot, token=None):
        """Actual method to start the bot
        
        Args:
            bot ([type]): [description]
            token ([type], optional): [description]. Defaults to None.
        """
        bot = bot()
        token = token or DISCORD_TOKEN

        try:
            bot.run(token, reconnect=True)
        except Exception as e:
            print(e)

    async def on_connect(self):
        print('bot.py connected!')

    async def on_ready(self):
        print(f'Hi, {self.user} is online!')

    async def on_message(self, message):
        # respond to others only
        if message.author.id == self.user.id:
            return

        await self.process_commands(message)

    @commands.command()
    async def ping(self):
        await self.send('Pong!')

    @commands.command(aliases=['find'])
    async def display_nation_in_aa(self, nation_id):
        await self.send(f'The nation id youre looking for is: {nation_id}. {round(self.latency*1000)}ms')

    @commands.command(aliases=['nation'])
    async def display_nation(self, nation_id):
        """Display a nation's info
        
        Args:
            nation_id (int): Unique ID of nation get info
        """
        before = time.monotonic()

        nation_info = Nations().find_nation(nation_id)

        embed = DisplayNation().display(nation_info)        

        embed.set_footer(text=f'{int((time.monotonic() - before) * 1000)}ms')

        return await self.send(embed=embed)

    @commands.command(aliases=['wars'])
    async def display_nation_wars(self, nation_id):
        """Display a nation's current wars
        
        Args:
            nation_id (int): Unique ID of nation get info
        """
        before = time.monotonic()

        nation_info = Nations().find_nation(nation_id)
        
        embed = DisplayNationWars().display(nation_info)

        embed.set_footer(text=f'{int((time.monotonic() - before) * 1000)}ms')

        return await self.send(embed=embed)

    @commands.command(aliases=['chest'])
    async def display_required_warchest(self, city_count):
        """Display's a nation required warchest based on city count
        
        Args:
            city_count (int): City count of the nation
        """
        before = time.monotonic()

        if int(city_count) < 2 or int(city_count) > 30:
            embed = DisplayError().display('Only accepting parameters of 2 to 30 cities.')

            return await self.send(embed=embed)

        warchest = WarChest().find_warchest(city_count)

        embed = DisplayWarChest().display(city_count, warchest)

        embed.set_footer(text=f'{int((time.monotonic() - before) * 1000)}ms')

        return await self.send(embed=embed)

    @commands.command(aliases=['counter'])
    async def find_counters(self, nation_id):
        """Find an ally nation to counter an aggressor nation
        
        Args:
            nation_id (int): Unique ID of nation to find counter for
        """
        before = time.monotonic()

        aggresor_nation = Nations().find_nation(nation_id)

        counters = Wars().counter_targets(aggresor_nation)

        embed = DisplayFindCounter().display(aggresor_nation, counters)

        embed.set_footer(text=f'{int((time.monotonic() - before) * 1000)}ms')

        return await self.send(embed=embed)

    # @commands.command(aliases=['raid'])
    # async def find_raid_target(self, nation_id, alliance_id=0):
    #     """Find a raid target based on nation score and provided alliance id
        
    #     Args:
    #         nation_id (int): Unique ID of nation looking for raid targets
    #         alliance_id (int, optional): Alliance ID of preferred targets. Defaults to 0.
    #     """
    #     before = time.monotonic()

    #     nation_info = Nations().find_nation(nation_id)

    #     targets = Wars().raid_targets(nation_info, alliance_id)

    #     # print(targets) # individual print: targets[0]['nationid']
    #     for target in targets:
    #         print(f'{target["nationid"]} - {int(target["gdp"]):,}')
            
    #     print(f'{int((time.monotonic() - before) * 1000)}ms')

    @commands.command(pass_context=True)
    async def help(self):
        author = self.message.author

        embed = discord.Embed(
            colour=discord.Colour.blue()
        )

        embed.add_field(name='Help', value='Test', inline=False)

        await self.send(embed=embed)

if __name__ == '__main__':
    Bot.start_bot()
