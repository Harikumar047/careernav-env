import json
import os
from typing import List
from ..models import SchemeData

def get_available_schemes() -> List[SchemeData]:
    """Loads schemes from the daily fallback JSON file"""
    path = os.path.join(os.path.dirname(__file__), "..", "..", "mocks", "schemes.json")
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return [SchemeData(**item) for item in data]
