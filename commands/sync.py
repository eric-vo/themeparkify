async def sync_commands(interaction, tree, guild=None):
    print("Syncing commands...")
    await interaction.response.defer()

    if guild is not None:
        await tree.sync(guild=guild)
    else:
        await tree.sync()

    print("Synced!")
    await interaction.followup.send("Synced!")
