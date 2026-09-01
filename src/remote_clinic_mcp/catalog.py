"""Preparation policies and requirement checks for lab tests."""

from __future__ import annotations

from typing import Any

PREPARATION_CATALOG: dict[str, dict[str, Any]] = {
    "GLU": {
        "test_name": "Fasting glucose",
        "category": "chemistry",
        "minimum_fasting_hours": 8,
        "water_allowed": True,
        "avoid_alcohol_hours": 24,
        "avoid_strenuous_exercise_hours": 12,
        "sample": "blood",
    },
    "HBA1C": {
        "test_name": "Glycated hemoglobin",
        "category": "chemistry",
        "minimum_fasting_hours": 0,
        "water_allowed": True,
        "avoid_alcohol_hours": 0,
        "avoid_strenuous_exercise_hours": 0,
        "sample": "blood",
    },
    "CHOL": {
        "test_name": "Lipid profile",
        "category": "chemistry",
        "minimum_fasting_hours": 9,
        "water_allowed": True,
        "avoid_alcohol_hours": 24,
        "avoid_strenuous_exercise_hours": 12,
        "sample": "blood",
    },
    "CREA": {
        "test_name": "Creatinine",
        "category": "renal",
        "minimum_fasting_hours": 0,
        "water_allowed": True,
        "avoid_alcohol_hours": 0,
        "avoid_strenuous_exercise_hours": 24,
        "sample": "blood",
    },
    "TSH": {
        "test_name": "Thyroid-stimulating hormone",
        "category": "endocrinology",
        "minimum_fasting_hours": 0,
        "water_allowed": True,
        "avoid_alcohol_hours": 0,
        "avoid_strenuous_exercise_hours": 0,
        "sample": "blood",
    },
}


class CatalogError(ValueError):
    """Raised when a catalog request is invalid."""


def list_preparations(category: str | None = None) -> dict[str, Any]:
    """Return preparation policies, optionally filtered by category."""
    normalized_category = category.strip().casefold() if category else None
    tests = [
        {"test_code": code, **details}
        for code, details in PREPARATION_CATALOG.items()
        if normalized_category is None
        or details["category"].casefold() == normalized_category
    ]
    return {"category": normalized_category, "count": len(tests), "tests": tests}


def get_preparation(test_code: str) -> dict[str, Any]:
    """Return the preparation policy for a specific test code."""
    normalized_code = test_code.strip().upper()
    details = PREPARATION_CATALOG.get(normalized_code)
    if details is None:
        raise CatalogError(f"Unknown laboratory test code: {test_code}")
    return {"test_code": normalized_code, **details}


def check_requirements(
    test_code: str,
    fasting_hours: float = 0,
    hours_since_alcohol: float | None = None,
    hours_since_strenuous_exercise: float | None = None,
) -> dict[str, Any]:
    """Compare supplied preparation facts with the required policy."""
    if fasting_hours < 0:
        raise CatalogError("fasting_hours cannot be negative")
    for field_name, value in (
        ("hours_since_alcohol", hours_since_alcohol),
        ("hours_since_strenuous_exercise", hours_since_strenuous_exercise),
    ):
        if value is not None and value < 0:
            raise CatalogError(f"{field_name} cannot be negative")

    policy = get_preparation(test_code)
    unmet: list[str] = []
    if fasting_hours < policy["minimum_fasting_hours"]:
        unmet.append(
            f"fasting: {fasting_hours:g} of {policy['minimum_fasting_hours']} required hours"
        )
    alcohol_requirement = policy["avoid_alcohol_hours"]
    if alcohol_requirement and (
        hours_since_alcohol is None or hours_since_alcohol < alcohol_requirement
    ):
        actual = (
            "not provided"
            if hours_since_alcohol is None
            else f"{hours_since_alcohol:g}"
        )
        unmet.append(f"alcohol: {actual} of {alcohol_requirement} required hours")
    exercise_requirement = policy["avoid_strenuous_exercise_hours"]
    if exercise_requirement and (
        hours_since_strenuous_exercise is None
        or hours_since_strenuous_exercise < exercise_requirement
    ):
        actual = (
            "not provided"
            if hours_since_strenuous_exercise is None
            else f"{hours_since_strenuous_exercise:g}"
        )
        unmet.append(
            f"strenuous exercise: {actual} of {exercise_requirement} required hours"
        )
    return {
        "test_code": policy["test_code"],
        "test_name": policy["test_name"],
        "ready_according_to_demo_policy": not unmet,
        "unmet_requirements": unmet,
        "policy": {
            key: policy[key]
            for key in (
                "minimum_fasting_hours",
                "avoid_alcohol_hours",
                "avoid_strenuous_exercise_hours",
                "water_allowed",
            )
        },
        "disclaimer": "Demo policy for academic testing.",
    }
