from discord import Colour

def get_success_info(result, threshold):
    success_str = "Failure :("
    success_colour = Colour.red()

    if result == 1:
        success_str = "Critical success!"
        success_colour = Colour.green()
    elif result == 100:
        success_str = "Fumbled!"
        success_colour = Colour.red()
    elif result >= 96 and threshold < 50:
        success_str = "Fumbled!"
        success_colour = Colour.red()
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
