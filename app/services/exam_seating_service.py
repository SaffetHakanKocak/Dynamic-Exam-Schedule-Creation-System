import datetime
from dataclasses import dataclass
from typing import List, Dict
from app.db import fetchall, fetchone
from reportlab.lib.pagesizes import A4, landscape
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import os
import platform


# ---------------------------------------
#  FONT TANIMI (Windows / Linux Otomatik)
# ---------------------------------------
def register_turkish_font():
    system = platform.system().lower()
    font_name = "DejaVu"
    font_paths = []

    if system == "windows":
        font_paths = [
            os.path.join(os.environ.get("WINDIR", "C:\\Windows"), "Fonts", "DejaVuSans.ttf"),
            os.path.join(os.environ.get("WINDIR", "C:\\Windows"), "Fonts", "arial.ttf"),
        ]
    else:
        font_paths = [
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
            "/usr/share/fonts/truetype/freefont/FreeSans.ttf",
        ]

    for path in font_paths:
        if os.path.exists(path):
            try:
                pdfmetrics.registerFont(TTFont(font_name, path))
                print(f"✅ Font yüklendi: {path}")
                return font_name
            except Exception as e:
                print(f"⚠️ Font yüklenemedi: {path} ({e})")

    print("⚠️ Türkçe font bulunamadı, Helvetica kullanılacak.")
    pdfmetrics.registerFont(TTFont(font_name, "Helvetica"))
    return font_name


FONT_NAME = register_turkish_font()


@dataclass
class Room:
    id: int
    code: str
    num_rows: int
    num_cols: int
    seat_group: int
    capacity: int
    col_groups: List[int]


