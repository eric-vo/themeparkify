import asyncio

import aiohttp
import helpers.database as db
import helpers.decorators as decorators
import helpers.embed as embed
import helpers.themeparks as themeparks


@decorators.require_destinations
async def get(interaction, park_name, attraction_name, destination_name):
    destination_ids = db.get_user_destinations(interaction.user.id)

    async with aiohttp.ClientSession() as session:
        attractions = await themeparks.search_for_entities(
            session,
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

            tasks = []
            for i, attraction in enumerate(attractions):
                tasks.append(asyncio.create_task(
                    themeparks.get_entity(session, attraction["id"])
                ))

                if i >= embed.MAX_FIELDS - 1:
                    break

            entities = await asyncio.gather(*tasks)
            embed.add_addresses(error_embed, entities)

            return await interaction.response.send_message(embed=error_embed)

        attraction_entity = await themeparks.get_entity(
            session, attractions[0]["id"]
        )

        attraction_task, park_task = (
            asyncio.create_task(themeparks.get_entity(
                session, attractions[0]["id"], "live"
            )),
            asyncio.create_task(themeparks.get_entity(
                session, attraction_entity["parkId"]
            ))
        )

        live_attraction, park = await attraction_task, await park_task

    message_embed = embed.create_embed(
        live_attraction["name"], park["name"]
    )

    live_data = live_attraction["liveData"][0]

    wait = live_data['queue']['STANDBY']['waitTime']

    message_embed.add_field(
        name="Wait time",
        value=f"`{wait}` minutes" if wait is not None else f"`{wait}`",
        inline=False
    )
    message_embed.add_field(
        name="Status",
        value=f"`{live_data['status']}`",
        inline=False
    )

    # TODO: Add the wait forecast if it exists for that attraction
    # TODO: Add return times if it exists for that attraction

    # We can maybe add notifications
    # If a return time drops to within, say 1 hour of the current time

    # TODO: Add operating hours if they exist

    await interaction.response.send_message(embed=message_embed)


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
    await interaction.send_message(embeds=[message_embed])

    return False
