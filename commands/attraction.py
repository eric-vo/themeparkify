import helpers.decorators as decorators


@decorators.require_destinations
async def get(interaction, park_name, attraction_name):
    await interaction.response.send_message("Not implemented yet, sorry!")
