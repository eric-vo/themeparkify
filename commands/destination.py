import openapi_client

import helpers.database as db
import helpers.embed as embed
import helpers.themeparks as themeparks


async def add(interaction, destination_name):
    await interaction.response.defer()

    current_destinations = get_user_destinations(interaction)

    if len(current_destinations) >= 25:
        error_embed = create_error_embed(
            "You have reached the max number of supported destinations (25).\n"
            "Try removing some with `/destination remove`!"
        )

        return await interaction.followup.send(embeds=[error_embed])

    destinations = themeparks.search_for_destinations(
        destination_name
    )

    if not await validate_destinations(
        interaction, destinations, destination_name
    ):
        return

    if len(destinations) > 1:
        error_embed = create_search_error_embed(
            "Multiple destinations", destination_name
        )
        error_embed.add_field(
            name="Fetching matching destinations...", value=""
        )
        await interaction.followup.send(embeds=[error_embed])

        error_embed.clear_fields()

        for i, destination in enumerate(destinations):
            entity = themeparks.get_entity(destination["id"])
            add_address(error_embed, entity)

            if i >= embed.MAX_FIELDS - 1:
                break

        return await interaction.edit_original_response(embeds=[error_embed])

    destination_id = destinations[0]["id"]

    duplicate_destinations = db.execute(
        "SELECT * FROM destinations WHERE user_id = ? AND destination_id = ?",
        interaction.user.id,
        destination_id
    )

    if duplicate_destinations:
        error_embed = create_error_embed(
            destinations[0]['name']
            + " is already in your list of destinations!"
        )

        return await interaction.followup.send(embeds=[error_embed])

    db.execute(
        "INSERT INTO destinations (user_id, destination_id) "
        "VALUES (?, ?)",
        interaction.user.id,
        destination_id
    )

    success_embed = create_destinations_embed(
        f"Added {destinations[0]['name']}!"
    )

    current_destinations = get_user_destinations(interaction)

    for destination in current_destinations:
        entity = themeparks.get_entity(destination["destination_id"])
        add_address(success_embed, entity)

    await interaction.followup.send(embeds=[success_embed])


async def remove(interaction, destination_name):
    await interaction.response.defer()

    current_destinations = get_user_destinations(interaction)

    destination_name = destination_name.strip().lower()

    matches = []
    remaining_entities = []

    for destination in current_destinations:
        entity = themeparks.get_entity(destination["destination_id"])

        if destination_name in entity["name"].lower():
            matches.append(entity)
        else:
            remaining_entities.append(entity)

    if not await validate_destinations(
        interaction, matches, destination_name
    ):
        return

    if len(matches) > 1:
        error_embed = create_search_error_embed(
            "Multiple destinations", destination_name
        )
        error_embed.add_field(
            name="Fetching matching destinations...", value=""
        )
        await interaction.followup.send(embeds=[error_embed])

        error_embed.clear_fields()

        for match in matches:
            add_address(error_embed, match)

        return await interaction.edit_original_response(embeds=[error_embed])

    db.execute(
        "DELETE FROM destinations WHERE user_id = ? AND destination_id = ?",
        interaction.user.id,
        matches[0]["id"]
    )

    success_embed = create_destinations_embed(f"Removed {matches[0]['name']}!")

    if remaining_entities:
        for entity in remaining_entities:
            add_address(success_embed, entity)
    else:
        add_no_destinations(success_embed)

    await interaction.followup.send(embeds=[success_embed])


async def view(interaction):
    await interaction.response.defer()

    destinations = get_user_destinations(interaction)

    message_embed = create_destinations_embed("Destinations")

    if destinations:
        for destination in destinations:
            entity = themeparks.get_entity(destination["destination_id"])
            add_address(message_embed, entity)
    else:
        add_no_destinations(message_embed)

    await interaction.followup.send(embeds=[message_embed])


def add_address(embed, entity):
    try:
        location = entity["location"]
        address = (
            "[Google Maps]"
            "(https://www.google.com/maps/place/"
            f"{location['latitude']},{location['longitude']})"
        )
    except openapi_client.ApiAttributeError:
        address = ""

    embed.add_field(
        name=entity["name"],
        value=address,
        inline=False
    )


def add_no_destinations(embed):
    embed.add_field(name="You have no added destinations.", value="")


def create_destinations_embed(title):
    message_embed = embed.create_embed(
        title, "Here are your currently added destinations."
    )
    return message_embed


def create_error_embed(error):
    error_embed = embed.create_embed("Error", error)
    return error_embed


def create_search_error_embed(error, query_name):
    error_embed = create_error_embed(
        f"{error} were found containing `{query_name}`."
    )
    return error_embed


def get_user_destinations(interaction):
    return db.execute(
        "SELECT * FROM destinations WHERE user_id = ?",
        interaction.user.id
    )


async def validate_destinations(interaction, destinations, destination_name):
    if destinations:
        return True

    message_embed = create_search_error_embed(
        "No destinations", destination_name
    )
    await interaction.followup.send(embeds=[message_embed])

    return False
