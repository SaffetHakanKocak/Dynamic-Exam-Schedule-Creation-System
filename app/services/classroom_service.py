from typing import Optional, List, Dict
import os
import mysql.connector


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
# DOĞRULAMA
# --------------------------------------------------------
def _validate(rows: int, cols: int, seat_group: int, capacity: int):
    if rows <= 0 or cols <= 0:
        raise ValueError("Satır ve sütun pozitif olmalı.")
    if seat_group not in (2, 3, 4):
        raise ValueError("Sıra yapısı 2, 3 veya 4 olmalı.")
    if capacity <= 0:
        raise ValueError("Kapasite pozitif olmalı.")


# --------------------------------------------------------
# DERSLİK SERVİSİ
# --------------------------------------------------------
class ClassroomService:
    # --------------------------------------------------------
    # LİSTELEME
    # --------------------------------------------------------
    @staticmethod
    def list_by_department(department_id: int) -> List[Dict]:
        """
        İlgili bölüme ait derslikleri listeler.
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
    # ARAMA
    # --------------------------------------------------------
    @staticmethod
    def search(department_id: int, keyword: str) -> List[Dict]:
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
              AND (c.code LIKE %s OR c.name LIKE %s)
            ORDER BY c.name
        """
        like = f"%{keyword}%"
        try:
            with _get_conn() as c:
                cur = c.cursor(dictionary=True)
                cur.execute(sql, (department_id, like, like))
                return cur.fetchall()
        except mysql.connector.Error as e:
            raise RuntimeError(f"Derslik araması başarısız: {e}")

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
                               rows: int, cols: int, seat_group: int, capacity: int) -> int:
        """
        Bölüm adı dahil yeni derslik ekler.
        """
        _validate(rows, cols, seat_group, capacity)
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
    # DERSLİK GÜNCELLEME
    # --------------------------------------------------------
    @staticmethod
    def update_with_department(department_id: int, dept_name: str, code: str, name: str,
                               rows: int, cols: int, seat_group: int, capacity: int) -> None:
        _validate(rows, cols, seat_group, capacity)
        sql = """
            UPDATE classrooms
               SET name = %s,
                   seat_group = %s,
                   num_rows = %s,
                   num_cols = %s,
                   capacity = %s
             WHERE department_id = %s AND code = %s
        """
        try:
            with _get_conn() as c:
                cur = c.cursor()
                cur.execute(sql, (name.strip(), seat_group, rows, cols, capacity, department_id, code.strip()))
        except mysql.connector.Error as e:
            raise RuntimeError(f"Derslik güncellenemedi: {e}")

    # --------------------------------------------------------
    # DERSLİK SİLME
    # --------------------------------------------------------
    @staticmethod
    def delete_by_code(department_id: int, code: str) -> None:
        sql = "DELETE FROM classrooms WHERE department_id = %s AND code = %s"
        try:
            with _get_conn() as c:
                cur = c.cursor()
                cur.execute(sql, (department_id, code.strip()))
        except mysql.connector.Error as e:
            raise RuntimeError(f"Derslik silinemedi: {e}")
