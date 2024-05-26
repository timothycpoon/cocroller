from discord.ext import tasks, commands
from datetime import datetime, timezone
import time

class DailyCog(commands.Cog):
    CHANNEL_ID = 1085319916594405408
    GUILD_ID = 1084587109857370183
    EVENT_ID = 1216460048843280475

    def __init__(self, bot):
        self.bot = bot
        self.send_reminder.start()

    @tasks.loop(hours=1)
    async def send_reminder(self):
        channel = self.bot.get_channel(self.CHANNEL_ID)
        guild = self.bot.get_guild(self.GUILD_ID)
        if guild == None or channel == None:
            print("Cannot find guild or channel")
            return

        event = guild.get_scheduled_event(self.EVENT_ID)
        if event == None:
            print("Cannot find event")
            return

        td = event.start_time - datetime.now(timezone.utc)
        hours = int(td.seconds / 60 / 60)
        if td.days == 0 and hours == 8:
            await channel.send("<@&1085319290980409454> Next JERP session is <t:{}:R>!".format(int(time.mktime(event.start_time.timetuple()))))
        print("ASDFASDF\n\n")

    @send_reminder.before_loop
    async def before_printer(self):
        print('waiting...')
        await self.bot.wait_until_ready()
