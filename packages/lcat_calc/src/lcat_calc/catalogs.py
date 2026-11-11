from pathlib import Path

from lcat_calc.loader import (
    _read_yaml,
    build_lcat_index,
    default_index,
    load_categories,
)
from lcat_calc.models import LcatIndex

DEFAULT_CATALOG = "default"


class CatalogRegistry:
    """
    Named LCAT catalogs: the bundled one ("default") plus any found under `directory`.

    Each catalog is a subdirectory containing `lcats.yaml` and, optionally, `categories.yaml`
    (the bundled categories are used when it is absent). Every catalog is validated on construction.
    """

    def __init__(self, directory: Path | None = None) -> None:
        bundled_categories = load_categories()
        self._indexes: dict[str, LcatIndex] = {DEFAULT_CATALOG: default_index()}
        self._categories: dict[str, dict[str, list[str]]] = {
            DEFAULT_CATALOG: bundled_categories
        }

        if directory is None:
            return
        if not directory.is_dir():
            raise FileNotFoundError(f"Catalog directory not found: {directory}")
        for path in sorted(
            p
            for p in directory.iterdir()
            if p.is_dir() and (p / "lcats.yaml").is_file()
        ):
            if path.name == DEFAULT_CATALOG:
                raise ValueError(
                    f"'{DEFAULT_CATALOG}' is reserved for the bundled catalog"
                )
            categories_file = path / "categories.yaml"
            categories = (
                load_categories(categories_file)
                if categories_file.is_file()
                else bundled_categories
            )
            try:
                self._indexes[path.name] = build_lcat_index(
                    _read_yaml(path / "lcats.yaml"), categories
                )
            except (ValueError, KeyError) as e:
                raise ValueError(f"Invalid catalog '{path.name}': {e!r}") from e
            self._categories[path.name] = categories

    def names(self) -> list[str]:
        return list(self._indexes)

    def index(self, name: str) -> LcatIndex:
        try:
            return self._indexes[name]
        except KeyError:
            raise KeyError(f"Unknown catalog '{name}'") from None

    def categories(self, name: str) -> dict[str, list[str]]:
        self.index(name)
        return self._categories[name]

    def all_categories(self) -> dict[str, list[str]]:
        """Categories from every catalog merged by practice area, without duplicates."""
        merged: dict[str, list[str]] = {}
        for categories in self._categories.values():
            for practice_area, names in categories.items():
                bucket = merged.setdefault(practice_area, [])
                bucket.extend(n for n in names if n not in bucket)
        return merged
