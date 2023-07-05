import discord

EMBED_DEFAULTS = {
    "color": discord.Color(0x00a8fc)
}

MAX_FIELDS = 25


def add_addresses(embed, entities):
    for entity in entities:
        if "location" in entity:
            location = entity["location"]
            address = (
                "[Google Maps]"
                "(https://www.google.com/maps/place/"
                f"{location['latitude']},{location['longitude']})"
            )
        else:
            address = ""

        embed.add_field(
            name=entity["name"],
            value=address,
            inline=False
        )


def create_embed(title, description, color=EMBED_DEFAULTS["color"]):
    return discord.Embed(title=title, description=description, color=color)


def create_error_embed(error):
    error_embed = create_embed("Error", error)
    return error_embed


def create_search_error_embed(error, query_name):
    error_embed = create_error_embed(
        f"{error} were found containing `{query_name}`."
    )
    return error_embed
