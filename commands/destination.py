import openapi_client

import helpers.database as db
import helpers.embed as embed
import helpers.themeparks as themeparks


async def add(interaction, destination_name):
    await interaction.response.defer()

    try:
        destinations = themeparks.search_for_destinations(
            destination_name
        )
    except openapi_client.ApiException as e:
        message_embed = embed.create_embed("Error", e)

        await interaction.followup.send(embeds=[message_embed])
        return

    print(destinations)

    if not destinations:
        message_embed = embed.create_embed(
            "Error",
            f"No destinations found containing **{destination_name}**."
        )

        await interaction.followup.send(embeds=[message_embed])
        return

    if len(destinations) > 1:
        message_embed = embed.create_embed(
            "Error",
            "Multiple destinations were found containing "
            f"**{destination_name}**."
        )

        for destination in destinations:
            print("field")
            try:
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
            except openapi_client.ApiException as e:
                message_embed = embed.create_embed("Error", e)

                await interaction.followup.send(embeds=[message_embed])
                return

            message_embed.add_field(
                name=destination["name"],
                value=address,
                inline=False
            )

        await interaction.followup.send(embeds=[message_embed])
        return

    destination_id = destinations[0]["id"]

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

    if current_destinations is not None:
        for destination in current_destinations:
            try:
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
            except openapi_client.ApiException as e:
                message_embed = embed.create_embed("Error", e)

                await interaction.followup.send(embeds=[message_embed])
                return

            message_embed.add_field(
                name=destination["name"],
                value=address,
                inline=False
            )

    await interaction.followup.send(embeds=[message_embed])
