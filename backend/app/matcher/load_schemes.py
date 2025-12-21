import json
from pathlib import Path

SCHEME_FILE = Path(__file__).parent.parent / "data" / "schemes_structured.json"


def load_schemes():
    with open(SCHEME_FILE, "r", encoding="utf-8") as f:
        return json.load(f)
