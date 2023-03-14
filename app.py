#!/usr/bin/env python3
# This example requires the 'message_content' intent.

from dotenv import load_dotenv
import os
import random
import re

import discord
from discord import Colour

load_dotenv()
CLIENT_SECRET = os.getenv('CLIENT_SECRET')

bot = discord.Bot()

def roll_helper(die):
    return random.randint(0, die - 1)

@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user}')

async def send_error(msg):
    return ctx.respond(embed = discord.Embed(description = msg, colour = Colour.red()))

def get_sucess_info(result, threshold):
    success_str = "Failure :("
    success_colour = Colour.red()

    if result == 1:
        success_str = "Crtical success!"
        success_colour = Colour.green()
    elif result == 100:
        success_str = "Fumbled!"
        success_colour = Colour.red()
    elif result >= 96:
        success_str = "Fumbled if success chance < 50%, otherwise "
        success_colour = Colour.red()
        if result <= threshold:
            success_str += "success"
        else:
            success_str += "normal failure"
    elif result <= threshold / 5:
        success_str = "Extreme success!"
        success_colour = Colour.green()
    elif result <= threshold / 2:
        success_str = "Hard success!"
        success_colour = Colour.green()
    elif result <= threshold:
        success_str = "Success!"
        success_colour = Colour.green()

    return success_str, success_colour

# remove hardcoded test server
@bot.slash_command(guild_ids=[828850110833885224], description="Roll a d100 and compare to threshold (usually skill level)")
async def r100(ctx, threshold: int, bonus: int = 0, penalty: int = 0, ephemeral: bool = False):
    response = ""
    if bonus < 0 or penalty < 0:
        await ctx.respond("Cannot have negative bonus or penalty dice")
        return
    if bonus > 0 and penalty > 0:
        if bonus == penalty:
            bonus = 0
            penalty = 0
        elif bonus > penalty:
            bonus = bonus - penalty
            penalty = 0
        elif bonus < penalty:
            penalty = penalty - bonus
            bonus = 0
        response += "Bonus and penalty die cancel out! Treating request as {} bonus and {} penalty dice\n".format(bonus, penalty)

    tens = [roll_helper(10) for _ in range(bonus + penalty + 1)]
    response += "Tens: {}\n".format(tens[0] if len(tens) == 1 else tens)
    tens_result = min(tens) if bonus > 0 else max(tens)
    if bonus > 0:
        response += "Taking {} due to bonus di(c)e\n".format(tens_result)
    if penalty > 0:
        response += "Taking {} due to penalty di(c)e\n".format(tens_result)
    ones_result = roll_helper(10)
    response += "Ones: {}\n".format(ones_result)

    result = 100 if tens_result == 0 and ones_result == 0 else 10 * tens_result + ones_result
    response += "Total: {}\n".format(result)
    success_str, success_colour = get_sucess_info(result, threshold)
    await ctx.respond(embed = discord.Embed(title = success_str, description = response, colour = success_colour), ephemeral = ephemeral)

@bot.slash_command(guild_ids=[828850110833885224], description="Roll dice (e.g. 1d6+5)")
async def roll(ctx, dice_str: str, ephemeral: bool = False):
    dice = dice_str.replace(" ", "").split("+")
    result = 0
    result_str = ""

    for d in dice:
        match = re.match(r'^([1-9][0-9]*)(?:d([1-9][0-9]*))?$', d)
        if not match:
            await send_error("Dice rolls should be in the form of (#dice)d(size of dice), adjoined by a '+'. For example, 1d6 rolls a single 6-sided die")
            return
        if match.lastindex == 1:
            result += int(match[1])
            result_str += "{}{}".format(" + " if result_str else "", match[1])
        elif match.lastindex == 2:
            num = int(match[1])
            size = int(match[2])
            results = [roll_helper(size) + 1 for _ in range(num)]
            for r in results:
                result_str += "{}{}".format(" + " if result_str else "", r)
            result += sum(results)

    result_str += " = {}\n".format(result)
    await ctx.respond(embed = discord.Embed(title = result, description = result_str), ephemeral = ephemeral)


bot.run(CLIENT_SECRET)