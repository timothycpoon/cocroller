import discord
from discord import Colour

import random
import re

from bot_interpreter import get_success_info, get_luck_str

bot = discord.Bot()

def roll_helper(die):
    return random.randint(0, die - 1)

@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user}')

async def send_error(msg):
    return ctx.respond(embed = discord.Embed(description = msg, colour = Colour.red()))

@bot.slash_command(description="Roll a d100 and compare to threshold (usually skill level)")
async def r100(ctx, threshold: int, bonus: int = 0, penalty: int = 0, ephemeral: bool = False):
    response = "Threshold: {}\n".format(threshold)
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

    # process boni and penalties
    tens = [roll_helper(10) for _ in range(bonus + penalty + 1)]
    response += "Tens: {}\n".format(tens[0] if len(tens) == 1 else tens)
    ones_result = roll_helper(10)
    if ones_result == 0:
        tens = map(lambda x: 10 if x == 0 else x, tens)
    tens_result = min(tens) if bonus > 0 else max(tens)
    if bonus > 0:
        response += "Taking {} due to bonus di(c)e\n".format(tens_result)
    if penalty > 0:
        response += "Taking {} due to penalty di(c)e\n".format(tens_result)
    response += "Ones: {}\n".format(ones_result)

    result = 100 if tens_result == 0 and ones_result == 0 else 10 * tens_result + ones_result
    response += "Total: {}\n".format(result)
    success_str, success_colour = get_success_info(result, threshold)
    luck_str = get_luck_str(result, threshold)
    if ephemeral:
        await ctx.respond(embed = discord.Embed(title = "Secret roll..."))
    await ctx.respond(embed = discord.Embed(title = success_str, description = response + luck_str, colour = success_colour), ephemeral = ephemeral)

@bot.slash_command(description="Roll dice (e.g. 1d6+5)")
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
    if ephemeral:
        await ctx.respond(embed = discord.Embed(title = "Secret roll..."))
    await ctx.respond(embed = discord.Embed(title = result, description = dice_str + "\n" + result_str), ephemeral = ephemeral)
