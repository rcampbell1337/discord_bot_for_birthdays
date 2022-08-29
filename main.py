import lightbulb
import hikari
import discord
from decouple import config
from birthday_logic import Birthday
from mongodb import BirthdayCollection
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

bot = lightbulb.BotApp(
    token=config("BOT_TOKEN"),
    prefix="cake!",
    intents=hikari.Intents.ALL_MESSAGES,
    ignore_bots=True,
)

daily_plugin = lightbulb.Plugin("Daily")
sched = AsyncIOScheduler()
sched.start()


@sched.scheduled_job(CronTrigger(second="*/15"))
async def check_for_birthday_in_specified_weeks() -> None:
    servers = BirthdayCollection().get_all_servers()
    for server in servers:
        channels = await daily_plugin.app.rest.fetch_guild_channels(server["serverid"])

        valid_channels = [channel for channel in channels if isinstance(channel, hikari.GuildTextChannel)]
        await bot.rest.create_message(valid_channels[0], "hello world")


bot.add_plugin(daily_plugin)


@bot.listen()
async def get_birthdays(event: hikari.MessageCreateEvent) -> None:
    if event.is_bot or not event.content:
        return

    if event.content.startswith("birthdays"):
        await event.message.respond(Birthday(str(event.message.guild_id)).formatted_birthday_information())


@bot.listen()
async def get_birthday_by_name(event: hikari.MessageCreateEvent) -> None:
    birthday_coll = BirthdayCollection()
    if event.is_bot or not event.content:
        return

    if event.content.startswith("get"):
        await event.message.respond(
            birthday_coll.get_birthday_by_name(
                str(event.message.guild_id),
                " ".join(event.content.split()[1:])
            )
        )

    if event.content.startswith("all"):
        await event.message.respond(
            birthday_coll.get_all_birthdays(
                str(event.message.guild_id)
            )
        )

    if event.content.startswith("new"):
        await event.message.respond(
            birthday_coll.insert_new_birthday(
                str(event.message.guild_id),
                event.content.split()[1],
                event.content.split()[2]
            )
        )

    if event.content.startswith("update"):
        await event.message.respond(
            birthday_coll.update_existing_birthday(
                str(event.message.guild_id),
                event.content.split()[1],
                event.content.split()[2]
            )
        )

bot.run()
