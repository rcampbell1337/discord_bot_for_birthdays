from datetime import datetime
from birthday_secrets import birthday_list

def get_date_diff(birthday: str):
    split_year_from_birthday = "/".join(birthday.split("/")[:2])
    upcoming_date = datetime.strptime(split_year_from_birthday, "%d/%m")
    current_date = datetime.strptime(f"{datetime.now().day}/{datetime.now().month}", "%d/%m")
    number_of_days = int(str(upcoming_date - current_date).split(" ")[0])
    return number_of_days if number_of_days > 0 else 365 + number_of_days


def sort_birthdays_by_closest():
    days_till_birthdays = {x: get_date_diff(birthday_list[x]) for x in birthday_list.keys()}
    return dict(sorted(days_till_birthdays.items(), key=lambda item: item[1]))