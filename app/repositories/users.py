from typing import Optional
from app.db import fetchone

def get_by_email(email: str) -> Optional[dict]:
    row = fetchone(
        """
        SELECT id, email, password_hash, role, department_id
        FROM users
        WHERE TRIM(LOWER(email)) = TRIM(LOWER(%s))
        """,
        (email,)
    )
    return row  # dict (None olabilir)
