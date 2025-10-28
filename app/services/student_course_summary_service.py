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
    def get_by_student_number(student_number: str, department_id: int = None):
        """
        Verilen öğrenci numarasına göre ders listesini döndürür.
        Admin -> tüm bölümler
        Koordinatör -> sadece kendi departmanı
        """
        sql = """
            SELECT `Öğrenci No`, `Ad Soyad`, `Sınıf`, `Dersin Kodu`, `Aldığı Ders`
            FROM student_course_summary
            WHERE `Öğrenci No` = %s
        """
        params = [student_number]

        # 🔹 Eğer koordinatör ise sadece kendi departmanını görür
        if department_id:
            sql += " AND department_id = %s"
            params.append(department_id)

        sql += " ORDER BY `Dersin Kodu`"

        with StudentCourseSummaryService._get_conn() as conn:
            cur = conn.cursor(dictionary=True)
            cur.execute(sql, tuple(params))
            return cur.fetchall()

    # --------------------------------------------------------
    # 2️⃣ Ders koduna göre getir
    # --------------------------------------------------------
    @staticmethod
    def get_by_course_code(course_code: str, department_id: int = None):
        """
        Verilen ders koduna göre öğrencileri döndürür.
        Admin -> tüm bölümler
        Koordinatör -> sadece kendi departmanı
        """
        sql = """
            SELECT `Öğrenci No`, `Ad Soyad`, `Sınıf`, `Dersin Kodu`, `Aldığı Ders`
            FROM student_course_summary
            WHERE `Dersin Kodu` = %s
        """
        params = [course_code]

        # 🔹 Eğer koordinatör ise sadece kendi departmanını görür
        if department_id:
            sql += " AND department_id = %s"
            params.append(department_id)

        sql += " ORDER BY `Öğrenci No`"

        with StudentCourseSummaryService._get_conn() as conn:
            cur = conn.cursor(dictionary=True)
            cur.execute(sql, tuple(params))
            return cur.fetchall()

    # --------------------------------------------------------
    # 3️⃣ Tüm dersleri listele (admin için)
    # --------------------------------------------------------
    @staticmethod
    def list_all_courses():
        """
        Admin tüm bölümlerdeki tüm dersleri görebilir.
        """
        sql = """
            SELECT DISTINCT `Dersin Kodu`, `Aldığı Ders`
            FROM student_course_summary
            ORDER BY `Dersin Kodu`
        """
        with StudentCourseSummaryService._get_conn() as conn:
            cur = conn.cursor(dictionary=True)
            cur.execute(sql)
            return cur.fetchall()

    # --------------------------------------------------------
    # 4️⃣ Belirli bir bölüme ait dersleri listele (koordinatör için)
    # --------------------------------------------------------
    @staticmethod
    def list_courses_by_department(department_id: int):
        """
        Sadece belirli bir departmana ait dersleri listeler.
        """
        sql = """
            SELECT DISTINCT `Dersin Kodu`, `Aldığı Ders`
            FROM student_course_summary
            WHERE department_id = %s
            ORDER BY `Dersin Kodu`
        """
        with StudentCourseSummaryService._get_conn() as conn:
            cur = conn.cursor(dictionary=True)
            cur.execute(sql, (department_id,))
            return cur.fetchall()
