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

    def update_existing_birthday(self, server: str, name: str, date: str):
        if not self.date_is_correct_format(date):
            return f"The date: '{date}' is in the incorrect format, please use dd/mm/yyyy."
        current_name = self.search_for_case_insensitive_name(server, name)
        if current_name:
            is_updated = self.collection.replace_one(
                {'_id': current_name.get('_id')},
                {server: {"name": name, "birthday": date}},
                upsert=True
            )
            return f"Successfully updated {name}'s birthday to {date}" \
                if is_updated.acknowledged \
                else f"Could not update the bithday for {name}."
        return f"Could not find an existing birthday with the name: {name}"

    def get_birthday_by_name(self, server: str, name: str):
        results = self.search_for_case_insensitive_name(server, name)
        return f"Birthday for {name} is {results['birthday']}! Let's celebrate!" \
            if results \
            else f"Hmmm... Couldn't find a birthday for {name} :("

    def get_all_birthdays(self, server):
        return [x for x in self.collection.find(server)]

    def search_for_case_insensitive_name(self, server: str, name: str):
        regx = re.compile(f"^{name}", re.IGNORECASE)
        return self.collection.find_one({server: {"name": regx}})
