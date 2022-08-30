import lightbulb
import hikari
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


@sched.scheduled_job(CronTrigger(day="*/1"))
async def check_for_birthday_in_specified_weeks() -> None:
    """
    Checks if any birthdays are coming up, once a day specified by number of days.
    """
    servers = BirthdayCollection().get_all_servers()
    for server in servers:
        birthday_triggers = Birthday(server).get_any_close_birthdays([7, 14, 28])
        birthday_warning = "\n".join(f"{birthday.name} in {birthday.weeks_till_day} weeks from today"
                                     for birthday in birthday_triggers)
        channels = await daily_plugin.app.rest.fetch_guild_channels(server["serverid"])
        valid_channels = [channel for channel in channels if isinstance(channel, hikari.GuildTextChannel)]
        if len(birthday_triggers):
            try:
                await bot.rest.create_message(valid_channels[0], f"The following birthdays are coming up!:"
                                                                 f"\n{birthday_warning}\nDon't forget!")
            except hikari.errors.ForbiddenError:
                await bot.rest.create_message(valid_channels[1], f"The following birthdays are coming up!:"
                                                                 f"\n{birthday_warning}\nDon't forget!")


@bot.listen()
async def get_birthdays(event: hikari.MessageCreateEvent) -> None:
    """
    Gets the status of all birthdays in a given server.
    :param event: A message is sent to the server.
    """
    if event.is_bot or not event.content:
        return

    if event.content.startswith("birthdays"):
        await event.message.respond(Birthday(str(event.message.guild_id)).formatted_birthday_information())


@bot.listen()
async def data_manipulation_methods(event: hikari.MessageCreateEvent) -> None:
    """
    Handles all data manipulation message events.
    :param event: A message is sent in a server.
    """
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

bot.add_plugin(daily_plugin)
bot.run()
