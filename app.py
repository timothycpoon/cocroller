#!/usr/bin/env python3
# This example requires the 'message_content' intent.

from dotenv import load_dotenv
import os

from bot import bot
from db import db
from daily import DailyCog


if __name__ == '__main__':
    load_dotenv()
    CLIENT_SECRET = os.getenv('CLIENT_SECRET')
    CONNECTION_STRING = os.getenv('CONNECTION_STRING')
    
    db.initialize(CONNECTION_STRING)
    bot.add_cog(DailyCog(bot))
    bot.run(CLIENT_SECRET)
