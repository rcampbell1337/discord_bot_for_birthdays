import hikari
from decouple import config
from birthday_logic import formatted_birthday_information
from mongodb import BirthdayCollection

bot = hikari.GatewayBot(config("BOT_TOKEN"))


@bot.listen()
async def get_birthdays(event: hikari.MessageCreateEvent) -> None:
    if event.is_bot or not event.content:
        return

    if event.content.startswith("cake!birthdays"):
        await event.message.respond(formatted_birthday_information())


@bot.listen()
async def get_birthday_by_name(event: hikari.MessageCreateEvent) -> None:
    birthday_coll = BirthdayCollection()
    if event.is_bot or not event.content:
        return

    if event.content.startswith("cake!get"):
        await event.message.respond(
            birthday_coll.get_birthday_by_name(
                event.channel_id,
                " ".join(event.content.split()[1:])
            )
        )

    if event.content.startswith("cake!all"):
        await event.message.respond(
            birthday_coll.get_all_birthdays(
                event.channel_id)
        )

    if event.content.startswith("cake!new"):
        await event.message.respond(
            birthday_coll.insert_new_birthday(
                str(event.message.guild_id),
                event.content.split()[1],
                event.content.split()[2]
            )
        )

bot.run()
