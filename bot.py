import os

import discord
from discord import app_commands
from dotenv import load_dotenv

import commands.attraction as attraction
import commands.sync as sync


load_dotenv()
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
GUILD = discord.Object(id=int(os.getenv("GUILD_ID")))

intents = discord.Intents.default()

client = discord.Client(intents=intents)

tree = app_commands.CommandTree(client)


def main():
    tree.add_command(Attraction(), guild=GUILD)

    client.run(DISCORD_TOKEN)


@client.event
async def on_ready():
    print(f"Logged in as {client.user}!")


@tree.command(description="Sync application commands.", guild=GUILD)
async def sync_commands(interaction):
    await sync.sync_commands(interaction, tree, GUILD)


class Attraction(app_commands.Group):
    """Get/manage attractions."""

    @app_commands.command(description="Get data for an attraction.")
    @app_commands.describe(
        park_name="The theme park to search.",
        attraction_name="The attraction to search for."
    )
    async def get(self, interaction, park_name: str, attraction_name: str):
        await attraction.get(interaction, park_name, attraction_name)


main()
