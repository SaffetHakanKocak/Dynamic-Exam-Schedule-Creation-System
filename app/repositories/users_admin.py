from typing import Optional
from app.db import fetchone, execute

def email_exists(email: str) -> bool:
    row = fetchone("SELECT id FROM users WHERE TRIM(LOWER(email))=TRIM(LOWER(%s))", (email,))
    return row is not None

def create_coord(email: str, password_hash: str, department_id: int) -> int:
    # role=COORD ve bölüm zorunlu
    return execute(
        """
        INSERT INTO users(email, password_hash, role, department_id)
        VALUES(%s, %s, 'COORD', %s)
        """,
        (email.strip().lower(), password_hash, department_id)
    )
