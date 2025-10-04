from dataclasses import dataclass
from typing import Optional, Literal

Role = Literal["ADMIN", "COORD"]

@dataclass
class User:
    id: int
    email: str
    password_hash: str
    role: Role
    department_id: Optional[int]
