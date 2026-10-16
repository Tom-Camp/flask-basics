import json
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent.parent


def load_json(path: Path) -> dict:
    with open(path, "r") as f:
        return json.load(f)
