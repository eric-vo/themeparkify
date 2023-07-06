import asyncio

import aiohttp
import helpers.database as db
import helpers.decorators as decorators
import helpers.embed as embed
import helpers.themeparks as themeparks


async def clear_tracked(interaction):
    await interaction.response.defer()

    db.execute("DELETE FROM tracks WHERE user_id = ?", interaction.user.id)

    success_embed = create_attractions_embed("Cleared tracked attractions!")
    add_no_attractions(success_embed)

    await interaction.followup.send(embed=success_embed)


@decorators.require_destinations
async def get(interaction, attraction_name, park_name, destination_name):
    await interaction.response.defer()

    destination_ids = db.get_user_destination_ids(interaction.user.id)

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
            await embed.add_addresses(error_embed, entities, session)

            return await interaction.followup.send(embed=error_embed)

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

    if "queue" in live_data:
        wait = live_data['queue']['STANDBY']['waitTime']
    else:
        wait = None

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

    await interaction.followup.send(embed=message_embed)


@decorators.require_destinations
async def track(
    interaction, attraction_name, wait_threshold, park_name, destination_name
):
    await interaction.response.defer()

    current_tracks = db.get_user_tracks(interaction.user.id)

    if len(current_tracks) >= 25:
        error_embed = embed.create_error_embed(
            "You have reached the max number of "
            "tracked attractions allowed (25).\n"
            "Try removing some with `/attraction untrack`!"
        )

        return await interaction.followup.send(embed=error_embed)

    destination_ids = db.get_user_destination_ids(interaction.user.id)

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
            await embed.add_addresses(error_embed, entities, session)

            return await interaction.followup.send(embed=error_embed)

        duplicates = db.execute(
            "SELECT * FROM tracks "
            "WHERE user_id = ? "
            "AND attraction_id = ?",
            interaction.user.id,
            attractions[0]["id"]
        )

        if duplicates:
            db.execute(
                "UPDATE tracks SET wait_threshold = ? "
                "WHERE user_id = ?",
                wait_threshold,
                interaction.user.id
            )
        else:
            db.execute(
                "INSERT INTO tracks (user_id, attraction_id, wait_threshold) "
                "VALUES (?, ?, ?)",
                interaction.user.id,
                attractions[0]["id"],
                wait_threshold
            )

        success_embed = create_attractions_embed(
            f"Tracked {attractions[0]['name']}!"
        )

        tracks = db.get_user_tracks(interaction.user.id)

        tasks = []
        wait_thresholds = tuple(row["wait_threshold"] for row in tracks)
        for row in tracks:
            tasks.append(asyncio.create_task(
                themeparks.get_entity(session, row["attraction_id"])
            ))

        entities = await asyncio.gather(*tasks)

        await embed.add_addresses(
            success_embed, entities, session, wait_thresholds
        )

    await interaction.followup.send(embed=success_embed)


@decorators.require_destinations
async def untrack(interaction, attraction_name, park_name, destination_name):
    await interaction.response.defer()

    destination_ids = db.get_user_destination_ids(interaction.user.id)

    async with aiohttp.ClientSession() as session:
        attractions = await themeparks.search_for_entities(
            session,
            attraction_name,
            destination_ids,
            park_name,
            destination_name,
            "attraction"
        )

        tracks = db.get_user_tracks(interaction.user.id)

        matching_ids = []
        matching_name = None
        for attraction in attractions:
            for row in tracks:
                if attraction["id"] == row["attraction_id"]:
                    matching_ids.append(attraction["id"])
                    matching_name = attraction["name"]

        if not await validate_attractions(
            interaction, matching_ids, attraction_name
        ):
            return

        if len(matching_ids) > 1:
            error_embed = embed.create_search_error_embed(
                "Multiple attractions", attraction_name
            )

            tasks = []
            for match in matching_ids:
                tasks.append(asyncio.create_task(
                    themeparks.get_entity(session, match)
                ))

            entities = await asyncio.gather(*tasks)
            await embed.add_addresses(error_embed, entities, session)

            return await interaction.followup.send(embed=error_embed)

        db.execute(
            "DELETE FROM tracks "
            "WHERE user_id = ? "
            "AND attraction_id = ?",
            interaction.user.id,
            matching_ids[0]
        )

        success_embed = create_attractions_embed(
            f"Untracked {matching_name}!"
        )

        tracks = db.get_user_tracks(interaction.user.id)

        if tracks:
            tasks = []
            wait_thresholds = tuple(row["wait_threshold"] for row in tracks)
            for row in tracks:
                tasks.append(asyncio.create_task(
                    themeparks.get_entity(session, row["attraction_id"])
                ))

            entities = await asyncio.gather(*tasks)

            await embed.add_addresses(
                success_embed, entities, session, wait_thresholds
            )
        else:
            add_no_attractions(success_embed)

    await interaction.followup.send(embed=success_embed)


async def view_tracked(interaction):
    await interaction.response.defer()

    tracks = db.get_user_tracks(interaction.user.id)

    message_embed = create_attractions_embed("Tracked attractions")

    if tracks:
        tasks = []

        thresholds = []

        async with aiohttp.ClientSession() as session:
            for row in tracks:
                tasks.append(asyncio.create_task(
                    themeparks.get_entity(session, row["attraction_id"])
                ))

                thresholds.append(row["wait_threshold"])

            entities = await asyncio.gather(*tasks)

            await embed.add_addresses(
                message_embed, entities, session, thresholds
            )
    else:
        add_no_attractions(message_embed)

    await interaction.followup.send(embed=message_embed)


def add_no_attractions(embed):
    embed.add_field(name="You have no tracked attractions.", value="")


def create_attractions_embed(title):
    message_embed = embed.create_embed(
        title, "Here are your currently tracked attractions."
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


async def validate_attractions(interaction, attractions, attraction_name):
    if attractions:
        return True

    message_embed = create_search_error_embed(
        "No attractions", attraction_name
    )
    await interaction.followup.send(embed=message_embed)

    return False
