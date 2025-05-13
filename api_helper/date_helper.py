import datetime

class DateHelper:

    @staticmethod
    def create_current_date_in_specific_format():
        current_date = datetime.date.today()
        current_date = str(current_date).split('-')
        return f'{int(current_date[2])} {DateHelper.replace_number_date_to_string(current_date[1])} {int(current_date[0])}'

    @staticmethod
    def replace_number_date_to_string(number_date):
        d = {
            "01": "января",
            "02": "февраля",
            "03": "марта",
            "04": "апреля",
            "05": "мая",
            "06": "июня",
            "07": "июля",
            "08": "августа",
            "09": "сентября",
            "10": "октября",
            "11": "ноября",
            "12": "декабря"
        }
        return d[number_date]