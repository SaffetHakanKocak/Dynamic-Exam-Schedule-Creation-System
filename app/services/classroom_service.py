from typing import Optional, List, Dict
import os
import mysql.connector
from app.db import fetchall, execute


# --------------------------------------------------------
# VERİTABANI BAĞLANTISI
# --------------------------------------------------------
def _get_conn():
    try:
        return mysql.connector.connect(
            host=os.getenv("DB_HOST", "localhost"),
            user=os.getenv("DB_USER", "root"),
            password=os.getenv("DB_PASS", ""),
            database=os.getenv("DB_NAME", "exam_scheduler"),
            autocommit=True,
            connection_timeout=5,
        )
    except mysql.connector.Error as e:
        raise RuntimeError(f"Veritabanına bağlanılamadı: {e}")


# --------------------------------------------------------
# OTURULABİLİR KAPASİTE HESABI
# --------------------------------------------------------
def _usable_capacity(rows: int, cols: int, seat_group: int) -> int:
    """
    Oturulabilir maksimum kapasiteyi hesaplar.
    2'li sıra -> 1 dolu
    3'lü sıra -> 2 dolu
    4'lü sıra -> 2 dolu
    """
    fill_per_group = {2: 1, 3: 2, 4: 2}
    if seat_group not in fill_per_group:
        raise ValueError("Sıra yapısı 2, 3 veya 4 olmalı.")
    return rows * cols * fill_per_group[seat_group]


# --------------------------------------------------------
# DOĞRULAMA
# --------------------------------------------------------
def _validate(rows: int, cols: int, seat_group: int):
    if rows <= 0 or cols <= 0:
        raise ValueError("Satır ve sütun pozitif olmalı.")
    if seat_group not in (2, 3, 4):
        raise ValueError("Sıra yapısı 2, 3 veya 4 olmalı.")


