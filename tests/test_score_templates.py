"""Tests for score template registry and API exposure."""

from __future__ import annotations

import json
from importlib import resources

import pytest
from fastapi.testclient import TestClient

from app.score_templates import get_score_template, list_score_templates
from app.score_templates.schema import ScoreTemplateDefinition, ScoreTemplateSummary
from app.score_templates.validation import validate_template


def test_registry_exposes_performance_template() -> None:
    summaries = list_score_templates()
    assert isinstance(summaries, list)
    assert any(isinstance(summary, ScoreTemplateSummary) for summary in summaries)
    assert any(summary.key == "performance_health_v1" for summary in summaries)

    definition = get_score_template("performance_health_v1")
    assert isinstance(definition, ScoreTemplateDefinition)
    assert definition.st_meta.name == "Performance Health Score"
    assert definition.summary().dimension_count == 3
    assert definition.buckets[0].range.min == 0
    assert definition.buckets[-1].range.max == 100


def test_score_template_api_endpoints(client: TestClient) -> None:
    response = client.get("/api/v1/score-templates/")
    assert response.status_code == 200
    payload = response.json()
    assert any(item["key"] == "performance_health_v1" for item in payload)

    detail = client.get("/api/v1/score-templates/performance_health_v1")
    assert detail.status_code == 200
    data = detail.json()
    assert data["st_meta"]["name"] == "Performance Health Score"
    assert data["dimensions"][0]["code"] in {"REACH", "QUALITY", "AGILITY"}


def test_score_template_not_found(client: TestClient) -> None:
    response = client.get("/api/v1/score-templates/unknown")
    assert response.status_code == 404
    assert response.json()["detail"] == "Score template not found"


def test_validate_template_rejects_bad_weights() -> None:
    doc_text = resources.files("app.score_templates.definitions").joinpath("performance_health_v1.json").read_text(
        encoding="utf-8"
    )
    document = json.loads(doc_text)
    document["dimensions"][0]["weight"] = 0.9

    with pytest.raises(ValueError) as exc:
        validate_template(document)

    assert "weights" in str(exc.value)
