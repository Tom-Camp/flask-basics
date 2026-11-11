from datetime import datetime

import pytest

from lcat_calc import (
    CatalogRegistry,
    EducationLevel,
    Job,
    WorkCategory,
    build_lcat_index,
    default_index,
    derive_lcats,
)


def _job(category: str, practice_area: str, years: int) -> Job:
    cat = WorkCategory(
        practice_area=practice_area,
        category=category,
        start_date=datetime(2000, 1, 1),
        end_date=datetime(2000 + years, 1, 1),
    )
    return Job(position="Dev", employer="Acme", categories=[cat])


def test_bundled_data_is_valid_and_indexed():
    names = {
        lcat.name for lcat in default_index().for_category("Design", "Visual Design")
    }
    assert "Visual Designer III" in names


def test_unknown_category_rejected():
    data = {
        "lcats": [
            {
                "name": "X",
                "education": "other",
                "min_years": 1,
                "experience": "e",
                "categories": ["Nope"],
            }
        ]
    }
    with pytest.raises(ValueError, match="unknown category"):
        build_lcat_index(data, {"Design": ["Visual Design"]})


def test_shared_category_indexed_under_each_practice_area():
    data = {
        "lcats": [
            {
                "name": "X",
                "education": "other",
                "min_years": 1,
                "experience": "e",
                "categories": ["Shared"],
            }
        ]
    }
    index = build_lcat_index(data, {"A": ["Shared"], "B": ["Shared"]})
    assert index.for_category("A", "Shared")
    assert index.for_category("B", "Shared")


def test_education_offsets_required_experience():
    jobs = [_job("Visual Design", "Design", 4)]
    # Visual Designer III needs 3 years with an associate degree.
    assert "Visual Designer III" in derive_lcats(jobs, EducationLevel.ASSOCIATE)
    # With no degree, 2 extra years are required, so 4 years falls short.
    assert "Visual Designer III" not in derive_lcats(jobs, None)


def test_current_job_uses_injected_now():
    cat = WorkCategory(
        practice_area="Design",
        category="Visual Design",
        start_date=datetime(2000, 1, 1),
    )
    jobs = [Job(position="Dev", employer="Acme", categories=[cat])]
    result = derive_lcats(jobs, EducationLevel.ASSOCIATE, now=datetime(2004, 1, 1))
    assert result["Visual Designer III"] == ["Dev at Acme from 2000-01-01 to current"]


def _write_catalog(root, name, lcats, categories=None):
    d = root / name
    d.mkdir()
    (d / "lcats.yaml").write_text(lcats)
    if categories:
        (d / "categories.yaml").write_text(categories)


CUSTOM_LCATS = """
lcats:
  - name: Senior Visual Person
    education: other
    min_years: 1
    experience: x
    categories: [Visual Design]
"""


def test_registry_lists_default_and_custom_catalogs(tmp_path):
    _write_catalog(tmp_path, "acme", CUSTOM_LCATS)
    registry = CatalogRegistry(tmp_path)
    assert registry.names() == ["default", "acme"]

    jobs = [_job("Visual Design", "Design", 2)]
    assert list(derive_lcats(jobs, None, index=registry.index("acme"))) == [
        "Senior Visual Person"
    ]
    assert "Senior Visual Person" not in derive_lcats(
        jobs, None, index=registry.index("default")
    )


def test_registry_rejects_invalid_catalog_and_reserved_name(tmp_path):
    _write_catalog(tmp_path, "bad", CUSTOM_LCATS.replace("Visual Design", "Nope"))
    with pytest.raises(ValueError, match="Invalid catalog 'bad'"):
        CatalogRegistry(tmp_path)

    reserved = tmp_path / "r"
    reserved.mkdir()
    _write_catalog(reserved, "default", CUSTOM_LCATS)
    with pytest.raises(ValueError, match="reserved"):
        CatalogRegistry(reserved)


def test_registry_unknown_catalog_and_merged_categories(tmp_path):
    _write_catalog(
        tmp_path,
        "acme",
        CUSTOM_LCATS.replace("Visual Design", "Widgets"),
        "Ops:\n- Widgets\n",
    )
    registry = CatalogRegistry(tmp_path)
    with pytest.raises(KeyError):
        registry.index("nope")
    merged = registry.all_categories()
    assert "Widgets" in merged["Ops"] and "Visual Design" in merged["Design"]
