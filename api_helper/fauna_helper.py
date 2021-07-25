from faunadb import query as q
import datetime
from faunadb.client import FaunaClient
from api_helper.config import ConfigApi


class FaunaHelper:

    clientf = FaunaClient(ConfigApi.fauna_key)
    discount_coupon_id = 236782992568091143

    @staticmethod
    def create_certify(student):
        return FaunaHelper.clientf.query(q.create(q.collection("Certificate"),
                                                  {"data": {
                                                      "student_name": student.name,
                                                      "email": student.email,
                                                      "date": FaunaHelper.create_current_date_in_specific_format(),
                                                      "course_name": student.course.name.split(',')[0],
                                                      "otl": False}
                                                  }))['ref'].value['id']

    @staticmethod
    def create_current_date_in_specific_format():
        current_date = datetime.date.today()
        current_date = str(current_date).split('-')
        return f'{int(current_date[2])} {FaunaHelper.replace_number_date_to_string(current_date[1])} {int(current_date[0])}'

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

    @staticmethod
    def get_discount_coupon():
        return FaunaHelper.clientf.query(q.get(q.ref(q.collection("Info"), FaunaHelper.discount_coupon_id)))['data']['Купон_скидка']
