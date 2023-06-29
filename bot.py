import os

import discord
from discord import app_commands
from dotenv import load_dotenv

import commands.attraction as attraction
import commands.destination as destination
import commands.sync as sync

load_dotenv()
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
GUILD = discord.Object(id=int(os.getenv("GUILD_ID")))

intents = discord.Intents.default()

client = discord.Client(intents=intents)

tree = app_commands.CommandTree(client)


def main():
    tree.add_command(Attraction(), guild=GUILD)
    tree.add_command(Destination(), guild=GUILD)

    client.run(DISCORD_TOKEN)


@client.event
async def on_ready():
    print(f"Logged in as {client.user}!")


@tree.command(description="Sync application commands.", guild=GUILD)
async def sync_commands(interaction):
    await sync.sync_commands(interaction, tree, GUILD)


class Attraction(app_commands.Group):
    """Get/manage attractions."""

    @app_commands.command(description="Get information for an attraction.")
    @app_commands.describe(
        attraction_name=(
            "The attraction to search for. Type all of part of the name."
        ),
        park_name=(
            "The theme park to search. Type all or part of the name."
        )
    )
    async def get(self, interaction, park_name: str, attraction_name: str):
        await attraction.get(interaction, park_name, attraction_name)


class Destination(app_commands.Group):
    """Get/manage destinations."""

    @app_commands.command(description="Add a destination to the search list.")
    @app_commands.describe(
        destination_name=(
            "The destination to add. Type all of part of the name."
        )
    )
    async def add(self, interaction, destination_name: str):
        await destination.add(interaction, destination_name)

    @app_commands.command(
        description="Remove a destination from the search list."
    )
    @app_commands.describe(
        destination_name=(
            "The destination to remove. Type all of part of the name."
        )
    )
    async def remove(self, interaction, destination_name: str):
        await destination.remove(interaction, destination_name)


main()
