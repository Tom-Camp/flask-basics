# lcat_calc API reference

All public names are importable from the top-level package:

```python
from lcat_calc import (
    DEFAULT_CATALOG,
    CatalogRegistry,
    EducationLevel,
    Job,
    JobTerm,
    LcatDefinition,
    LcatIndex,
    WorkCategory,
    build_lcat_index,
    calculate_lcats,
    default_index,
    derive_lcats,
    get_category_terms,
    highest_education,
    load_categories,
    load_index,
)
```

Requires Python >= 3.14, `pydantic>=2`, `ruamel-yaml`. See the [README](../README.md) for the matching rules and data file formats.

## Models (`lcat_calc.models`)

All models are pydantic `BaseModel`s.

### `EducationLevel(StrEnum)`

Values, lowest to highest rank: `other`, `associate`, `bachelors`, `masters`, `doctorate`.

| Member | Description |
| --- | --- |
| `rank -> int` | Zero-based position in the ordering above (`OTHER` = 0). |

### `WorkCategory`

A category a candidate worked in during one job.

| Field | Type | Default | Notes |
| --- | --- | --- | --- |
| `practice_area` | `str` | required | |
| `category` | `str` | required | |
| `start_date` | `datetime \| None` | `None` | Categories without one are ignored. |
| `end_date` | `datetime \| None` | `None` | `None` means the job is current. |

### `Job`

| Field | Type | Default |
| --- | --- | --- |
| `position` | `str \| None` | `None` |
| `employer` | `str \| None` | `None` |
| `categories` | `list[WorkCategory]` | `[]` |

### `JobTerm`

Total experience in one category.

| Field | Type | Notes |
| --- | --- | --- |
| `term` | `int` | Total days, overlaps counted once. |
| `spans` | `list[tuple[datetime, datetime]]` | Start/end of each job in the category; used to combine categories without double-counting. |
| `jobs` | `list[str]` | Descriptions like `"Designer at Acme from 2018-01-01 to 2023-01-01"` (`current` when no end date). |

### `CategoryRef` (frozen)

`practice_area: str`, `category: str`. Hashable pair identifying a category.

### `LcatDefinition`

| Field | Type | Notes |
| --- | --- | --- |
| `name` | `str` | |
| `education` | `EducationLevel` | Minimum education. |
| `min_years` | `int` | Minimum years of experience. |
| `experience` | `str` | Experience description (resolved from a template if one was used). |
| `categories` | `list[CategoryRef]` | |

### `LcatIndex`

LCATs keyed by `(practice_area, category)`.

- `by_category: dict[tuple[str, str], list[LcatDefinition]]`
- `for_category(practice_area, category) -> list[LcatDefinition]`: matching LCATs, or `[]`.

## Calculation (`lcat_calc.calculator`)

### `derive_lcats(jobs, education=None, index=None, now=None) -> dict[str, list[str]]`

Main entry point: `calculate_lcats(get_category_terms(jobs, now), education, index)`.

| Param | Description |
| --- | --- |
| `jobs` | `list[Job]` |
| `education` | Candidate's highest `EducationLevel`; `None` is treated as `other`. |
| `index` | `LcatIndex` to match against; defaults to `default_index()`. |
| `now` | Date used as the end of current jobs; defaults to `datetime.now()`. |

Returns `{lcat name: supporting job descriptions}` (deduplicated, order preserved). Only qualifying LCATs are included.

### `get_category_terms(jobs, now=None) -> dict[str, dict[str, JobTerm]]`

Totals days per `{practice_area: {category: JobTerm}}` across all jobs, counting overlapping dates once. Categories with no `start_date` are skipped.

### `calculate_lcats(terms, education=None, index=None) -> dict[str, list[str]]`

Matches pre-computed terms to LCATs. An LCAT qualifies when the days covered by the union of `spans` across its matched categories (overlaps counted once), divided by 365, is >= `min_years + 2 * max(lcat.education.rank - candidate.rank, 0)`.

### `highest_education(levels) -> EducationLevel | None`

Highest-ranked level in an iterable; `None` values are ignored; returns `None` if nothing remains.

### Helpers (not exported at top level)

- `merge_spans_days(spans) -> int`: days covered by `(start, end)` spans, overlaps counted once.
- `get_experience_days(cat, now=None) -> int`: days between start and end (or `now`/today). Raises `ValueError` if `start_date` is missing.
- `get_additional_education_years(lcat_education, user_education) -> int`: 2 years per level below the requirement, never negative.

## Loading (`lcat_calc.loader`)

| Function | Description |
| --- | --- |
| `load_categories(path=None) -> dict[str, list[str]]` | Practice area to category names. Defaults to bundled `categories.yaml`; empty file gives `{}`. |
| `load_index(lcats_path=None, categories_path=None) -> LcatIndex` | Loads and validates an index; each path defaults to the bundled file. |
| `build_lcat_index(lcat_data, categories) -> LcatIndex` | Builds an index from already-parsed data (`{"experience_templates": ..., "lcats": [...]}`). A category listed under several practice areas is indexed under each. Raises `ValueError` for an unknown category or experience template; pydantic raises on an invalid `education`. |
| `default_index() -> LcatIndex` | Bundled index, cached per process. Call `default_index.cache_clear()` to reload. |

## Catalogs (`lcat_calc.catalogs`)

`DEFAULT_CATALOG = "default"`: reserved name of the bundled catalog.

### `CatalogRegistry(directory: Path | None = None)`

Holds the bundled catalog plus one per subfolder of `directory` that contains `lcats.yaml` (optional `categories.yaml`; bundled categories are used when absent). Subfolders are loaded in sorted order and validated on construction.

Raises:
- `FileNotFoundError` if `directory` is given but isn't a directory.
- `ValueError` if a subfolder is named `default`, or a catalog is invalid (message names the catalog).

| Method | Description |
| --- | --- |
| `names() -> list[str]` | Catalog names, `default` first. |
| `index(name) -> LcatIndex` | Raises `KeyError` for an unknown catalog. |
| `categories(name) -> dict[str, list[str]]` | One catalog's categories. Raises `KeyError` if unknown. |
| `all_categories() -> dict[str, list[str]]` | Categories of all catalogs merged by practice area, deduplicated. |

## Example

```python
from pathlib import Path
from lcat_calc import CatalogRegistry, EducationLevel, derive_lcats

registry = CatalogRegistry(Path("catalogs"))
result = derive_lcats(jobs, EducationLevel.MASTERS, index=registry.index("acme"))
for lcat, evidence in result.items():
    print(lcat, evidence)
```
