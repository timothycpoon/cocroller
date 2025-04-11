from discord.ext import tasks, commands
from datetime import datetime, timezone, timedelta
from zoneinfo import ZoneInfo
import time

class DailyCog(commands.Cog):
    CHANNEL_ID = 1085319916594405408
    GUILD_ID = 1084587109857370183
    EVENT_ID = 1357910907124060281

    def __init__(self, bot):
        self.bot = bot
        self.send_reminder.start()

    @tasks.loop(hours=1)
    async def send_reminder(self):
        channel = self.bot.get_channel(self.CHANNEL_ID) or await self.bot.fetch_channel(self.CHANNEL_ID)
        guild = self.bot.get_guild(self.GUILD_ID) or await self.bot.fetch_guild(self.GUILD_ID)
        if guild == None or channel == None:
            print("Cannot find guild or channel")
            return

        event = guild.get_scheduled_event(self.EVENT_ID) or await guild.fetch_scheduled_event(self.EVENT_ID)
        if event == None:
            print("Cannot find event")
            return

        dst_start = event.start_time + event.start_time.astimezone(ZoneInfo("US/Pacific")).dst() - timedelta(hours=1)
        td = dst_start - datetime.now(timezone.utc)
        hours = int(td.seconds / 60 / 60)
        print("Days: ", td.days, "; Hours: ", hours, "; TS: ", int(dst_start.timestamp()))
        if td.days == 0 and hours == 2:
            await channel.send("<@&1085319290980409454> It's MILFing time <t:{}:R>!".format(int(dst_start.timestamp())))

    @send_reminder.before_loop
    async def before_printer(self):
        print('waiting...')
        await self.bot.wait_until_ready()
