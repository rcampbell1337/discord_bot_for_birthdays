import math
from dataclasses import dataclass
from datetime import datetime, date
from typing import List

from mongodb import BirthdayCollection
from collections import OrderedDict
from operator import getitem


@dataclass
class BirthdayPerson:
    """ Class for storing birthday information. """
    name: str
    weeks_till_day: int


class Birthday:
    """ Class representing all birthday logic. """
    def __init__(self, server):
        self.birthday_list = BirthdayCollection().get_all_birthdays(server["serverid"])

    @staticmethod
    def get_date_diff(birthday: str) -> int:
        """
        Gets the number of days between now and someones birthday.
        :param birthday:v
        :return: The number of days between two dates.
        """
        split_year_from_birthday = "/".join(birthday.split("/")[:2])
        upcoming_date = datetime.strptime(split_year_from_birthday, "%d/%m")
        current_date = datetime.strptime(f"{datetime.now().day}/{datetime.now().month}", "%d/%m")
        number_of_days = int(str(upcoming_date - current_date).split(" ")[0])
        return number_of_days if number_of_days > 0 else 365 + number_of_days

    @staticmethod
    def get_age_on_birthday(birthday: str) -> int:
        """
        Gets how old a person will be on their birthday.
        :param birthday: The persons birthday.
        :return: The persons age on their birthday.
        """
        birth_year = birthday.split("/")[2]
        current_year = datetime.now().year
        return current_year - int(birth_year)

    @staticmethod
    def determine_if_birthday_is_this_year_or_the_next(days_away: int) -> int:
        """
        Determines if the year to be shown against when their birthday is should be this year or the next.
        :param days_away: Number of days till the persons birthday.
        :return: The persons birthday year.
        Example:
        _______
        If someone will be 23 on the first of Jan next year, as it is written without this method it will return:
        01/01/current_year.
        Parsed with method:
        01/01/next_year
        """
        today = datetime.now()
        return today.year \
            if days_away < ((date(today.year + 1, 1, 1)) - date(today.year, today.month, today.day)).days \
            else today.year + 1

    def sort_birthdays_by_closest(self) -> OrderedDict:
        """
        Sorts the birthdays by whose how far away it is in days.
        :return: A sorted birthday list by how far away it is in days.
        """
        full_birthday_data = {
            birthday["name"]: {
                   "birthday": f"{'/'.join(birthday['birthday'].split('/')[:2])}/"
                               f"{self.determine_if_birthday_is_this_year_or_the_next(self.get_date_diff(birthday['birthday']))}",
                   "days_away": self.get_date_diff(birthday['birthday']),
                   "expected_age": self.get_age_on_birthday(birthday['birthday'])
                   }
            for birthday in self.birthday_list}
        return OrderedDict(sorted(full_birthday_data.items(), key=lambda item: getitem(item[1], 'days_away')))

    def formatted_birthday_information(self) -> str:
        """
        Returns the sorted birthday list in a human readable format.
        :return: The sorted birthday list in a human readable format.
        """
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

    def get_any_close_birthdays(self, distance_to_check: List[int]) -> List[BirthdayPerson]:
        """
        Lists all birthdays which are close to the current date.
        :param distance_to_check: A list of days to check.
        :return: All birthdays which are close to the current date.
        """
        return [
            BirthdayPerson(
                name=birthday["name"],
                weeks_till_day=math.floor(self.get_date_diff(birthday["birthday"]) / 7)
            )
            for birthday in self.birthday_list
            if self.get_date_diff(birthday["birthday"]) in distance_to_check]

