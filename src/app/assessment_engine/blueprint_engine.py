"""Docs: ./docs/functions/assessment_blueprint_engine.md | SPOT: ./SPOT.md#function-catalog"""
from __future__ import annotations

import random
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Iterable, Mapping, MutableMapping, Sequence
from uuid import UUID

from pydantic import ValidationError

from app.assessment_templates import get_assessment_template
from app.schemas.assessment_template import AssessmentTemplateSummary
from app.schemas.assessment_blueprint import (
    AssessmentBlueprintDocument,
    BucketThreshold,
    CriticalDimensionPolicy,
    DimensionBlueprint,
    DimensionScoringPolicy,
    DifficultyWeights,
    SampleItem,
)

if TYPE_CHECKING:
    from app.models.assessment_item_bank import (
        AssessmentItemBank,
        AssessmentItemStats,
    )

try:  # Python 3.11+
    from importlib import resources
except ImportError:  # pragma: no cover - fallback for legacy interpreters
    import importlib_resources as resources  # type: ignore[assignment]


BLUEPRINT_PACKAGE = "app.assessment_templates.blueprints"


@dataclass(slots=True)
class BlueprintItem:
    """Runtime item representation with scoring metadata."""

    code: str
    dimension: str
    difficulty: str
    weight: float = 1.0
    is_anchor: bool = False
    is_critical: bool = False
    discrimination: float | None = None
    exposure_ratio: float | None = None
    exposure_cap: float | None = None
    tags: tuple[str, ...] = field(default_factory=tuple)

    def selection_weight(self, weights: DifficultyWeights, min_weight: float) -> float:
        """Compute a sampling weight honoring difficulty, exposure, and discrimination."""

        difficulty_factor = getattr(weights, self.difficulty, 1.0)
        discrimination = self.discrimination if self.discrimination and self.discrimination > 0 else 1.0
        exposure_penalty = 1.0
        if self.exposure_ratio is not None:
            exposure_penalty = max(min_weight, 1.0 - self.exposure_ratio)
        return max(min_weight, difficulty_factor * discrimination * exposure_penalty)


class BlueprintLoadError(RuntimeError):
    """Raised when blueprint resources cannot be loaded or parsed."""


def load_blueprint_document(template_id: str) -> AssessmentBlueprintDocument:
    """Load and validate the blueprint document associated with a template."""

    base_path = resources.files(BLUEPRINT_PACKAGE)
    try:
        blueprint_path = base_path.joinpath(f"{template_id}.json")
    except FileNotFoundError as exc:  # pragma: no cover - defensive
        raise BlueprintLoadError(f"Blueprint package missing for {template_id}") from exc

    if not blueprint_path.is_file():
        raise BlueprintLoadError(f"No blueprint available for template '{template_id}'")

    raw = blueprint_path.read_text(encoding="utf-8")
    try:
        return AssessmentBlueprintDocument.model_validate_json(raw)
    except ValidationError as exc:  # pragma: no cover - surfaces configuration issues clearly
        raise BlueprintLoadError(f"Invalid blueprint for template '{template_id}': {exc}") from exc


def list_blueprint_ids() -> list[str]:
    """Return all blueprint identifiers bundled with the application."""

    base_path = resources.files(BLUEPRINT_PACKAGE)
    return [path.stem for path in base_path.iterdir() if path.suffix == ".json"]


def _as_item(sample: SampleItem, blueprint: AssessmentBlueprintDocument) -> BlueprintItem:
    """Convert a sample item specification into the runtime structure."""

    is_critical = sample.critical or sample.code in blueprint.critical.items
    dimension_policy = blueprint.critical.dimensions.get(sample.dimension)
    if dimension_policy and dimension_policy.mode == "knockout":
        is_critical = True
    return BlueprintItem(
        code=sample.code,
        dimension=sample.dimension,
        difficulty=sample.difficulty,
        weight=sample.weight,
        is_anchor=sample.anchor or sample.code in {anchor.code for anchor in blueprint.anchor_items},
        is_critical=is_critical or sample.code in blueprint.dimensions.get(sample.dimension, DimensionBlueprint()).critical_items,
        discrimination=sample.discrimination,
        exposure_ratio=sample.exposure_ratio,
        exposure_cap=sample.exposure_cap if sample.exposure_cap is not None else blueprint.exposure.default_cap,
        tags=tuple(sample.tags),
    )


