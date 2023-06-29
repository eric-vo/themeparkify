import helpers.database as db
import helpers.embed as embed


def require_destinations(func):
    async def inner(interaction, *args, **kwargs):
        destinations = db.execute(
            "SELECT * FROM destinations WHERE user_id = ?",
            interaction.user.id
        )

        if not destinations:
            embed_message = embed.create_embed(
                "Error",
                "You have no destinations to search.\n"
                "Try using `/destination add`!"
            )

            await interaction.response.send_message(embeds=[embed_message])
            return

        await func(interaction, *args, **kwargs)

    return inner
