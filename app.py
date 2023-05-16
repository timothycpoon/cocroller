#!/usr/bin/env python3
# This example requires the 'message_content' intent.

from dotenv import load_dotenv
import os

from bot import bot

load_dotenv()
CLIENT_SECRET = os.getenv('CLIENT_SECRET')
CONNECTION_STRING = os.getenv('CONNECTION_STRING')

if __name__ == '__main__':
    bot.run(CLIENT_SECRET)