class ExamSeatingService:
    """
    Sınav bazlı oturma planı üretimi + PDF çıktısı.
    Seat_group bazlı yerleştirme + sayfaya sığacak ölçeklendirme.
    Uyarı/Hata mantığı dahil edilmiştir.
    """

    def __init__(self):
        self.warnings = []  # 🔹 Uyarı mesajları burada toplanacak

    # -------------------- PUBLIC API --------------------
    def list_exams(self, department_id: int) -> List[Dict]:
        """Tüm sınavları getirir (geriye dönük uyumluluk için korundu)."""
        return fetchall("""
            SELECT ex.id, c.code AS course_code, c.name AS course_name,
                   t.starts_at, t.ends_at
            FROM exams ex
            JOIN courses c ON c.id = ex.course_id
            JOIN timeslots t ON t.id = ex.timeslot_id
            WHERE c.department_id = %s
            ORDER BY t.starts_at ASC
        """, (department_id,))

    def list_latest_exams(self, department_id: int) -> List[Dict]:
        """
        En son oluşturulan sınav dönemine ait sınavları döndürür.
        Eğer exam_term_id eşleşmesi yoksa tarih bazlı yedek kontrol yapılır.
        """

        # 🔥 Admin bölüm seçmeden çağırırsa hata vermesin
        if not department_id:
            print("⚠️ Bölüm ID boş, sınav listesi yüklenmedi (admin henüz seçim yapmadı).")
            return []

        latest_term = fetchone("""
            SELECT id, date_start, date_end
            FROM exam_terms
            ORDER BY id DESC
            LIMIT 1
        """)

        if not latest_term:
            print("⚠️ Hiç sınav dönemi bulunamadı.")
            return []

        term_id = latest_term["id"]
        start_date = latest_term["date_start"]
        end_date = latest_term["date_end"]

        # Öncelikli olarak exam_term_id üzerinden çek
        exams = fetchall("""
            SELECT ex.id, c.code AS course_code, c.name AS course_name,
                   t.starts_at, t.ends_at
            FROM exams ex
            JOIN courses c ON c.id = ex.course_id
            JOIN timeslots t ON t.id = ex.timeslot_id
            JOIN exam_terms et ON et.id = ex.exam_term_id
            WHERE c.department_id = %s
              AND et.id = %s
            ORDER BY t.starts_at ASC
        """, (department_id, term_id))

        # Eğer exam_term_id bağlantısı yoksa tarih aralığına göre getir
        if not exams:
            exams = fetchall("""
                SELECT ex.id, c.code AS course_code, c.name AS course_name,
                       t.starts_at, t.ends_at
                FROM exams ex
                JOIN courses c ON c.id = ex.course_id
                JOIN timeslots t ON t.id = ex.timeslot_id
                WHERE c.department_id = %s
                  AND DATE(t.starts_at) BETWEEN %s AND %s
                ORDER BY t.starts_at ASC
            """, (department_id, start_date, end_date))

        return exams

    def get_exam_overview(self, exam_id: int) -> Dict:
        exam = fetchone("""
            SELECT ex.id, c.code, c.name, t.starts_at, t.ends_at
            FROM exams ex
            JOIN courses c ON c.id = ex.course_id
            JOIN timeslots t ON t.id = ex.timeslot_id
            WHERE ex.id = %s
        """, (exam_id,))
        rooms = self._load_rooms_for_exam(exam_id)
        return {"exam": exam, "rooms": rooms}

    def generate_seating(self, exam_id: int) -> List[Dict]:
        """Öğrencileri derslik kapasitesine göre sırayla yerleştirir."""
        self.warnings.clear()
        students = self._load_students_for_exam(exam_id)
        rooms = self._load_rooms_for_exam(exam_id)
        if not students or not rooms:
            msg = "⚠️ Oturma planı oluşturulamadı: Öğrenci veya derslik bulunamadı."
            print(msg)
            self.warnings.append(msg)
            return []

        total_cap = sum(r.capacity for r in rooms)
        print(f"🧮 Toplam {len(rooms)} derslik kapasitesi: {total_cap} — Öğrenci sayısı: {len(students)}")

        if total_cap < len(students):
            msg = f"Derslik kapasitesi yetersiz! (Toplam kapasite: {total_cap}, Öğrenci: {len(students)})"
            self.warnings.append(msg)
            raise ValueError(msg)

        placements = []
        idx = 0
        for r in sorted(rooms, key=lambda x: x.capacity, reverse=True):
            room_capacity = r.capacity
            available_students = students[idx: idx + room_capacity]

            if not available_students:
                continue

            # 🔹 Eğer kapasite dolduysa uyarı
            if len(available_students) < room_capacity and idx + len(available_students) < len(students):
                remaining = len(students) - (idx + len(available_students))
                self.warnings.append(
                    f"{remaining} öğrenci {r.code} dersliğine sığmadı (kapasite dolu)."
                )

            for i, s in enumerate(available_students):
                row_no = (i // r.num_cols) + 1
                col_no = (i % r.num_cols) + 1
                placements.append({
                    "student_number": s["number"],
                    "student_name": s["name"],
                    "room_code": r.code,
                    "row_no": row_no,
                    "col_no": col_no
                })
            idx += len(available_students)

            if idx >= len(students):
                break

        # 🔹 Yan yana oturma kontrolü
        for i in range(1, len(placements)):
            prev = placements[i - 1]
            curr = placements[i]
            if prev["room_code"] == curr["room_code"] and prev["row_no"] == curr["row_no"]:
                if prev["student_name"].split()[-1] == curr["student_name"].split()[-1]:
                    self.warnings.append(
                        f"{prev['student_name']} ve {curr['student_name']} aynı soyadlı öğrenciler yan yana oturdu ({prev['room_code']})."
                    )

        print(f"✅ Oturma planı tamamlandı, toplam {len(placements)} öğrenci yerleştirildi.\n")
        return placements

    def export_pdf(self, exam_id: int, seating: List[Dict], filename: str):
        """PDF çıktısı üretir (seat_group + ölçeklendirilmiş çizim)."""
        ov = self.get_exam_overview(exam_id)
        ex, rooms = ov["exam"], ov["rooms"]

        c = canvas.Canvas(filename, pagesize=landscape(A4))
        w, h = landscape(A4)

        # Başlık
        c.setFont(FONT_NAME, 16)
        c.drawString(2 * cm, h - 2 * cm, "Sınav Oturma Planı (Ders Bazlı)")
        c.setFont(FONT_NAME, 12)
        c.drawString(
            2 * cm, h - 2.8 * cm,
            f"{ex['code']} — {ex['name']} | {ex['starts_at'].strftime('%d.%m.%Y %H:%M')}"
        )

        # Her derslik için sayfa
        for room in rooms:
            c.showPage()
            w, h = landscape(A4)
            c.setFont(FONT_NAME, 14)
            c.drawString(2 * cm, h - 2 * cm, f"Derslik: {room.code}")
            c.setFont(FONT_NAME, 10)
            c.drawString(2 * cm, h - 2.7 * cm,
                         f"Sıra: {room.num_rows}   Sütun: {room.num_cols}   Kapasite: {room.capacity}")

            room_students = [p for p in seating if p["room_code"] == room.code]
            if not room_students:
                c.drawString(2 * cm, h - 3.5 * cm, "⚠️ Bu dersliğe öğrenci atanmadı.")
                continue

            scale = 0.75
            box_w, box_h = 2.0 * cm * scale, 1.0 * cm * scale
            spacing = 0.3 * cm * scale
            group_gap = 2.5 * cm * scale
            start_x, start_y = 3 * cm, h - 4 * cm
            idx = 0

            def get_pattern(group_size):
                if group_size == 2:
                    return [1, 0]
                elif group_size == 3:
                    return [1, 0, 1]
                elif group_size == 4:
                    return [1, 0, 0, 1]
                else:
                    return [1] * group_size

            for r_i in range(room.num_rows):
                x = start_x
                for g_idx, group in enumerate(room.col_groups):
                    if g_idx > 0:
                        x += group_gap
                    pattern = get_pattern(group)
                    for col_idx, val in enumerate(pattern):
                        if val == 1:
                            if idx < len(room_students):
                                student = room_students[idx]
                                idx += 1
                                c.setFillColor(colors.lightblue)
                                c.rect(x, start_y - r_i * (box_h + spacing), box_w, box_h, fill=True, stroke=1)
                                name = student["student_name"]
                                number = student["student_number"]
                                text = f"{name} - {number}"
                                font_size = 7 * scale
                                if len(text) > 22:
                                    font_size = 6 * scale
                                if len(text) > 30:
                                    font_size = 5 * scale
                                c.setFont(FONT_NAME, font_size)
                                c.setFillColor(colors.black)
                                c.drawCentredString(
                                    x + box_w / 2,
                                    start_y - r_i * (box_h + spacing) + box_h / 2 - 0.15 * cm * scale,
                                    text
                                )
                            else:
                                c.setFillColor(colors.lightgrey)
                                c.rect(x, start_y - r_i * (box_h + spacing), box_w, box_h, fill=True, stroke=1)
                        else:
                            c.setFillColor(colors.lightgrey)
                            c.rect(x, start_y - r_i * (box_h + spacing), box_w, box_h, fill=True, stroke=1)
                        x += box_w + spacing

            c.setFont(FONT_NAME, 9)
            c.setFillColor(colors.black)
            c.drawString(2 * cm, 2 * cm, f"Toplam Yerleşen: {len(room_students)} öğrenci")

        c.save()

    # -------------------- DATA HELPERS --------------------
    def _load_students_for_exam(self, exam_id: int):
        return fetchall("""
            SELECT s.id, s.number, s.name
            FROM students s
            JOIN enrollments e ON e.student_id = s.id
            JOIN exams ex ON ex.course_id = e.course_id
            WHERE ex.id = %s
            ORDER BY s.number
        """, (exam_id,))

    def _load_rooms_for_exam(self, exam_id: int) -> List[Room]:
        rows = fetchall("""
            SELECT r.id, r.code, r.num_rows, r.num_cols, r.seat_group, r.capacity
            FROM exam_rooms er
            JOIN classrooms r ON r.id = er.classroom_id
            WHERE er.exam_id = %s
            ORDER BY r.capacity DESC
        """, (exam_id,))
        rooms = []
        for rr in rows:
            cols = fetchall("""
                SELECT col_index, seat_group
                FROM classroom_columns
                WHERE classroom_id = %s
                ORDER BY col_index
            """, (rr["id"],))
            col_groups = [c["seat_group"] for c in cols] if cols else [rr["seat_group"]] * rr["num_cols"]
            rooms.append(Room(
                id=rr["id"],
                code=rr["code"],
                num_rows=rr["num_rows"],
                num_cols=rr["num_cols"],
                seat_group=rr["seat_group"],
                capacity=rr["capacity"],
                col_groups=col_groups
            ))
        return rooms