# --------------------------------------------------------
# DERSLİK SERVİSİ
# --------------------------------------------------------
class ClassroomService:
    # --------------------------------------------------------
    # LİSTELEME
    # --------------------------------------------------------
    @staticmethod
    def list_by_department(department_id: int) -> List[Dict]:
        sql = """
            SELECT
                c.id,
                c.department_id,
                d.name AS department_name,
                c.code,
                c.name,
                c.seat_group,
                c.num_rows,
                c.num_cols,
                c.capacity
            FROM classrooms c
            JOIN departments d ON d.id = c.department_id
            WHERE c.department_id = %s
            ORDER BY c.name
        """
        try:
            with _get_conn() as c:
                cur = c.cursor(dictionary=True)
                cur.execute(sql, (department_id,))
                return cur.fetchall()
        except mysql.connector.Error as e:
            raise RuntimeError(f"Derslik listesi alınamadı: {e}")

    # --------------------------------------------------------
    # 🔍 SADECE DERSLİK KODU İLE ARAMA (Bölüm Koordinatörü)
    # --------------------------------------------------------
    @staticmethod
    def search(department_id: int, code: str) -> List[Dict]:
        """
        Bölüm koordinatörleri için: yalnızca derslik kodu (c.code) üzerinden arama yapar.
        """
        sql = """
            SELECT
                c.id,
                c.department_id,
                d.name AS department_name,
                c.code,
                c.name,
                c.seat_group,
                c.num_rows,
                c.num_cols,
                c.capacity
            FROM classrooms c
            JOIN departments d ON d.id = c.department_id
            WHERE c.department_id = %s
              AND c.code LIKE %s
            ORDER BY c.name
        """
        like = f"%{code}%"
        try:
            with _get_conn() as c:
                cur = c.cursor(dictionary=True)
                cur.execute(sql, (department_id, like))
                return cur.fetchall()
        except mysql.connector.Error as e:
            raise RuntimeError(f"Derslik araması başarısız: {e}")

    # --------------------------------------------------------
    # 🔍 SADECE DERSLİK KODU İLE GLOBAL ARAMA (Admin)
    # --------------------------------------------------------
    @staticmethod
    def search_global(code: str) -> List[Dict]:
        """
        Admin kullanıcılar için: yalnızca derslik kodu (c.code) üzerinden arama yapar.
        """
        sql = """
            SELECT
                c.id,
                c.department_id,
                d.name AS department_name,
                c.code,
                c.name,
                c.seat_group,
                c.num_rows,
                c.num_cols,
                c.capacity
            FROM classrooms c
            JOIN departments d ON d.id = c.department_id
            WHERE c.code LIKE %s
            ORDER BY d.name, c.code
        """
        like = f"%{code}%"
        try:
            with _get_conn() as c:
                cur = c.cursor(dictionary=True)
                cur.execute(sql, (like,))
                return cur.fetchall()
        except mysql.connector.Error as e:
            raise RuntimeError(f"Global derslik araması başarısız: {e}")

    # --------------------------------------------------------
    # TEK DERSLİK GETİRME
    # --------------------------------------------------------
    @staticmethod
    def get(classroom_id: int) -> Optional[Dict]:
        sql = """
            SELECT
                c.id,
                c.department_id,
                d.name AS department_name,
                c.code,
                c.name,
                c.seat_group,
                c.num_rows,
                c.num_cols,
                c.capacity
            FROM classrooms c
            JOIN departments d ON d.id = c.department_id
            WHERE c.id = %s
        """
        try:
            with _get_conn() as c:
                cur = c.cursor(dictionary=True)
                cur.execute(sql, (classroom_id,))
                return cur.fetchone()
        except mysql.connector.Error as e:
            raise RuntimeError(f"Derslik getirilemedi: {e}")

    # --------------------------------------------------------
    # DERSLİK OLUŞTURMA
    # --------------------------------------------------------
    @staticmethod
    def create_with_department(department_id: int, dept_name: str, code: str, name: str,
                               rows: int, cols: int, seat_group: int) -> int:
        _validate(rows, cols, seat_group)
        # ✅ Kapasiteyi otomatik hesapla
        capacity = _usable_capacity(rows, cols, seat_group)
        sql = """
            INSERT INTO classrooms (department_id, code, name, seat_group, num_rows, num_cols, capacity)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        try:
            with _get_conn() as c:
                cur = c.cursor()
                cur.execute(sql, (department_id, code.strip(), name.strip(),
                                 seat_group, rows, cols, capacity))
                return cur.lastrowid
        except mysql.connector.Error as e:
            raise RuntimeError(f"Derslik eklenemedi: {e}")

    # --------------------------------------------------------
    # DERSLİK GÜNCELLEME (ID bazlı)
    # --------------------------------------------------------
    @staticmethod
    def update_by_id(classroom_id: int, name: str, rows: int, cols: int,
                     seat_group: int) -> None:
        _validate(rows, cols, seat_group)
        capacity = _usable_capacity(rows, cols, seat_group)
        sql = """
            UPDATE classrooms
               SET name = %s,
                   seat_group = %s,
                   num_rows = %s,
                   num_cols = %s,
                   capacity = %s
             WHERE id = %s
        """
        try:
            with _get_conn() as c:
                cur = c.cursor()
                cur.execute(sql, (name.strip(), seat_group, rows, cols, capacity, classroom_id))
        except mysql.connector.Error as e:
            raise RuntimeError(f"Derslik güncellenemedi: {e}")

    # --------------------------------------------------------
    # DERSLİK SİLME
    # --------------------------------------------------------
    @staticmethod
    def delete_by_id(classroom_id: int) -> None:
        sql = "DELETE FROM classrooms WHERE id = %s"
        try:
            with _get_conn() as c:
                cur = c.cursor()
                cur.execute(sql, (classroom_id,))
        except mysql.connector.Error as e:
            raise RuntimeError(f"Derslik silinemedi: {e}")

    # --------------------------------------------------------
    # TÜM BÖLÜMLERİN DERSLİKLERİNİ LİSTELE (Admin için)
    # --------------------------------------------------------
    def list_all(self):
        return fetchall("""
        SELECT c.id, c.code, c.name, c.num_rows, c.num_cols, 
               c.seat_group, c.capacity, d.name AS department_name
        FROM classrooms c
        LEFT JOIN departments d ON c.department_id = d.id
        ORDER BY d.name, c.code
    """)
