import mysql.connector
import os
import re


class StudentService:
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
        added_students = 0
        added_enrollments = 0

        try:
            department_id = int(department_id)
        except (ValueError, TypeError):
            department_id = 0

        with StudentService._get_conn() as conn:
            cur = conn.cursor()

            for _, row in df.iterrows():
                try:
                    ogr_no    = str(row.get("Öğrenci No", row.get("OGRENCI NO", ""))).strip()
                    ad_soyad  = str(row.get("Ad Soyad",   row.get("AD SOYAD",   ""))).strip()
                    sinif_raw = str(row.get("Sınıf",      row.get("SINIF",      ""))).strip()
                    ders_kodu = str(row.get("Ders",       row.get("DERS",       ""))).strip()

                    if not ogr_no or not ad_soyad or not ders_kodu:
                        continue

                    m = re.search(r'\d+', sinif_raw or "")
                    sinif = int(m.group()) if m else None

                    # öğrenci ekle/güncelle
                    cur.execute("""
                        INSERT INTO students (number, name, grade_level, department_id)
                        VALUES (%s, %s, %s, %s)
                        ON DUPLICATE KEY UPDATE
                            name = VALUES(name),
                            grade_level = VALUES(grade_level),
                            department_id = VALUES(department_id)
                    """, (ogr_no, ad_soyad, sinif, department_id))
                    added_students += 1

                    # ders id
                    cur.execute("""
                        SELECT id FROM courses
                        WHERE department_id = %s AND code = %s
                    """, (department_id, ders_kodu))
                    course = cur.fetchone()
                    if not course:
                        continue
                    course_id = course[0]

                    # öğrenci id
                    cur.execute("SELECT id FROM students WHERE number = %s", (ogr_no,))
                    student = cur.fetchone()
                    if not student:
                        continue
                    student_id = student[0]

                    # enrollments'a ekle (uniq index varsa kopya zaten düşer)
                    cur.execute("""
                        INSERT IGNORE INTO enrollments (student_id, course_id)
                        VALUES (%s, %s)
                    """, (student_id, course_id))
                    added_enrollments += 1

                except Exception as e:
                    print(f"[HATA] Satır işlenemedi ({ogr_no}): {e}")
                    continue

            # --- özet tablo öncesi: enrollments'ta varsa kopyaları temizle ---
            try:
                cur.execute("""
                    DELETE e1
                    FROM enrollments e1
                    JOIN enrollments e2
                      ON e1.student_id = e2.student_id
                     AND e1.course_id  = e2.course_id
                     AND e1.id > e2.id
                """)
            except Exception as e:
                print(f"[UYARI] enrollments dedupe başarısız: {e}")

            # --- 📘 ÖNEMLİ: Artık sadece o bölüme ait kayıtlar silinecek ---
            try:
                print(f"[INFO] {added_students} öğrenci işlendi, özet tablo güncelleniyor...")

                # 🔥 TRUNCATE yerine sadece o departmanın verilerini temizle
                cur.execute("DELETE FROM `student_course_summary` WHERE department_id = %s;", (department_id,))

                # 🔥 Yeni kayıtlar department_id ile ekleniyor
                cur.execute("""
                    INSERT INTO `student_course_summary`
                        (`Öğrenci No`, `Ad Soyad`, `Sınıf`, `Dersin Kodu`, `Aldığı Ders`, department_id)
                    SELECT DISTINCT
                        s.number,
                        s.name,
                        s.grade_level,
                        c.code,
                        c.name,
                        s.department_id
                    FROM enrollments e
                    JOIN students  s ON e.student_id = s.id
                    JOIN courses   c ON e.course_id  = c.id
                    WHERE s.department_id = %s
                    ORDER BY s.number, c.code;
                """, (department_id,))

                print("[✅] student_course_summary başarıyla güncellendi (bölüm bazlı).")

            except Exception as e:
                print(f"[UYARI] student_course_summary güncellenemedi: {e}")

        print(f"[ÖZET] {added_students} öğrenci işlendi, {added_enrollments} ders kaydı eklendi.")
        return added_students, added_enrollments
