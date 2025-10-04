from typing import List, Dict
from app.db import fetchall

def list_all() -> List[Dict]:
    return fetchall("SELECT id, name FROM departments ORDER BY name")
