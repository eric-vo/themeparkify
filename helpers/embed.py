import discord

EMBED_DEFAULTS = {
    "color": discord.Color(0x00a8fc)
}

MAX_FIELDS = 25


def create_embed(title, description, color=EMBED_DEFAULTS["color"]):
    return discord.Embed(title=title, description=description, color=color)
