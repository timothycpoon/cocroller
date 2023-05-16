import discord
from discord import Colour

import random
import re

from constants import Success
from db import db
from user import User

bot = discord.Bot()

def roll_helper(die):
    return random.randint(0, die - 1)

@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user}')

async def send_error(msg):
    return ctx.respond(embed = discord.Embed(description = msg, colour = Colour.red()))

def get_success_info(result, threshold):
    success_str = "Failure :("
    success_colour = Colour.red()

    if result == 1:
        success_str = Success.CRITICAL
        success_colour = Colour.green()
    elif result == 100:
        success_str = Success.FUMBLED
        success_colour = Colour.red()
    elif result >= 96 and threshold < 50:
        success_str = Success.FUMBLED
        success_colour = Colour.red()
    elif result <= threshold / 5:
        success_str = Success.EXTREME
        success_colour = Colour.green()
    elif result <= threshold / 2:
        success_str = Success.HARD
        success_colour = Colour.green()
    elif result <= threshold:
        success_str = Success.NORMAL
        success_colour = Colour.green()

    return success_str, success_colour

def get_luck_str(result, threshold):
    luck_strs = []
    if result == 1 or result == 100:
        return ""
    if result >= 96:
        luck_strs.append("Note: can only spend luck if not a fumble")
    if result > threshold:
        luck_strs.append("Spend {} luck for success!".format(result - threshold))
    if result > threshold / 2:
        luck_strs.append("Spend {} luck for hard success!".format(int(result - threshold / 2)))
    if result > threshold / 5:
        luck_strs.append("Spend {} luck for extreme success!".format(int(result - threshold / 5)))

    if len(luck_strs) == 0:
        return ""

    return "\n[Using luck?]({} \"{}\")".format("https://cdn3.emoji.gg/emojis/2923_MikuDab.png", "\n".join(luck_strs))

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

    if success_str == Success.CRITICAL:
        user = User(ctx.author.id)
        user.increment_crit_count()
        user.save()

    if success_str == Success.FUMBLED:
        user = User(ctx.author.id)
        user.increment_fumble_count()
        if result == 100:
            user.increment_nat_100_count()
        user.save()

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

@bot.slash_command(description="Show leaderboard of nat 100s")
async def leaderboard_nat100(ctx):
    user_list = db.collection("users").find({}).sort('nat100s', -1)
    description = '\n'.join(["<@{}>: {}".format(user.get('user_id'), user.get('nat100s'))
                             for user in user_list if user.get('nat100s')])

    await ctx.respond(embed = discord.Embed(title = "Leaderboard of Nat 100s <:nat100:1107895321314476063>",
                                            description = description))

@bot.slash_command(description="Show leaderboard of fumbles")
async def leaderboard_fumble(ctx):
    user_list = db.collection("users").find({}).sort('fumbles', -1)
    description = '\n'.join(["<@{}>: {}".format(user.get('user_id'), user.get('fumbles'))
                             for user in user_list if user.get('fumbles')])

    await ctx.respond(embed = discord.Embed(title = "Leaderboard of Fumbles",
                                            description = description))

@bot.slash_command(description="Show leaderboard of crits")
async def leaderboard_crit(ctx):
    user_list = db.collection("users").find({}).sort('crits', -1)
    description = '\n'.join(["<@{}>: {}".format(user.get('user_id'), user.get('crits'))
                             for user in user_list if user.get('crits')])

    await ctx.respond(embed = discord.Embed(title = "Leaderboard of Crits",
                                            description = description))
