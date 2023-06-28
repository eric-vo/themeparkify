import os

import discord
from discord import app_commands
from dotenv import load_dotenv

import commands

load_dotenv()
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
GUILD = discord.Object(id=int(os.getenv("GUILD_ID")))

intents = discord.Intents.default()

client = discord.Client(intents=intents)

tree = app_commands.CommandTree(client)


def main():
    client.run(DISCORD_TOKEN)


@client.event
async def on_ready():
    print(f"Logged in as {client.user}!")


@tree.command(description="Sync application commands.", guild=GUILD)
async def sync_commands(interaction):
    await commands.sync_commands(interaction, tree, GUILD)


main()
