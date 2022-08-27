from pymongo import MongoClient
from decouple import config
from datetime import datetime
import re


class BirthdayCollection:
    def __init__(self):
        self.collection = self.connect_to_birthday_collection()

    @staticmethod
    def connect_to_birthday_collection():
        client = MongoClient(config("MONGO_DB_CONN_URL"))
        db = client.get_database(config("MONGO_DB_NAME"))

        return db.get_collection(config("MONGO_BIRTHDAY_COLLECTION"))

    @staticmethod
    def date_is_correct_format(date: str):
        try:
            format_ddmmyyyy = "%d/%m/%Y"
            datetime.strptime(date, format_ddmmyyyy)

            return True
        except ValueError:

            return False

    def insert_new_birthday(self, calling_server: str, name: str, date: str):
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

    def update_existing_birthday(self, calling_server: str, name: str, date: str):
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

    def get_birthday_by_name(self, calling_server: str, queried_name: str):
        server = self.collection.find_one({"serverid": calling_server})
        birthdays = [birthday for birthday in server["birthdays"]]
        results = [name for name in birthdays if name["name"] == queried_name]

        return f"Birthday for {queried_name} is {results[0]['birthday']}! Let's celebrate!" \
            if len(results) \
            else f"Hmmm... Couldn't find a birthday for {queried_name} :("

    def get_all_birthdays(self, server):
        return [birthdays for birthdays in self.collection.find({"serverid": server})["birthdays"]]
