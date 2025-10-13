# app/db.py
from dotenv import load_dotenv
load_dotenv()
from contextlib import contextmanager
from typing import Tuple, Any, Iterable, List, Dict, Optional
import mysql.connector
import os

DB_HOST = os.getenv("DB_HOST", "127.0.0.1")
DB_PORT = int(os.getenv("DB_PORT", "3306"))
DB_USER = os.getenv("DB_USER", "root")
DB_PASS = os.getenv("DB_PASS", "")
DB_NAME = os.getenv("DB_NAME", "exam_scheduler")

def _connect():
    return mysql.connector.connect(
        host=DB_HOST,
        port=DB_PORT,
        user=DB_USER,
        password=DB_PASS,
        database=DB_NAME,
        charset="utf8mb4",
        autocommit=False,
    )

@contextmanager
def tx():
    conn = _connect()
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()

def fetchone(sql: str, params: Tuple[Any, ...] = ()) -> Optional[Dict]:
    with tx() as conn:
        with conn.cursor(dictionary=True) as cur:
            cur.execute(sql, params)
            return cur.fetchone()

def fetchall(sql: str, params: Tuple[Any, ...] = ()) -> List[Dict]:
    with tx() as conn:
        with conn.cursor(dictionary=True) as cur:
            cur.execute(sql, params)
            return cur.fetchall()

def execute(sql: str, params: Tuple[Any, ...] = ()) -> int:
    with tx() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, params)
            return cur.lastrowid or cur.rowcount

def executemany(sql: str, param_list: Iterable[Tuple[Any, ...]]) -> int:
    with tx() as conn:
        with conn.cursor() as cur:
            cur.executemany(sql, list(param_list))
            return cur.rowcount
