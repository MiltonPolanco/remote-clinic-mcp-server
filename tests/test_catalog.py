from __future__ import annotations

import pytest

from remote_clinic_mcp.catalog import (
    CatalogError,
    check_requirements,
    get_preparation,
    list_preparations,
)
from remote_clinic_mcp.server import get_remote_server_time


def test_list_preparations_can_filter_category() -> None:
    result = list_preparations("renal")
    assert result["count"] == 1
    assert result["tests"][0]["test_code"] == "CREA"


def test_get_preparation_normalizes_code() -> None:
    assert get_preparation(" glu ")["minimum_fasting_hours"] == 8


def test_unknown_test_is_rejected() -> None:
    with pytest.raises(CatalogError, match="Unknown"):
        get_preparation("ABC")


def test_check_preparation_reports_missing_requirements() -> None:
    result = check_requirements(
        "GLU",
        fasting_hours=6,
        hours_since_alcohol=10,
        hours_since_strenuous_exercise=15,
    )
    assert result["ready_according_to_demo_policy"] is False
    assert len(result["unmet_requirements"]) == 2


def test_check_preparation_accepts_matching_facts() -> None:
    result = check_requirements(
        "GLU",
        fasting_hours=8,
        hours_since_alcohol=24,
        hours_since_strenuous_exercise=12,
    )
    assert result["ready_according_to_demo_policy"] is True
    assert result["unmet_requirements"] == []


def test_negative_hours_are_rejected() -> None:
    with pytest.raises(CatalogError, match="cannot be negative"):
        check_requirements("GLU", fasting_hours=-1)


def test_remote_time_uses_guatemala_offset_without_system_tzdata() -> None:
    result = get_remote_server_time()
    assert result["guatemala"].endswith("-06:00")
    assert result["transport"] == "streamable-http"
