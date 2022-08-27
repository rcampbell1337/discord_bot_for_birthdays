from datetime import datetime, date
from birthday_secrets import birthday_list
from collections import OrderedDict
from operator import getitem


def get_date_diff(birthday: str):
    split_year_from_birthday = "/".join(birthday.split("/")[:2])
    upcoming_date = datetime.strptime(split_year_from_birthday, "%d/%m")
    current_date = datetime.strptime(f"{datetime.now().day}/{datetime.now().month}", "%d/%m")
    number_of_days = int(str(upcoming_date - current_date).split(" ")[0])
    return number_of_days if number_of_days > 0 else 365 + number_of_days


def get_age_on_birthday(birthday: str):
    birth_year = birthday.split("/")[2]
    current_year = datetime.now().year
    return current_year - int(birth_year)


def sort_birthdays_by_closest():
    full_birthday_data = {
        name: {
               "birthday": f"{'/'.join(birthday_list[name].split('/')[:2])}/"
                           f"{determine_if_birthday_is_this_year_or_the_next(get_date_diff(birthday_list[name]))}",
               "time_till_birthday": get_date_diff(birthday_list[name]),
               "expected_age": get_age_on_birthday(birthday_list[name])
               }
        for name in birthday_list.keys()}
    return OrderedDict(sorted(full_birthday_data.items(), key=lambda item: getitem(item[1], 'time_till_birthday')))


def determine_if_birthday_is_this_year_or_the_next(time_till_birthday):
    today = datetime.now()
    return today.year \
        if time_till_birthday < ((date(today.year + 1, 1, 1)) - date(today.year, today.month, today.day)).days \
        else today.year + 1


def formatted_birthday_information():
    sorted_birthdays = sort_birthdays_by_closest()
    return "\n".join(f"{name} will be "
                     f"{sorted_birthdays[name]['expected_age']} on their birthday "
                     f"{sorted_birthdays[name]['birthday']}. this is "
                     f"{sorted_birthdays[name]['time_till_birthday']} days away."
                     for name in sorted_birthdays
                     if sorted_birthdays[name]['time_till_birthday'])

