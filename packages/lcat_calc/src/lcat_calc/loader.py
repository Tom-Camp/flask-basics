from functools import lru_cache
from importlib.resources import files
from pathlib import Path
from typing import Any

from ruamel.yaml import YAML

from lcat_calc.models import CategoryRef, LcatDefinition, LcatIndex


def _read_yaml(path: Path) -> Any:
    with open(path, "r") as fp:
        return YAML(typ="safe").load(fp)


def build_lcat_index(
    lcat_data: dict[str, Any], categories: dict[str, list[str]]
) -> LcatIndex:
    """
    Validate raw LCAT data and index it by (practice_area, category).
    A category listed under several practice areas in the categories data is indexed under each.
    :raises ValueError: if an LCAT references an unknown category or experience template
    """
    practice_areas: dict[str, list[str]] = {}
    for practice_area, names in categories.items():
        for name in names:
            practice_areas.setdefault(name, []).append(practice_area)

    templates: dict[str, str] = lcat_data.get("experience_templates", {})
    by_category: dict[tuple[str, str], list[LcatDefinition]] = {}
    for raw in lcat_data["lcats"]:
        refs: list[CategoryRef] = []
        for name in raw["categories"]:
            if name not in practice_areas:
                raise ValueError(f"LCAT '{raw['name']}' uses unknown category '{name}'")
            refs.extend(
                CategoryRef(practice_area=pa, category=name)
                for pa in practice_areas[name]
            )

        template = raw.get("experience_template")
        if template and template not in templates:
            raise ValueError(
                f"LCAT '{raw['name']}' uses unknown experience template '{template}'"
            )

        lcat = LcatDefinition(
            name=raw["name"],
            education=raw["education"],
            min_years=raw["min_years"],
            experience=templates[template] if template else raw["experience"],
            categories=refs,
        )
        for ref in refs:
            by_category.setdefault((ref.practice_area, ref.category), []).append(lcat)
    return LcatIndex(by_category=by_category)


def load_categories(path: Path | None = None) -> dict[str, list[str]]:
    """Practice areas mapped to their categories, defaulting to the data bundled with the package."""
    return (
        _read_yaml(path or Path(str(files("lcat_calc") / "data" / "categories.yaml")))
        or {}
    )


def load_index(
    lcats_path: Path | None = None, categories_path: Path | None = None
) -> LcatIndex:
    """Load an index from the given files, defaulting to the data bundled with the package."""
    data = files("lcat_calc") / "data"
    return build_lcat_index(
        _read_yaml(lcats_path or Path(str(data / "lcats.yaml"))),
        load_categories(categories_path),
    )


@lru_cache(maxsize=1)
def default_index() -> LcatIndex:
    """The bundled index, loaded once per process. Call default_index.cache_clear() to reload."""
    return load_index()
