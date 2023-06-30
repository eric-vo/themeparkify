import helpers.database as db
import helpers.decorators as decorators
import helpers.embed as embed
import helpers.themeparks as themeparks


@decorators.require_destinations
async def get(interaction, park_name, attraction_name, destination_name):
    await interaction.response.defer()

    destination_ids = db.get_user_destinations(interaction.user.id)

    attractions = themeparks.search_for_entities(
        attraction_name,
        destination_ids,
        park_name,
        destination_name,
        "attraction"
    )

    if not await validate_attractions(
        interaction, attractions, attraction_name
    ):
        return

    if len(attractions) > 1:
        error_embed = embed.create_search_error_embed(
            "Multiple attractions", attraction_name
        )
        error_embed.add_field(
            name="Fetching matching attractions...", value=""
        )
        await interaction.followup.send(embeds=[error_embed])

        error_embed.clear_fields()

        for i, attraction in enumerate(attractions):
            entity = themeparks.get_entity(attraction["id"])
            embed.add_address(error_embed, entity)

            if i >= embed.MAX_FIELDS - 1:
                break

        return await interaction.edit_original_response(embeds=[error_embed])

    attraction_data = themeparks.get_entity(attractions[0]["id"], "live")

    attraction_embed = embed.create_embed(
        attraction_data["name"], attractions[0]["park_name"]
    )

    attraction = attraction_data['live_data'][0]

    attraction_embed.add_field(
        name="Wait time",
        value=f"`{attraction['queue']['STANDBY']['waitTime']}` minutes",
        inline=False
    )
    attraction_embed.add_field(
        name="Status",
        value=f"`{attraction['status']}`",
        inline=False
    )

    # TODO: Add the wait forecast if it exists for that attraction
    # TODO: Add return times if it exists for that attraction

    # We can maybe add notifications
    # If a return time drops to within, say 1 hour of the current time

    # TODO: Add operating hours if they exist

    await interaction.followup.send(embeds=[attraction_embed])


def create_error_embed(error):
    error_embed = embed.create_embed("Error", error)
    return error_embed


def create_search_error_embed(error, query_name):
    error_embed = create_error_embed(
        f"{error} were found containing `{query_name}`."
    )
    return error_embed


async def validate_attractions(interaction, attractions, attraction_name):
    if attractions:
        return True

    message_embed = create_search_error_embed(
        "No attractions", attraction_name
    )
    await interaction.followup.send(embeds=[message_embed])

    return False
