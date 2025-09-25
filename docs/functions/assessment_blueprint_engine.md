---
langs: [en, nb-NO]
lastUpdated: 2025-09-24
---

# Assessment Blueprint Engine — Overview

**en:** Stratified blueprint loader and selector powering adaptive assessment forms. Sources: `src/app/assessment_engine/blueprint_engine.py`, `src/app/assessment_engine/__init__.py`, `src/app/schemas/assessment_blueprint.py`, `src/app/api/v1/assessments.py`, `tests/test_assessment_blueprint_engine.py`.

**nb-NO:** Stratifisert blueprint-laster og trekker for adaptive vurderingsskjema. Kildebaner: `src/app/assessment_engine/blueprint_engine.py`, `src/app/assessment_engine/__init__.py`, `src/app/schemas/assessment_blueprint.py`, `src/app/api/v1/assessments.py`, `tests/test_assessment_blueprint_engine.py`.

**SPOT:** ./SPOT.md#function-catalog

## API

- `GET /api/v1/assessment/blueprint` – Lists bundled blueprint summaries for operators.
- `GET /api/v1/assessment/blueprint/{template_id}/preview` – Returns deterministic item selection previews (optional `seed`).
- Python helpers:
  - `load_blueprint_document(template_id)` – Parse blueprint JSON into validated model.
  - `select_items(document, pool, seen_codes=None, rng=None)` – Stratified sampling respecting quotas, anchors, exposure caps.
  - `score_responses(selected_items, item_scores, document)` – Weighted dimension scoring with knockout policies.
  - `generate_selection_preview(template_id, seed=None)` – Utility harness for API exposure/tests.
  - `pool_from_item_bank(records, stats=None)` – Merge persisted item bank rows with live stats before selection.

## Design

- Blueprint definitions live in `src/app/assessment_templates/blueprints/*.json` and follow the `AssessmentBlueprintDocument` schema (quotas, anchors, critical policies, scoring, sample pools).
- Selection honours three layers:
  1. Explicit anchor items → subtract matching difficulty quotas.
  2. Remaining per-dimension anchor quota.
  3. Difficulty buckets with weighted random sampling (difficulty factors, discrimination, exposure penalty with default cap fallback).
- Exposure caps default to blueprint `exposure.default_cap` unless item overrides.
- Scoring aggregates dimension scores with configurable weight strategies and supports two critical modes: knockout (bucket override) or weighted (multiplied weight).
- Preview endpoints reuse bundled sample pools so API consumers can verify quotas without hitting production item banks.
- `pool_from_item_bank` hydrates `BlueprintItem` objects from the Postgres item bank, preferring live discrimination/exposure metrics when stats exist.
- Error handling surfaces invalid/missing blueprint packages with `BlueprintLoadError` mapped to HTTP 404.

## Usage

```python
from app.assessment_engine import load_blueprint_document, sample_pool_from_blueprint, select_items, score_responses

document = load_blueprint_document("course_gdpr_social_email_cookies_v1_no")
pool = sample_pool_from_blueprint(document)
selected = select_items(document, pool, seen_codes={"safety_easy_intro_rules"})
responses = {item.code: 0.8 for item in selected}
summary = score_responses(selected, responses, document)
print(summary.overall_bucket)
```

When sourcing items from the persistent bank:

```python
from app.assessment_engine import pool_from_item_bank

pool = pool_from_item_bank(db_items, db_stats)
selected = select_items(document, pool, seen_codes=session_history)
```

HTTP preview example:

```bash
curl "http://localhost:8000/api/v1/assessment/blueprint/course_gdpr_social_email_cookies_v1_no/preview?seed=42"
```

## Changelog

### [Unreleased]
- 2025-09-24: Initial blueprint loader, selector, scoring engine, and API previews.
- 2025-09-24: Added item bank hydration helper aligning selection with persisted exposure statistics.

## Diagrams

```mermaid
digraph BlueprintFlow {
  rankdir=LR
  BlueprintJSON["Blueprint JSON\n(quotas, anchors)"]
  SamplePool["Sample Pool\n(items with stats)"]
  Selector["Stratified Selector"]
  Responses["Responses\n(normalised 0..1)"]
  Scorer["Scoring Engine\n(weights + knockout)"]
  Summary["Dimension & Total Summary"]

  BlueprintJSON -> Selector
  SamplePool -> Selector
  Selector -> Responses
  Responses -> Scorer
  Selector -> Scorer
  Scorer -> Summary
}
```
