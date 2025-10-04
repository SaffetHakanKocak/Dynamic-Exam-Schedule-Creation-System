import bcrypt
from .db import get_conn

class AuthError(Exception):
    pass

def authenticate(email: str, password: str) -> dict:
    if not email or not password:
        raise AuthError("E-posta veya şifre eksik.")

    sql = """
        SELECT u.id, u.email, u.password_hash, u.role, u.department_id,
               d.name AS department_name
          FROM users u
     LEFT JOIN departments d ON d.id = u.department_id
         WHERE TRIM(LOWER(u.email)) = TRIM(LOWER(%s))
         LIMIT 1
    """
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(sql, (email,))
        row = cur.fetchone()

    if not row:
        raise AuthError("E-posta veya şifre hatalı.")

    # DB'deki hash string ise encode et
    pw_hash = row["password_hash"]
    if isinstance(pw_hash, str):
        pw_hash = pw_hash.encode("utf-8")

    ok = bcrypt.checkpw(password.encode("utf-8"), pw_hash)
    if not ok:
        raise AuthError("E-posta veya şifre hatalı.")

    return {
        "id": row["id"],
        "email": row["email"],
        "role": row["role"],  # 'ADMIN' | 'COORD'
        "department_id": row["department_id"],
        "department_name": row["department_name"],
        "is_admin": row["role"] == "ADMIN",
        "scope": "ALL" if row["role"] == "ADMIN" else f"DEPT:{row['department_id']}",
    }
