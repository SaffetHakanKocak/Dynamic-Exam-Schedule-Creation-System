# app/services/classroom_layout_service.py
from typing import List, Dict
import os, mysql.connector

def _get_conn():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST","localhost"),
        user=os.getenv("DB_USER","root"),
        password=os.getenv("DB_PASS",""),
        database=os.getenv("DB_NAME","exam_scheduler"),
        autocommit=True,
    )

class ClassroomLayoutService:
    @staticmethod
    def get_layout(classroom_id:int) -> List[int]:
        """Sütun indeksine göre 1..N seat_group listesi döner."""
        sql = "SELECT col_index, seat_group FROM classroom_columns WHERE classroom_id=%s ORDER BY col_index"
        with _get_conn() as c:
            cur = c.cursor()
            cur.execute(sql, (classroom_id,))
            rows = cur.fetchall()
            return [sg for _, sg in rows]

    @staticmethod
    def save_layout(classroom_id:int, seat_groups:List[int]) -> None:
        """Tam listeyi yazar; num_cols ile uzunluğu eşit olmalı."""
        # küçük doğrulama
        if not seat_groups or any(sg not in (2,3,4) for sg in seat_groups):
            raise ValueError("Sütun koltuk sayıları 2/3/4 olmalı.")
        with _get_conn() as c:
            cur = c.cursor()
            # num_cols ile uyuştur
            cur.execute("SELECT num_cols FROM classrooms WHERE id=%s", (classroom_id,))
            (num_cols,) = cur.fetchone()
            if num_cols != len(seat_groups):
                raise ValueError(f"num_cols={num_cols} fakat gelen liste {len(seat_groups)} uzunlukta.")

            # replace-all stratejisi
            cur.execute("DELETE FROM classroom_columns WHERE classroom_id=%s", (classroom_id,))
            cur.executemany(
                "INSERT INTO classroom_columns(classroom_id,col_index,seat_group) VALUES(%s,%s,%s)",
                [(classroom_id, i+1, sg) for i, sg in enumerate(seat_groups)]
            )
            # capacity trigger ile otomatik güncellendi
