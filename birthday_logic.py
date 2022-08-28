from datetime import datetime, date
from mongodb import BirthdayCollection
from collections import OrderedDict
from operator import getitem


class Birthday:
    def __init__(self, server):
        self.birthday_list = BirthdayCollection().get_all_birthdays(server)

    @staticmethod
    def get_date_diff(birthday: str):
        split_year_from_birthday = "/".join(birthday.split("/")[:2])
        upcoming_date = datetime.strptime(split_year_from_birthday, "%d/%m")
        current_date = datetime.strptime(f"{datetime.now().day}/{datetime.now().month}", "%d/%m")
        number_of_days = int(str(upcoming_date - current_date).split(" ")[0])
        return number_of_days if number_of_days > 0 else 365 + number_of_days

    @staticmethod
    def get_age_on_birthday(birthday: str):
        birth_year = birthday.split("/")[2]
        current_year = datetime.now().year
        return current_year - int(birth_year)

    @staticmethod
    def determine_if_birthday_is_this_year_or_the_next(days_away):
        today = datetime.now()
        return today.year \
            if days_away < ((date(today.year + 1, 1, 1)) - date(today.year, today.month, today.day)).days \
            else today.year + 1

    def sort_birthdays_by_closest(self):
        full_birthday_data = {
            birthday["name"]: {
                   "birthday": f"{'/'.join(birthday['birthday'].split('/')[:2])}/"
                               f"{self.determine_if_birthday_is_this_year_or_the_next(self.get_date_diff(birthday['birthday']))}",
                   "days_away": self.get_date_diff(birthday['birthday']),
                   "expected_age": self.get_age_on_birthday(birthday['birthday'])
                   }
            for birthday in self.birthday_list}
        return OrderedDict(sorted(full_birthday_data.items(), key=lambda item: getitem(item[1], 'days_away')))

    def formatted_birthday_information(self):
        birthdays = self.sort_birthdays_by_closest()
        later_birthdays = [name for name in list(birthdays.keys())[:-1] if birthdays[name]['days_away'] > 60]
        birthdays_coming_up = "\n".join(f"{name} will be "
                                        f"{birthdays[name]['expected_age']} on their birthday "
                                        f"{birthdays[name]['birthday']}. This is "
                                        f"{birthdays[name]['days_away']} days away."
                                        for name in birthdays
                                        if birthdays[name]['days_away'] <= 60)
        other_birthdays = f"{', '.join(later_birthdays)}"\
                          f" and {list(birthdays.keys())[-1]}'s birthdays are still over 60 days away."
        return f"{birthdays_coming_up}\n" \
               f"{other_birthdays if len(later_birthdays) else ''}"

