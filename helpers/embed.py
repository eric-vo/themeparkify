import discord

EMBED_DEFAULTS = {
    "color": discord.Color.og_blurple()
}


def create_embed(title, description, color=EMBED_DEFAULTS["color"]):
    return discord.Embed(title=title, description=description, color=color)
