import lightbulb
import hikari
from decouple import config
from birthday_logic import Birthday
from mongodb import BirthdayCollection
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from youtube import get_first_yt_video

bot = lightbulb.BotApp(
    token=config("BOT_TOKEN"),
    intents=hikari.Intents.ALL_MESSAGES,
    ignore_bots=True,
)

daily_plugin = lightbulb.Plugin("Daily")
sched = AsyncIOScheduler()
sched.start()


@sched.scheduled_job(CronTrigger(day="*", hour="10", minute="30"))
async def check_for_birthday_in_specified_weeks() -> None:
    """
    Checks if any birthdays are coming up or are today, once a day specified by number of days.
    """
    servers = BirthdayCollection().get_all_servers()
    for server in servers:
        birthdays_for_server = Birthday(server)

        # Gets a list of the close birthdays
        birthday_triggers = birthdays_for_server.get_any_close_birthdays([7, 14, 28])

        # Gets actual birthdays
        birthdays_today = birthdays_for_server.get_any_close_birthdays([0])

        channels = await daily_plugin.app.rest.fetch_guild_channels(server["serverid"])
        valid_channels = [channel for channel in channels if isinstance(channel, hikari.GuildTextChannel)]

        # Handle Birthday events
        if len(birthdays_today):
            birthday_message = "\n".join(f"{birthday.name} HAPPY BIRTHDAY!!!\n{get_first_yt_video(birthday.name)}"
                                         for birthday in birthdays_today)

            await try_to_send_to_channel(valid_channels, f"OMG IT'S BIRTHDAY TIME!!!:"
                                                         f"\n{birthday_message}\n:cupcake:")

        # Handle upcoming birthday events.
        if len(birthday_triggers):
            birthday_warning = "\n".join(f"{birthday.name.upper()} in {birthday.weeks_till_day} "
                                         f"week{'s' if birthday.weeks_till_day != 1 else ''} from today"
                                         for birthday in birthday_triggers)

            await try_to_send_to_channel(valid_channels, f"The following birthdays are coming up!:"
                                                         f"\n{birthday_warning}\nDon't forget! :anger:")


async def try_to_send_to_channel(channels: list, message: str, channel_index=0):
    """
    An recursive helper method that will only send a message to a channel which the bot has permissions to see.
    :param channels: A list of valid channels.
    :param message: The message to be sent.
    :param channel_index: The channel to try to send a message too.
    :return: If no channels can be found.
    """
    try:
        await bot.rest.create_message(channels[channel_index], message)
    except hikari.errors.ForbiddenError:
        await try_to_send_to_channel(channels, message, channel_index + 1)
    except IndexError:
        return


@bot.listen()
async def get_birthdays(event: hikari.MessageCreateEvent) -> None:
    """
    Gets the status of all birthdays in a given server.
    :param event: A message is sent to the server.
    """
    if event.is_bot or not event.content:
        return

    if event.content.startswith("cake!birthdays"):
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

    if event.content.startswith("cake!get"):
        await event.message.respond(
            birthday_coll.get_birthday_by_name(
                str(event.message.guild_id),
                " ".join(event.content.split()[1:])
            )
        )

    if event.content.startswith("cake!all"):
        await event.message.respond(
            birthday_coll.get_all_birthdays(
                str(event.message.guild_id)
            )
        )

    if event.content.startswith("cake!new"):
        await event.message.respond(
            birthday_coll.insert_new_birthday(
                str(event.message.guild_id),
                event.content.split()[1],
                event.content.split()[2]
            )
        )

    if event.content.startswith("cake!update"):
        await event.message.respond(
            birthday_coll.update_existing_birthday(
                str(event.message.guild_id),
                event.content.split()[1],
                event.content.split()[2]
            )
        )

bot.add_plugin(daily_plugin)
bot.run()
