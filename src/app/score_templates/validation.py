# Docs: ./docs/functions/score_template_registry.md | SPOT: ./SPOT.md#function-catalog
"""Schema-level validation helpers for score template resources."""

from __future__ import annotations

import json
import math
from functools import lru_cache
from importlib import resources
from typing import Any, Dict, Iterable

from jsonschema import Draft202012Validator
from pydantic import ValidationError

from .schema import ScoreTemplateDefinition

SCHEMA_RESOURCE = "score_template.schema.json"


@lru_cache(maxsize=1)
def load_schema() -> Dict[str, Any]:
    """Load the canonical JSON schema shipped with the package."""

    schema_resource = resources.files("app.score_templates.schemas").joinpath(SCHEMA_RESOURCE)
    return json.loads(schema_resource.read_text(encoding="utf-8"))


def validate_structure(document: Dict[str, Any]) -> None:
    """Validate raw data against the JSON Schema contract."""

    validator = Draft202012Validator(load_schema())
    errors = sorted(validator.iter_errors(document), key=lambda err: list(err.path))
    if errors:
        formatted = "\n".join(
            f"{'/'.join(str(part) for part in error.path)}: {error.message}"
            for error in errors
        )
        raise ValueError(f"Schema validation failed:\n{formatted}")


def _assert_weights_sum_to_one(dimensions: Iterable[Dict[str, Any]], tol: float = 1e-4) -> None:
    weights = [float(d["weight"]) for d in dimensions]
    total = math.fsum(weights)
    if not math.isclose(total, 1.0, rel_tol=0, abs_tol=tol):
        raise ValueError(f"dimension weights must sum to 1.0 (got {total:.6f})")


def _assert_bucket_ranges(buckets: Iterable[Dict[str, Any]]) -> None:
    buckets_list = sorted(buckets, key=lambda bucket: (bucket["range"]["min"], bucket["range"]["max"]))
    if not buckets_list:
        raise ValueError("at least one bucket is required")

    previous_max = 0.0
    for index, bucket in enumerate(buckets_list):
        bucket_min = bucket["range"]["min"]
        bucket_max = bucket["range"]["max"]
        if bucket_min > bucket_max:
            raise ValueError(f"bucket {bucket['code']}: min cannot exceed max")
        if index == 0 and bucket_min > 0:
            raise ValueError("first bucket must start at 0")
        if bucket_min < previous_max - 1e-9:
            raise ValueError("bucket ranges overlap or are unordered")
        previous_max = bucket_max

    if buckets_list[-1]["range"]["max"] < 100:
        raise ValueError("last bucket must end at 100")


def _assert_dimension_overrides(dimensions: Iterable[Dict[str, Any]]) -> None:
    for dimension in dimensions:
        overrides = dimension.get("bucket_overrides") or {}
        red_max = overrides.get("RED_MAX")
        yellow_max = overrides.get("YELLOW_MAX")
        if red_max is None or yellow_max is None:
            continue
        if not (0 <= red_max < yellow_max <= 100):
            raise ValueError(f"{dimension['code']}.bucket_overrides invalid thresholds")


def _assert_tip_alignment(document: Dict[str, Any]) -> None:
    dimension_codes = {dimension["code"] for dimension in document.get("dimensions", [])}
    for key in (document.get("tips") or {}):
        if key not in dimension_codes:
            raise ValueError(f"tips entry '{key}' has no matching dimension")


def validate_template(document: Dict[str, Any]) -> ScoreTemplateDefinition:
    """Validate and coerce a score template document."""

    validate_structure(document)
    _assert_weights_sum_to_one(document["dimensions"])
    _assert_bucket_ranges(document["buckets"])
    _assert_dimension_overrides(document["dimensions"])
    _assert_tip_alignment(document)

    try:
        return ScoreTemplateDefinition.model_validate(document)
    except ValidationError as exc:
        raise ValueError("Pydantic validation failed") from exc


__all__ = ["validate_template", "validate_structure", "load_schema"]
