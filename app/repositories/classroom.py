# app/repositories/classrooms.py
from typing import List, Dict, Optional, Tuple
from app.db import fetchall, fetchone, execute

def list_by_department(dept_id: int) -> List[Dict]:
    return fetchall("""
        SELECT id, department_id, code, name, seat_group, num_rows, num_cols, capacity
        FROM classrooms
        WHERE department_id = %s
        ORDER BY code
    """, (dept_id,))

def get_by_id(cid: int) -> Optional[Dict]:
    return fetchone("""
        SELECT id, department_id, code, name, seat_group, num_rows, num_cols, capacity
        FROM classrooms
        WHERE id = %s
    """, (cid,))

def create(dept_id: int, code: str, name: str, seat_group: int, rows: int, cols: int) -> int:
    return execute("""
        INSERT INTO classrooms(department_id, code, name, seat_group, num_rows, num_cols)
        VALUES (%s,%s,%s,%s,%s,%s)
    """, (dept_id, code.strip(), name.strip(), seat_group, rows, cols))

def update(cid: int, code: str, name: str, seat_group: int, rows: int, cols: int) -> int:
    return execute("""
        UPDATE classrooms
           SET code=%s, name=%s, seat_group=%s, num_rows=%s, num_cols=%s
         WHERE id=%s
    """, (code.strip(), name.strip(), seat_group, rows, cols, cid))

def delete(cid: int) -> int:
    return execute("DELETE FROM classrooms WHERE id=%s", (cid,))
