import json
from pathlib import Path

from ruamel.yaml import YAML, YAMLError

BASE_DIR = Path(__file__).resolve().parent.parent.parent
PROJECT_DIR = Path(__file__).resolve().parent.parent


def load_file(filepath: Path) -> dict:
    yaml = YAML(typ="safe")
    try:
        with open(filepath, "r") as fp:
            if filepath.suffix == ".json":
                return json.load(fp)
            elif filepath.suffix in (".yaml", ".yml"):
                return yaml.load(fp)
            else:
                raise ValueError(f"Unsupported file type: {filepath.suffix}")
    except (json.JSONDecodeError, YAMLError) as e:
        raise ValueError(f"Could not parse {filepath}: {e}") from e