def pool_from_item_bank(
    bank_items: Sequence["AssessmentItemBank"],
    stats: Mapping["UUID", "AssessmentItemStats"] | Sequence["AssessmentItemStats"] | None = None,
) -> list[BlueprintItem]:
    """Hydrate blueprint items from persisted bank records and optional statistics."""

    stats_lookup: dict[UUID, AssessmentItemStats] = {}
    if stats:
        if isinstance(stats, Mapping):
            stats_lookup = dict(stats)
        else:
            stats_lookup = {entry.item_id: entry for entry in stats}

    hydrated: list[BlueprintItem] = []
    for record in bank_items:
        stat = stats_lookup.get(record.item_id)
        discrimination = None
        exposure_ratio = None

        if stat and stat.discrimination is not None:
            discrimination = float(stat.discrimination)
        elif record.discrimination is not None:
            discrimination = float(record.discrimination)

        if stat and stat.exposure is not None:
            exposure_ratio = max(0.0, min(1.0, float(stat.exposure)))
        elif record.meta and isinstance(record.meta, dict):
            maybe_exposure = record.meta.get("exposure_ratio")
            if isinstance(maybe_exposure, (int, float)):
                exposure_ratio = max(0.0, min(1.0, float(maybe_exposure)))

        tags_value = ()
        if isinstance(record.tags, (list, tuple)):
            tags_value = tuple(str(tag) for tag in record.tags)

        hydrated.append(
            BlueprintItem(
                code=record.code,
                dimension=record.dimension,
                difficulty=record.difficulty,
                weight=float(record.weight) if record.weight is not None else 1.0,
                is_anchor=bool(record.anchor),
                is_critical=bool(record.critical),
                discrimination=discrimination,
                exposure_ratio=exposure_ratio,
                exposure_cap=float(record.exposure_cap)
                if record.exposure_cap is not None
                else None,
                tags=tags_value,
            )
        )

    return hydrated


def sample_pool_from_blueprint(document: AssessmentBlueprintDocument) -> list[BlueprintItem]:
    """Create a pool of items using the inline sample metadata if present."""

    return [_as_item(sample, document) for sample in document.sample_pool]


def _filter_exposure(items: list[BlueprintItem]) -> list[BlueprintItem]:
    """Filter out items that exceeded their exposure cap, keeping fallbacks."""

    if not items:
        return items
    limited = [
        item
        for item in items
        if item.exposure_cap is None
        or item.exposure_ratio is None
        or item.exposure_ratio < item.exposure_cap
    ]
    return limited or items


def _weighted_sample(
    rng: random.Random,
    candidates: list[BlueprintItem],
    count: int,
    difficulty_weights: DifficultyWeights,
    min_weight: float,
) -> list[BlueprintItem]:
    """Select items without replacement using proportional weights."""

    if count <= 0 or not candidates:
        return []

    working = candidates.copy()
    selected: list[BlueprintItem] = []
    for _ in range(min(count, len(working))):
        weights = [item.selection_weight(difficulty_weights, min_weight) for item in working]
        total = sum(weights)
        if total <= 0:
            choice_index = rng.randrange(len(working))
        else:
            pick = rng.random() * total
            cumulative = 0.0
            choice_index = 0
            for idx, weight in enumerate(weights):
                cumulative += weight
                if cumulative >= pick:
                    choice_index = idx
                    break
        selected.append(working.pop(choice_index))
    return selected


