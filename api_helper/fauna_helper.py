from faunadb import query as q
import datetime
from faunadb.client import FaunaClient
from api_helper.config import ConfigApi


class FaunaHelper:

    clientf = FaunaClient(ConfigApi.fauna_key)

    @staticmethod
    def create_certify(student):
        return FaunaHelper.clientf.query(q.create(q.collection("Certificate"),
                                                  {"data": {
                                                      "student_name": student.name,
                                                      "email": student.email,
                                                      "date": "15 июля 2019",
                                                      "course_name": student.course.name,
                                                      "otl": False}
                                                  }))['ref'].value['id']


    @staticmethod
    def create_current_date_in_specific_format():
        current_date = None
