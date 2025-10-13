# app/services/student_course_summary_service.py
import mysql.connector
import os

class StudentCourseSummaryService:
    @staticmethod
    def _get_conn():
        return mysql.connector.connect(
            host=os.getenv("DB_HOST", "localhost"),
            user=os.getenv("DB_USER", "root"),
            password=os.getenv("DB_PASS", ""),
            database=os.getenv("DB_NAME", "exam_scheduler"),
            autocommit=True
        )

    # --------------------------------------------------------
    # 1️⃣ Öğrenci numarasına göre getir
    # --------------------------------------------------------
    @staticmethod
    def get_by_student_number(student_number: str):
        sql = """
            SELECT `Öğrenci No`, `Ad Soyad`, `Sınıf`, `Dersin Kodu`, `Aldığı Ders`
            FROM student_course_summary
            WHERE `Öğrenci No` = %s
            ORDER BY `Dersin Kodu`
        """
        with StudentCourseSummaryService._get_conn() as conn:
            cur = conn.cursor(dictionary=True)
            cur.execute(sql, (student_number,))
            return cur.fetchall()

    # --------------------------------------------------------
    # 2️⃣ Ders koduna göre getir
    # --------------------------------------------------------
    @staticmethod
    def get_by_course_code(course_code: str):
        sql = """
            SELECT `Öğrenci No`, `Ad Soyad`, `Sınıf`, `Dersin Kodu`, `Aldığı Ders`
            FROM student_course_summary
            WHERE `Dersin Kodu` = %s
            ORDER BY `Öğrenci No`
        """
        with StudentCourseSummaryService._get_conn() as conn:
            cur = conn.cursor(dictionary=True)
            cur.execute(sql, (course_code,))
            return cur.fetchall()

    # --------------------------------------------------------
    # 3️⃣ Tüm dersleri listele
    # --------------------------------------------------------
    @staticmethod
    def list_all_courses():
        sql = """
            SELECT DISTINCT `Dersin Kodu`, `Aldığı Ders`
            FROM student_course_summary
            ORDER BY `Dersin Kodu`
        """
        with StudentCourseSummaryService._get_conn() as conn:
            cur = conn.cursor(dictionary=True)
            cur.execute(sql)
            return cur.fetchall()
