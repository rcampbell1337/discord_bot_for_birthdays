from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.database import Database
from decouple import config
from datetime import datetime


class BirthdayCollection:
    """
    Class representing the interactions with the remote MongoDB instance.
    """
    def __init__(self):
        self.collection = self.connect_to_birthday_collection()

    @staticmethod
    def connect_to_birthday_collection() -> Collection:
        """
        Connects to MongoDB and returns an instance of the birthday collection.
        :return: The birthday collection.
        """
        client = MongoClient(config("MONGO_DB_CONN_URL"))
        db = client.get_database(config("MONGO_DB_NAME"))

        return db.get_collection(config("MONGO_BIRTHDAY_COLLECTION"))

    @staticmethod
    def date_is_correct_format(date: str) -> bool:
        """
        Checks a given date is in the correct format for storage.
        :param date: The date to be checked.
        :return: Whether the date is in the correct format.
        """
        try:
            format_ddmmyyyy = "%d/%m/%Y"
            datetime.strptime(date, format_ddmmyyyy)

            return True
        except ValueError:

            return False

    def insert_new_birthday(self, calling_server: str, name: str, date: str) -> str:
        """
        Inserts a new birthday into the birthday collection for the server it has been called from.
        :param calling_server: The calling server.
        :param name: The birthday persons name.
        :param date: The date of the birthday.
        :return: Informative message of the insertion.
        """
        if not self.date_is_correct_format(date):
            return f"The date: '{date}' is in the incorrect format, please use dd/mm/yyyy."

        server = self.collection.find_one({"serverid": calling_server})
        if not server:

            is_inserted = self.collection.insert_one(
                {"serverid": calling_server, "birthdays": [{"name": name, "birthday": date}]})

            return f"Successfully inserted {name}'s birthday as {date}" \
                if is_inserted.acknowledged \
                else f"Could not save a birthday for {name}"

        birthdays = [birthday for birthday in server["birthdays"]]
        names = [name["name"] for name in birthdays]
        if name in names:

            return f"Sorry, but a birthday already exists for '{name}'" \
                   f", please try using a unique name."

        is_inserted = self.collection.update_one({"_id": server.get("_id")}, {"$push": {"birthdays": {
            "name": name,
            "birthday": date
        }}})

        return f"Successfully inserted {name}'s birthday as {date}" \
            if is_inserted.acknowledged \
            else f"Could not save a birthday for {name}"

    def update_existing_birthday(self, calling_server: str, name: str, date: str) -> str:
        """
        Checks a birthday exists for a given name then updates their birthday to a new value
        :param calling_server: The calling server.
        :param name: The birthday persons name.
        :param date: The date of the birthday.
        :return: Informative message of the update.
        Remarks
        ______
        This method basically allows for people who have accidentally entered the wrong birthday to rectify their error.
        (Yes it is a bit weird)
        """
        if not self.date_is_correct_format(date):

            return f"The date: '{date}' is in the incorrect format, please use dd/mm/yyyy."

        server = self.collection.find_one({"serverid": calling_server})
        if server:
            birthdays = [birthday for birthday in server["birthdays"]]
            names = [name["name"] for name in birthdays]
            if name in names:
                birthday_to_update = names.index(name)
                birthdays.pop(birthday_to_update)
                birthdays.append({
                    "name": name,
                    "birthday": date
                })
                is_updated = self.collection.update_one({"_id": server.get("_id")}, {"$set": {"birthdays": birthdays}})

                return f"Successfully updated {name}'s birthday to {date}" \
                    if is_updated.acknowledged \
                    else f"Could not save a birthday for {name}"

        return f"Could not find an existing birthday with the name: {name}"

    def get_birthday_by_name(self, calling_server: str, queried_name: str) -> str:
        """
        Gets a single birthday by name.
        :param calling_server: The calling server.
        :param queried_name: The birthday persons name.
        :return: The persons birthday.
        """
        # TODO: make this case insensitive
        server = self.collection.find_one({"serverid": calling_server})
        birthdays = [birthday for birthday in server["birthdays"]]
        results = [name for name in birthdays if name["name"] == queried_name]

        return f"Birthday for {queried_name} is {results[0]['birthday']}! Let's celebrate!" \
            if len(results) \
            else f"Hmmm... Couldn't find a birthday for {queried_name} :("

    def get_all_birthdays(self, server: str) -> list:
        """
        Gets all birthdays for a given server.
        :param server: The calling server.
        :return: A list of all birthdays for a given server.
        """
        return [birthdays for birthdays in self.collection.find_one({"serverid": server})["birthdays"]]

    def get_all_servers(self):
        return self.collection.find()
