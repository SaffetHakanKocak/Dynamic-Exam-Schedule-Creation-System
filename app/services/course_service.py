import mysql.connector
import os


class CourseService:
    @staticmethod
    def _get_conn():
        return mysql.connector.connect(
            host=os.getenv("DB_HOST", "localhost"),
            user=os.getenv("DB_USER", "root"),
            password=os.getenv("DB_PASS", ""),
            database=os.getenv("DB_NAME", "exam_scheduler"),
            autocommit=True
        )

    @staticmethod
    def bulk_insert_from_excel(department_id: int, df):
        added = 0
        with CourseService._get_conn() as conn:
            cur = conn.cursor()
            for _, row in df.iterrows():
                try:
                    code = str(row.get("DERS KODU", "")).strip()
                    name = str(row.get("DERSİN ADI", row.get("DERSIN ADI", ""))).strip()
                    instructor = str(row.get("DERSİ VEREN ÖĞR. ELEMANI", row.get("DERSI VEREN OGR. ELEMANI", ""))).strip()
                    class_name = str(row.get("SINIF", "Belirtilmemiş")).strip()
                    course_type = str(row.get("DERS TÜRÜ", "Zorunlu")).strip()

                    if not code or not name:
                        continue

                    cur.execute("""
                        INSERT INTO courses 
                            (department_id, code, name, instructor_name, class_name, course_type)
                        VALUES (%s, %s, %s, %s, %s, %s)
                        ON DUPLICATE KEY UPDATE 
                            name = VALUES(name),
                            instructor_name = VALUES(instructor_name),
                            class_name = VALUES(class_name),
                            course_type = VALUES(course_type)
                    """, (department_id, code, name, instructor, class_name, course_type))
                    added += 1
                except Exception as e:
                    print(f"Hata satırda: {e}")
                    continue
        return added
