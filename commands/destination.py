import openapi_client

import helpers.database as db
import helpers.embed as embed
import helpers.themeparks as themeparks


async def add(interaction, destination_name):
    await interaction.response.defer()

    destinations = themeparks.search_for_destinations(
        destination_name
    )

    if not destinations:
        message_embed = embed.create_embed(
            "Error",
            f"No destinations found containing `{destination_name}`."
        )

        await interaction.followup.send(embeds=[message_embed])
        return

    if len(destinations) > 1:
        message_embed = embed.create_embed(
            "Error",
            "Multiple destinations were found containing "
            f"`{destination_name}`."
        )

        count = 0
        for destination in destinations:
            try:
                location = themeparks.get_entity(
                    destination["id"]
                )["location"]

                address = (
                    "[Google Maps]"
                    "(https://www.google.com/maps/place/"
                    f"{location['latitude']},{location['longitude']})"
                )
            except openapi_client.ApiAttributeError:
                address = ""

            message_embed.add_field(
                name=destination["name"],
                value=address,
                inline=False
            )

            if count >= embed.MAX_FIELDS - 1:
                break

            count += 1

        await interaction.followup.send(embeds=[message_embed])
        return

    destination_id = destinations[0]["id"]

    current_destinations = db.execute(
        "SELECT * FROM destinations WHERE user_id = ?",
        interaction.user.id
    )

    if len(current_destinations) >= 25:
        message_embed = embed.create_embed(
            "Error",
            "You have reached the max number of supported destinations (25).\n"
            "Try removing some with `/destination remove`!"
        )

        await interaction.followup.send(embeds=[message_embed])
        return

    duplicate_destinations = db.execute(
        "SELECT * FROM destinations WHERE user_id = ? AND destination_id = ?",
        interaction.user.id,
        destination_id
    )

    if not duplicate_destinations:
        db.execute(
            "INSERT INTO destinations (user_id, destination_id) "
            "VALUES (?, ?)",
            interaction.user.id,
            destination_id
        )

    message_embed = embed.create_embed(
        f"Added {destinations[0]['name']}!",
        "Here are your currently added destinations."
    )

    current_destinations = db.execute(
        "SELECT * FROM destinations WHERE user_id = ?",
        interaction.user.id
    )

    for destination in current_destinations:
        entity = themeparks.get_entity(destination["destination_id"])

        try:
            location = entity["location"]
            address = (
                "[Google Maps]"
                "(https://www.google.com/maps/place/"
                f"{location['latitude']},{location['longitude']})"
            )
        except openapi_client.ApiAttributeError:
            address = ""

        message_embed.add_field(
            name=entity["name"],
            value=address,
            inline=False
        )

    await interaction.followup.send(embeds=[message_embed])


async def remove(interaction, destination_name):
    await interaction.response.defer()

    destinations = db.execute(
        "SELECT * FROM destinations WHERE user_id = ?", interaction.user.id
    )

    destination_name = destination_name.strip().lower()

    matches = []
    remaining_entities = []

    for destination in destinations:
        entity = themeparks.get_entity(destination["destination_id"])

        if destination_name in entity["name"].lower():
            matches.append(entity)
        else:
            remaining_entities.append(entity)

    if not matches:
        message_embed = embed.create_embed(
            "Error",
            f"No destinations found containing `{destination_name}`."
        )

        await interaction.followup.send(embeds=[message_embed])
        return

    if len(matches) > 1:
        message_embed = embed.create_embed(
            "Error",
            "Multiple destinations were found containing "
            f"`{destination_name}`."
        )

        for match in matches:
            try:
                location = match["location"]

                address = (
                    "[Google Maps]"
                    "(https://www.google.com/maps/place/"
                    f"{location['latitude']},{location['longitude']})"
                )
            except openapi_client.ApiAttributeError:
                address = ""

            message_embed.add_field(
                name=match["name"],
                value=address,
                inline=False
            )

        await interaction.followup.send(embeds=[message_embed])
        return

    db.execute(
        "DELETE FROM destinations WHERE user_id = ? AND destination_id = ?",
        interaction.user.id,
        matches[0]["id"]
    )

    message_embed = embed.create_embed(
        f"Removed {matches[0]['name']}!",
        "Here are your currently added destinations."
    )

    for entity in remaining_entities:
        try:
            location = entity["location"]
            address = (
                "[Google Maps]"
                "(https://www.google.com/maps/place/"
                f"{location['latitude']},{location['longitude']})"
            )
        except openapi_client.ApiAttributeError:
            address = ""

        message_embed.add_field(
            name=entity["name"],
            value=address,
            inline=False
        )

    await interaction.followup.send(embeds=[message_embed])
