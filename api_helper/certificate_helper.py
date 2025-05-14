import psycopg2
from psycopg2.extras import RealDictCursor
from telegram.config import ConfigTelegram


class CertDBHelper:
    def __init__(self):
        self.conn = psycopg2.connect(
            host=ConfigTelegram.CERT_DB_HOST,
            port=int(ConfigTelegram.CERT_DB_PORT),
            dbname=ConfigTelegram.CERT_DB_NAME,
            user=ConfigTelegram.CERT_DB_USER,
            password=ConfigTelegram.CERT_DB_PASSWORD
        )

    def insert_certificate(self, email, student_name, course_name, date, otl=False):
        try:
            with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(
                    """
                    INSERT INTO certificates (faunaid, student_name, email, date, course_name, otl)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    RETURNING id
                    """,
                    (None, student_name, email, date, course_name, otl)
                )
                self.conn.commit()
                return cur.fetchone()["id"]
        except Exception as e:
            self.conn.rollback()
            raise Exception("Ошибка при создании сертификата:", e)

    def close(self):
        self.conn.close()