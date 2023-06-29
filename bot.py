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

    @app_commands.command(description="Get information for an attraction.")
    @app_commands.describe(
        attraction_name=(
            "The attraction to search for. Type all of part of the name."
        ),
        park_name=(
            "The theme park to search. Type all or part of the name."
        )
    )
    async def get(self, interaction, attraction_name: str, park_name: str):
        await attraction.get(interaction, attraction_name, park_name)


main()
