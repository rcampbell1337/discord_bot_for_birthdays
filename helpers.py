from datetime import datetime


def get_date_diff(birthday: str) -> int:
        """
        Gets the number of days between now and someones birthday.
        :param: The persons birthday.
        :return: The number of days between two dates.
        """
        split_year_from_birthday = "/".join(birthday.split("/")[:2])
        upcoming_date = datetime.strptime(split_year_from_birthday, "%d/%m")
        current_date = datetime.strptime(f"{datetime.now().day}/{datetime.now().month}", "%d/%m")
        if current_date == upcoming_date:
            return 0
        number_of_days = int(str(upcoming_date - current_date).split(" ")[0])
        return number_of_days if number_of_days >= 0 else 365 + number_of_days