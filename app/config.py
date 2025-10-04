from dataclasses import dataclass
import os
from dotenv import load_dotenv

load_dotenv()

@dataclass
class Settings:
    db_host: str = os.getenv("DB_HOST", "127.0.0.1")
    db_port: int = int(os.getenv("DB_PORT", "3306"))
    db_user: str = os.getenv("DB_USER", "root")
    db_pass: str = os.getenv("DB_PASS", "")
    db_name: str = os.getenv("DB_NAME", "exam_scheduler")
    db_pool_size: int = int(os.getenv("DB_POOL_SIZE", "5"))

settings = Settings()
