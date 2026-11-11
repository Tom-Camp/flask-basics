# lcat-calc

Matches a candidate's work experience and education to labor categories (LCATs).

## How it works

An LCAT lists the categories it applies to, a minimum education level, and minimum years of experience.
The time covered by **all jobs** in any of the LCAT's categories is totaled: four jobs adding up to 10 years
in one category count as 10 years, and time in several of the LCAT's categories is added together. Dates that
overlap (concurrent jobs, or one job tagged with several of the LCAT's categories) are counted once.
A candidate qualifies when that total meets:

```
min_years + extra_years_for_education
```

- Extra years are 2 per education level the candidate is below the LCAT requirement
  (`other < associate < bachelors < masters < doctorate`). No degree counts as `other`.
- Jobs are matched on `(practice_area, category)`. A job whose category has no start date is skipped;
  a missing end date means the job is current.

## Usage

```python
from datetime import datetime
from lcat_calc import EducationLevel, Job, WorkCategory, derive_lcats

jobs = [
    Job(
        position="Designer",
        employer="Acme",
        categories=[
            WorkCategory(
                practice_area="Design",
                category="Visual Design",
                start_date=datetime(2018, 1, 1),
                end_date=datetime(2023, 1, 1),
            )
        ],
    )
]

derive_lcats(jobs, EducationLevel.BACHELORS)
# {"Visual Designer III": ["Designer at Acme from 2018-01-01 to 2023-01-01"], ...}
```

`derive_lcats(jobs, education=None, index=None, now=None)` returns `{lcat name: supporting jobs}`.
Pass `index` to use custom data and `now` to fix the date used for current jobs.

Other public functions: `highest_education(levels)`, `load_categories()` (practice area to categories),
`load_index(lcats_path, categories_path)`, `default_index()` (bundled data, cached per process; call
`default_index.cache_clear()` to reload), and `build_lcat_index(lcat_data, categories)`.

## Catalogs

`CatalogRegistry` manages named catalogs: the bundled `default` plus any in a directory you point it at.
Each subfolder is one catalog:

```
catalogs/
  acme/
    lcats.yaml
    categories.yaml   # optional; the bundled categories are used when absent
```

```python
from pathlib import Path
from lcat_calc import CatalogRegistry, derive_lcats

registry = CatalogRegistry(Path("catalogs"))
registry.names()  # ["default", "acme"]
derive_lcats(jobs, education, index=registry.index("acme"))
```

Every catalog is validated when the registry is built (an invalid one raises `ValueError` naming it), and
`default` is reserved. `categories(name)` returns one catalog's categories; `all_categories()` merges them
all by practice area, which is useful for a UI where a job can be tagged once and scored against any catalog.

## Data

Both files live in `src/lcat_calc/data/` and ship with the package.

`categories.yaml` maps practice areas to category names:

```yaml
Design:
- Visual Design
- Theme Designer
```

`lcats.yaml` has an optional `experience_templates` map and a flat `lcats` list:

```yaml
experience_templates:
  non_leadership: Work on Direct Client Assignments as a Team Member. ...

lcats:
  - name: Visual Designer III
    education: associate          # an EducationLevel value
    min_years: 3
    experience_template: non_leadership   # or an inline `experience: ...`
    categories:
      - Visual Design
      - Theme Designer
```

Practice areas are not repeated in `lcats.yaml`; each category name is looked up in `categories.yaml`.
A category listed under several practice areas is indexed under each. Loading raises `ValueError` for an
unknown category or experience template, and pydantic rejects an invalid `education` value.

## API reference

See [docs/api.md](docs/api.md) for every public function, class, and exception.

## Development

```bash
cd packages/lcat_calc
uv run --isolated pytest
```