def _subtract_quota(quota: dict[str, int], difficulty: str) -> None:
    if difficulty in quota and quota[difficulty] > 0:
        quota[difficulty] -= 1


def select_items(
    document: AssessmentBlueprintDocument,
    pool: Sequence[BlueprintItem],
    seen_codes: Iterable[str] | None = None,
    rng: random.Random | None = None,
) -> list[BlueprintItem]:
    """Select items following the blueprint quotas, anchors, and exposure rules."""

    rng = rng or random.Random()
    seen = set(seen_codes or [])
    available = [item for item in pool if item.code not in seen]
    selected: list[BlueprintItem] = []
    quota_remaining: dict[str, dict[str, int]] = {
        dim: {"easy": spec.easy, "medium": spec.medium, "hard": spec.hard}
        for dim, spec in document.dimensions.items()
    }

    # 1) Explicit anchor items
    anchor_lookup = {anchor.code: anchor for anchor in document.anchor_items}
    for anchor_code, anchor in anchor_lookup.items():
        match = next((item for item in available if item.code == anchor_code), None)
        if not match:
            continue
        selected.append(match)
        available.remove(match)
        difficulty = anchor.difficulty or match.difficulty
        _subtract_quota(quota_remaining.setdefault(match.dimension, {}), difficulty)

    # 2) Additional anchors per dimension quota
    for dimension, spec in document.dimensions.items():
        required = max(0, spec.anchors - sum(1 for item in selected if item.dimension == dimension and item.is_anchor))
        if required == 0:
            continue
        candidates = [
            item
            for item in available
            if item.dimension == dimension and item.is_anchor
        ]
        candidates = _filter_exposure(candidates)
        picks = _weighted_sample(rng, candidates, required, document.difficulty_weights, document.exposure.min_weight)
        for item in picks:
            selected.append(item)
            available.remove(item)
            _subtract_quota(quota_remaining.setdefault(item.dimension, {}), item.difficulty)

    # 3) General selection per dimension/difficulty
    for dimension, difficulty_quota in quota_remaining.items():
        for difficulty, count in difficulty_quota.items():
            if count <= 0:
                continue
            candidates = [
                item
                for item in available
                if item.dimension == dimension and item.difficulty == difficulty and not item.is_anchor
            ]
            candidates = _filter_exposure(candidates)
            picks = _weighted_sample(rng, candidates, count, document.difficulty_weights, document.exposure.min_weight)
            for item in picks:
                selected.append(item)
                available.remove(item)
            remaining = count - len(picks)
            if remaining > 0:
                # Fallback: any remaining difficulty within the dimension
                fallback_candidates = [
                    item
                    for item in available
                    if item.dimension == dimension and not item.is_anchor
                ]
                fallback_candidates = _filter_exposure(fallback_candidates)
                fallback_picks = _weighted_sample(
                    rng,
                    fallback_candidates,
                    remaining,
                    document.difficulty_weights,
                    document.exposure.min_weight,
                )
                for item in fallback_picks:
                    selected.append(item)
                    available.remove(item)

    return selected


@dataclass
class DimensionScore:
    code: str
    raw_score: float
    max_score: float
    percentage: float
    bucket: str
    knockout_triggered: bool


@dataclass
class ScoreSummary:
    overall_score: float
    overall_bucket: str
    dimensions: list[DimensionScore]


def _bucket_for_value(thresholds: Sequence[BucketThreshold], value: float) -> str:
    for threshold in thresholds:
        if value >= threshold.min:
            return threshold.code
    return thresholds[-1].code if thresholds else "RED"


