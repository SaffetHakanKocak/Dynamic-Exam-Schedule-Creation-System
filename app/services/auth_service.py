import bcrypt
from app.repositories.users import get_by_email

class AuthService:
    @staticmethod
    def login(email: str, password: str) -> dict | None:
        u = get_by_email(email)
        if not u:
            return None
        if not bcrypt.checkpw(password.encode("utf-8"), u["password_hash"].encode("utf-8")):
            return None

        # COORD ise department zorunlu
        if u["role"] == "COORD" and u["department_id"] is None:
            # Girişi reddet, login ekranında uyarı görünsün
            raise ValueError("Koordinatör hesabı için department_id tanımlı olmalıdır.")

        return {
            "id": u["id"],
            "email": u["email"],
            "role": u["role"],
            "department_id": u["department_id"],
        }
