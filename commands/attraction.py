import helpers.decorators as decorators


@decorators.require_destinations
async def get(interaction, attraction_name, park_name):
    await interaction.response.send_message("Not implemented yet, sorry!")