def score_responses(
    selected_items: Sequence[BlueprintItem],
    item_scores: Mapping[str, float],
    document: AssessmentBlueprintDocument,
) -> ScoreSummary:
    """Aggregate weighted scores per dimension and apply knockout logic."""

    item_map: MutableMapping[str, BlueprintItem] = {item.code: item for item in selected_items}
    dimension_policies: Mapping[str, DimensionScoringPolicy] = {
        policy.code: policy for policy in document.scoring.dimensions
    }
    critical_policy: Mapping[str, CriticalDimensionPolicy] = document.critical.dimensions
    dimension_results: list[DimensionScore] = []
    knockout_dimensions: set[str] = set()

    for dimension, policy in dimension_policies.items():
        items = [item for item in selected_items if item.dimension == dimension]
        if not items:
            dimension_results.append(
                DimensionScore(
                    code=dimension,
                    raw_score=0.0,
                    max_score=0.0,
                    percentage=0.0,
                    bucket=document.scoring.buckets[-1].code,
                    knockout_triggered=False,
                )
            )
            continue

        critical_conf = critical_policy.get(dimension)
        raw_score = 0.0
        max_score = 0.0
        knockout_triggered = False

        for item in items:
            response = item_scores.get(item.code, 0.0)
            response = max(0.0, min(1.0, response))
            if policy.item_weight_mode == "equal":
                item_weight = 1.0
            else:
                item_weight = item.weight

            if critical_conf and item.is_critical and critical_conf.mode == "weighted":
                item_weight *= critical_conf.weight_multiplier
            elif item.is_critical:
                item_weight *= policy.critical_weight_multiplier

            raw_score += response * item_weight
            max_score += item_weight

            if (
                policy.critical_knockout
                and item.is_critical
                and response < policy.critical_threshold
            ):
                knockout_triggered = True

            if (
                critical_conf
                and critical_conf.mode == "knockout"
                and item.is_critical
                and response < critical_conf.threshold
            ):
                knockout_triggered = True

        percentage = (raw_score / max_score * 100) if max_score > 0 else 0.0
        bucket = _bucket_for_value(document.scoring.buckets, percentage)
        if knockout_triggered:
            bucket = document.scoring.overall_knockout_bucket
            knockout_dimensions.add(dimension)
        dimension_results.append(
            DimensionScore(
                code=dimension,
                raw_score=raw_score,
                max_score=max_score,
                percentage=percentage,
                bucket=bucket,
                knockout_triggered=knockout_triggered,
            )
        )

    overall_score = 0.0
    for result in dimension_results:
        policy = dimension_policies[result.code]
        contribution = result.percentage * policy.weight
        overall_score += contribution

    overall_bucket = _bucket_for_value(document.scoring.buckets, overall_score)
    if knockout_dimensions:
        overall_bucket = document.scoring.overall_knockout_bucket

    return ScoreSummary(
        overall_score=overall_score,
        overall_bucket=overall_bucket,
        dimensions=dimension_results,
    )


def generate_selection_preview(template_id: str, seed: int | None = None) -> dict[str, object]:
    """Utility helper for API exposure: run a deterministic sample draw."""

    blueprint = load_blueprint_document(template_id)
    rng = random.Random(seed or 42)
    pool = sample_pool_from_blueprint(blueprint)
    selected = select_items(blueprint, pool, rng=rng)
    template = get_assessment_template(template_id)
    summary = AssessmentTemplateSummary.from_definition(template) if template else None
    return {
        "template": summary.model_dump() if summary else None,
        "blueprint": {
            "template_id": blueprint.template_id,
            "name": blueprint.blueprint_name,
            "version": blueprint.version,
            "anchors": blueprint.anchors,
            "total_quota": blueprint.total_quota,
        },
        "selected_items": [
            {
                "code": item.code,
                "dimension": item.dimension,
                "difficulty": item.difficulty,
                "weight": item.weight,
                "anchor": item.is_anchor,
                "critical": item.is_critical,
            }
            for item in selected
        ],
    }


__all__ = [
    "BlueprintItem",
    "BlueprintLoadError",
    "DimensionScore",
    "ScoreSummary",
    "generate_selection_preview",
    "list_blueprint_ids",
    "load_blueprint_document",
    "pool_from_item_bank",
    "sample_pool_from_blueprint",
    "score_responses",
    "select_items",
]
