import asyncio
import logging
import os

import discord
from discord import app_commands
from dotenv import load_dotenv

import commands.attraction as attraction
import commands.destination as destination
import commands.sync as sync
import commands.weather as weather
import helpers.track_attractions as track_attractions

logging.getLogger().setLevel(logging.INFO)

load_dotenv()
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
GUILD = discord.Object(int(os.getenv("GUILD_ID")))

intents = discord.Intents.default()

client = discord.Client(intents=intents)

tree = app_commands.CommandTree(client)


def main():
    tree.add_command(Attraction(), guild=GUILD)
    tree.add_command(Destination(), guild=GUILD)
    tree.add_command(Weather(), guild=GUILD)

    client.run(DISCORD_TOKEN)


@client.event
async def on_ready():
    print(f"Logged in as {client.user}!")

    while True:
        await track_attractions.track(client)
        await asyncio.sleep(5)


@tree.command(description="Sync application commands.", guild=GUILD)
async def sync_commands(interaction):
    await sync.sync_commands(interaction, tree, GUILD)


class Attraction(app_commands.Group):
    """Get/manage attractions."""

    @app_commands.command(description="Clear all tracked attractions.")
    async def clear_tracked(self, interaction):
        await attraction.clear_tracked(interaction)

    @app_commands.command(description="Get information for an attraction.")
    @app_commands.describe(
        attraction_name=(
            "The attraction to search for. Type all of part of the name."
        ),
        park_name=("The theme park to search. Type all or part of the name."),
    )
    async def get(
        self,
        interaction,
        attraction_name: str,
        park_name: str = None,
        destination_name: str = None,
    ):
        await attraction.get(
            interaction, attraction_name, park_name, destination_name
        )

    @app_commands.command(description="Track an attraction.")
    async def track(
        self,
        interaction,
        attraction_name: str,
        wait_threshold: app_commands.Range[int, 0],
        park_name: str = None,
        destination_name: str = None,
    ):
        await attraction.track(
            interaction,
            attraction_name,
            wait_threshold,
            park_name,
            destination_name,
        )

    @app_commands.command(description="Untrack an attraction.")
    async def untrack(
        self,
        interaction,
        attraction_name: str,
        park_name: str = None,
        destination_name: str = None,
    ):
        await attraction.untrack(
            interaction, attraction_name, park_name, destination_name
        )

    @app_commands.command(description="View tracked attrations.")
    async def view_tracked(self, interaction):
        await attraction.view_tracked(interaction)


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

    @app_commands.command(description="Clear your destination list.")
    async def clear_added(self, interaction):
        await destination.clear_added(interaction)

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

    @app_commands.command(description="View added destinations.")
    async def view_added(self, interaction):
        await destination.view_added(interaction)


class Weather(app_commands.Group):
    # Weather related commands

    @app_commands.command(
        description="Get the weather forecast for a destination."
    )
    @app_commands.describe(
        destination_name=("The destination to get the weather forcast of.")
    )
    async def forecast(self, interaction, destination_name: str):
        await weather.forecast(interaction, destination_name)


if __name__ == "__main__":
    main()
