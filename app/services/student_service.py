import mysql.connector
import os
import re


class StudentService:
    @staticmethod
    def _get_conn():
        """MySQL bağlantısı oluşturur"""
        return mysql.connector.connect(
            host=os.getenv("DB_HOST", "localhost"),
            user=os.getenv("DB_USER", "root"),
            password=os.getenv("DB_PASS", ""),
            database=os.getenv("DB_NAME", "exam_scheduler"),
            autocommit=True
        )

    # -------------------------------------------------------------------
    # Excel'den gelen öğrenci-ders bilgilerini toplu ekleme
    # -------------------------------------------------------------------
    @staticmethod
    def bulk_insert_from_excel(department_id: int, df):
        """
        Excel'den gelen dataframe'i parse eder ve:
        - Öğrencileri `students` tablosuna ekler/günceller
        - Öğrencilerin aldığı dersleri `enrollments` tablosuna kaydeder
        - Snapshot tabloyu (`student_course_summary`) günceller
        """
        added_students = 0
        added_enrollments = 0

        with StudentService._get_conn() as conn:
            cur = conn.cursor()

            for _, row in df.iterrows():
                try:
                    # --- 1️⃣ Excel'den kolonları oku ---
                    ogr_no = str(row.get("Öğrenci No", row.get("OGRENCI NO", ""))).strip()
                    ad_soyad = str(row.get("Ad Soyad", row.get("AD SOYAD", ""))).strip()
                    sinif_raw = str(row.get("Sınıf", row.get("SINIF", ""))).strip()
                    ders_kodu = str(row.get("Ders", row.get("DERS", ""))).strip()

                    # Boş satır kontrolü
                    if not ogr_no or not ad_soyad or not ders_kodu:
                        continue

                    # --- 2️⃣ "5. Sınıf" gibi değerlerden sadece rakamı ayıkla ---
                    sinif_match = re.search(r'\d+', sinif_raw)
                    sinif = int(sinif_match.group()) if sinif_match else None

                    # --- 3️⃣ Öğrenciyi ekle veya güncelle ---
                    cur.execute("""
                        INSERT INTO students (number, name, grade_level, department_id)
                        VALUES (%s, %s, %s, %s)
                        ON DUPLICATE KEY UPDATE 
                            name = VALUES(name),
                            grade_level = VALUES(grade_level)
                    """, (ogr_no, ad_soyad, sinif, department_id))
                    added_students += 1  # 🔹 Artık her işlenen öğrenci sayılıyor

                    # --- 4️⃣ Ders ID'sini al ---
                    cur.execute("""
                        SELECT id FROM courses 
                        WHERE department_id = %s AND code = %s
                    """, (department_id, ders_kodu))
                    course = cur.fetchone()
                    if not course:
                        # Ders bulunamazsa o satır atlanır (önceden yüklenmeli)
                        continue
                    course_id = course[0]

                    # --- 5️⃣ Öğrenci ID'sini al ---
                    cur.execute("SELECT id FROM students WHERE number = %s", (ogr_no,))
                    student = cur.fetchone()
                    if not student:
                        continue
                    student_id = student[0]

                    # --- 6️⃣ Enrollments tablosuna kaydet ---
                    cur.execute("""
                        INSERT IGNORE INTO enrollments (student_id, course_id)
                        VALUES (%s, %s)
                    """, (student_id, course_id))
                    added_enrollments += 1  # 🔹 Her başarılı kayıt sayılıyor

                except Exception as e:
                    print(f"[HATA] Satırda hata: {e}")
                    continue

            # ----------------------------------------------------------------
            # 7️⃣ Snapshot tabloyu (student_course_summary) güncelle
            # ----------------------------------------------------------------
            try:
                cur.execute("TRUNCATE TABLE `student_course_summary`;")
                cur.execute("""
                    INSERT INTO `student_course_summary`
                        (`Öğrenci No`, `Ad Soyad`, `Sınıf`, `Dersin Kodu`, `Aldığı Ders`)
                    SELECT 
                        s.number AS `Öğrenci No`,
                        s.name AS `Ad Soyad`,
                        s.grade_level AS `Sınıf`,
                        c.code AS `Dersin Kodu`,
                        c.name AS `Aldığı Ders`
                    FROM enrollments e
                    JOIN students s ON e.student_id = s.id
                    JOIN courses c  ON e.course_id  = c.id
                    WHERE s.department_id = %s
                    ORDER BY s.number, c.code;
                """, (department_id,))
                print("[✅ TABLO GÜNCELLENDİ] student_course_summary başarıyla yenilendi.")
            except Exception as e:
                print(f"[UYARI] student_course_summary güncellenemedi: {e}")

        # ----------------------------------------------------------------
        print(f"[ÖZET] {added_students} öğrenci işlendi, {added_enrollments} ders kaydı eklendi.")
        return added_students, added_enrollments
