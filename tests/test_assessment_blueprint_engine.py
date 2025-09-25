"""Docs: ./docs/functions/assessment_blueprint_engine.md | SPOT: ./SPOT.md#function-catalog"""
from __future__ import annotations

import random
from decimal import Decimal
from uuid import uuid4

from app.assessment_engine import (
    ScoreSummary,
    load_blueprint_document,
    pool_from_item_bank,
    sample_pool_from_blueprint,
    score_responses,
    select_items,
)
from app.schemas.assessment_blueprint import BlueprintPreviewItem
from app.models.assessment_item_bank import AssessmentItemBank, AssessmentItemStats

BLUEPRINT_ID = "course_gdpr_social_email_cookies_v1_no"


def test_blueprint_document_metadata() -> None:
    document = load_blueprint_document(BLUEPRINT_ID)
    assert document.blueprint_name == "Safety Culture & Leadership Form A"
    assert document.anchors == 2
    assert document.total_quota == 20


def test_select_items_matches_blueprint() -> None:
    document = load_blueprint_document(BLUEPRINT_ID)
    pool = sample_pool_from_blueprint(document)
    rng = random.Random(2024)
    selected = select_items(document, pool, rng=rng)

    assert len(selected) == document.total_quota
    safety_items = [item for item in selected if item.dimension == "SAFETY"]
    culture_items = [item for item in selected if item.dimension == "CULTURE"]
    leadership_items = [item for item in selected if item.dimension == "LEADERSHIP"]

    assert len(safety_items) == 8
    assert len(culture_items) == 6
    assert len(leadership_items) == 6

    anchors = [item for item in selected if item.is_anchor]
    assert {item.code for item in anchors} >= {"safety_anchor_ppe", "culture_anchor_voice"}

    safety_by_difficulty = {bucket: sum(1 for item in safety_items if item.difficulty == bucket) for bucket in {"easy", "medium", "hard"}}
    assert safety_by_difficulty["easy"] == 2
    assert safety_by_difficulty["medium"] == 4
    assert safety_by_difficulty["hard"] == 2


def test_score_responses_applies_knockout() -> None:
    document = load_blueprint_document(BLUEPRINT_ID)
    pool = sample_pool_from_blueprint(document)
    rng = random.Random(17)
    selected = select_items(document, pool, rng=rng)

    item_scores = {item.code: 0.9 for item in selected}
    item_scores["safety_anchor_ppe"] = 0.2  # Trigger knockout on safety
    summary: ScoreSummary = score_responses(selected, item_scores, document)

    safety_dimension = next(dim for dim in summary.dimensions if dim.code == "SAFETY")
    assert safety_dimension.knockout_triggered is True
    assert summary.overall_bucket == document.scoring.overall_knockout_bucket


def test_pool_from_item_bank_prefers_stats_over_record() -> None:
    version_id = uuid4()
    item_id = uuid4()
    record = AssessmentItemBank()
    record.item_id = item_id
    record.version_id = version_id
    record.code = "safety_anchor_ppe"
    record.dimension = "SAFETY"
    record.difficulty = "medium"
    record.weight = Decimal("2.5")
    record.critical = True
    record.anchor = True
    record.discrimination = Decimal("0.40")
    record.exposure_cap = Decimal("0.25")
    record.tags = ["PPE", "anchor"]
    record.meta = {"exposure_ratio": 0.18}
    stats = AssessmentItemStats()
    stats.item_id = item_id
    stats.shown = 25
    stats.correct = 18
    stats.facility = Decimal("0.72")
    stats.discrimination = Decimal("0.55")
    stats.exposure = Decimal("0.32")

    hydrated = pool_from_item_bank([record], [stats])
    assert len(hydrated) == 1
    item = hydrated[0]
    assert item.code == "safety_anchor_ppe"
    assert item.is_anchor is True
    assert item.is_critical is True
    assert item.discrimination == 0.55
    assert item.exposure_ratio == 0.32
    assert item.exposure_cap == 0.25
    assert item.tags == ("PPE", "anchor")


def test_blueprint_preview_endpoint(client) -> None:
    response = client.get("/api/v1/assessment/blueprint")
    assert response.status_code == 200
    payload = response.json()
    assert any(item["template_id"] == BLUEPRINT_ID for item in payload)

    preview_response = client.get(f"/api/v1/assessment/blueprint/{BLUEPRINT_ID}/preview", params={"seed": 99})
    assert preview_response.status_code == 200
    preview_payload = preview_response.json()
    assert preview_payload["blueprint"]["template_id"] == BLUEPRINT_ID
    assert len(preview_payload["items"]) == 20
    first_item = BlueprintPreviewItem.model_validate(preview_payload["items"][0])
    assert first_item.dimension in {"SAFETY", "CULTURE", "LEADERSHIP"}
