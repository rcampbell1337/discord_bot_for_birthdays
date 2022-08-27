import hikari
from decouple import config
from birthday_logic import formatted_birthday_information

bot = hikari.GatewayBot(config("BOT_TOKEN"))


@bot.listen()
async def test(event: hikari.MessageCreateEvent) -> None:
    if event.is_bot or not event.content:
        return

    if event.content.startswith("bb!birthdays"):
        await event.message.respond(formatted_birthday_information())

bot.run()
