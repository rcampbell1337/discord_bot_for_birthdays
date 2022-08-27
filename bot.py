import hikari
from decouple import config
from birthday_logic import sort_birthdays_by_closest

bot = hikari.GatewayBot(config("BOT_TOKEN"))


@bot.listen()
async def test(event: hikari.MessageCreateEvent) -> None:
    if event.is_bot or not event.content:
        return

    if event.content.startswith("b!birthdays"):
        await event.message.respond(sort_birthdays_by_closest())

bot.run()
