"""Docs: ./docs/functions/assessment_blueprint_engine.md | SPOT: ./SPOT.md#function-catalog"""
from __future__ import annotations

from typing import Dict, List, Literal

from enum import Enum

from pydantic import BaseModel, ConfigDict, Field, RootModel, model_validator

from app.schemas.assessment_template import AssessmentTemplateSummary

ItemDifficulty = Literal["easy", "medium", "hard"]

class DifficultyQuota(BaseModel):
    """Requested number of items per difficulty bucket."""

    easy: int = Field(default=0, ge=0)
    medium: int = Field(default=0, ge=0)
    hard: int = Field(default=0, ge=0)

    model_config = ConfigDict(extra="forbid")

    @property
    def total(self) -> int:
        return self.easy + self.medium + self.hard


class AnchorItem(BaseModel):
    """Explicit anchor allocation for deterministic inclusion."""

    code: str = Field(..., description="Stable item identifier.")
    dimension: str = Field(..., description="Blueprint dimension this anchor belongs to.")
    difficulty: ItemDifficulty | None = Field(
        default=None,
        description="Optional hint to decrement the correct difficulty quota.",
    )

    model_config = ConfigDict(extra="forbid")


class DimensionBlueprint(BaseModel):
    """Blueprint quotas and metadata for one assessment dimension."""

    easy: int = Field(default=0, ge=0)
    medium: int = Field(default=0, ge=0)
    hard: int = Field(default=0, ge=0)
    anchors: int = Field(default=0, ge=0)
    critical_items: List[str] = Field(default_factory=list)

    model_config = ConfigDict(extra="forbid")

    @property
    def quota(self) -> DifficultyQuota:
        return DifficultyQuota(easy=self.easy, medium=self.medium, hard=self.hard)

    @model_validator(mode="after")
    def validate_anchor_quota(self) -> "DimensionBlueprint":
        if self.anchors > self.quota.total:
            raise ValueError("anchor quota cannot exceed total quota for dimension")
        return self


class CriticalMode(str, Enum):
    """Supported critical handling strategies."""

    KNOCKOUT = "knockout"
    WEIGHTED = "weighted"


class CriticalDimensionPolicy(BaseModel):
    """Critical handling rules for a dimension."""

    mode: CriticalMode = Field(default=CriticalMode.WEIGHTED)
    threshold: float = Field(default=0.5, ge=0.0, le=1.0)
    weight_multiplier: float = Field(default=3.0, ge=1.0)

    model_config = ConfigDict(extra="forbid")


class CriticalBlueprint(BaseModel):
    """Global critical item and dimension policy definitions."""

    items: List[str] = Field(default_factory=list)
    dimensions: Dict[str, CriticalDimensionPolicy] = Field(default_factory=dict)

    model_config = ConfigDict(extra="forbid")


class BucketThreshold(BaseModel):
    """Threshold definition for qualitative score buckets."""

    code: str
    min: float = Field(..., ge=0, le=100)

    model_config = ConfigDict(extra="forbid")


class DimensionScoringPolicy(BaseModel):
    """Scoring behaviour for an individual dimension."""

    code: str
    weight: float = Field(..., gt=0)
    critical_knockout: bool = False
    critical_threshold: float = Field(default=0.5, ge=0.0, le=1.0)
    item_weight_mode: Literal["use_item_weight", "equal"] = "use_item_weight"
    critical_weight_multiplier: float = Field(default=3.0, ge=1.0)

    model_config = ConfigDict(extra="forbid")


class ScoringBlueprint(BaseModel):
    """Aggregation and bucket calculation rules."""

    dimensions: List[DimensionScoringPolicy]
    buckets: List[BucketThreshold] = Field(
        default_factory=lambda: [
            BucketThreshold(code="GREEN", min=80),
            BucketThreshold(code="YELLOW", min=60),
            BucketThreshold(code="ORANGE", min=40),
            BucketThreshold(code="RED", min=0),
        ]
    )
    overall_knockout_bucket: str = "RED"

    model_config = ConfigDict(extra="forbid")

    @model_validator(mode="after")
    def validate_weights(self) -> "ScoringBlueprint":
        total = sum(d.weight for d in self.dimensions)
        if abs(total - 1.0) > 1e-6:
            raise ValueError("dimension weights must sum to 1.0")
        return self

    @model_validator(mode="after")
    def validate_bucket_order(self) -> "ScoringBlueprint":
        mins = [bucket.min for bucket in self.buckets]
        if mins != sorted(mins, reverse=True):
            raise ValueError("bucket thresholds must be provided in descending order")
        return self


class DifficultyWeights(BaseModel):
    """Optional weighting factors per difficulty for selection priority."""

    easy: float = Field(default=1.0, ge=0.0)
    medium: float = Field(default=1.2, ge=0.0)
    hard: float = Field(default=1.4, ge=0.0)

    model_config = ConfigDict(extra="forbid")


class ExposureSettings(BaseModel):
    """Global exposure defaults for selection balancing."""

    default_cap: float | None = Field(default=0.25, ge=0.0, le=1.0)
    min_weight: float = Field(default=0.05, ge=0.0)

    model_config = ConfigDict(extra="forbid")


class SampleItem(BaseModel):
    """Inline sample item metadata to exercise the blueprint logic."""

    code: str
    dimension: str
    difficulty: ItemDifficulty
    weight: float = 1.0
    anchor: bool = False
    critical: bool = False
    discrimination: float | None = None
    exposure_ratio: float | None = Field(default=None, ge=0.0, le=1.0)
    exposure_cap: float | None = Field(default=None, ge=0.0, le=1.0)
    tags: List[str] = Field(default_factory=list)

    model_config = ConfigDict(extra="forbid")


class AssessmentBlueprintDocument(BaseModel):
    """Complete blueprint specification for an assessment version."""

    template_id: str
    blueprint_name: str
    version: str
    anchors: int = Field(default=0, ge=0)
    dimensions: Dict[str, DimensionBlueprint]
    anchor_items: List[AnchorItem] = Field(default_factory=list)
    difficulty_weights: DifficultyWeights = Field(default_factory=DifficultyWeights)
    exposure: ExposureSettings = Field(default_factory=ExposureSettings)
    critical: CriticalBlueprint = Field(default_factory=CriticalBlueprint)
    scoring: ScoringBlueprint
    sample_pool: List[SampleItem] = Field(default_factory=list)

    model_config = ConfigDict(extra="forbid")

    @property
    def total_quota(self) -> int:
        return sum(d.quota.total for d in self.dimensions.values())

    @model_validator(mode="after")
    def validate_anchor_counts(self) -> "AssessmentBlueprintDocument":
        dimension_anchor_total = sum(d.anchors for d in self.dimensions.values())
        anchor_item_total = len(self.anchor_items)
        expected = max(dimension_anchor_total, anchor_item_total)
        if expected > self.anchors:
            raise ValueError(
                "declared anchors must cover explicit per-dimension and listed anchor items"
            )
        return self

    @model_validator(mode="after")
    def validate_dimension_alignment(self) -> "AssessmentBlueprintDocument":
        dimension_codes = set(self.dimensions.keys())
        scoring_codes = {rule.code for rule in self.scoring.dimensions}
        missing = dimension_codes.symmetric_difference(scoring_codes)
        if missing:
            raise ValueError(
                "blueprint and scoring dimensions must match exactly; mismatches: "
                + ", ".join(sorted(missing))
            )
        critical_codes = set(self.critical.dimensions.keys())
        invalid_critical = critical_codes - dimension_codes
        if invalid_critical:
            raise ValueError(
                "critical dimension policies reference unknown dimensions: "
                + ", ".join(sorted(invalid_critical))
            )
        return self


BlueprintRegistry = RootModel[Dict[str, AssessmentBlueprintDocument]]


class BlueprintSummary(BaseModel):
    """Lightweight metadata representation for blueprint listings."""

    template_id: str
    blueprint_name: str
    version: str
    anchors: int
    total_quota: int

    model_config = ConfigDict(extra="forbid")


class BlueprintPreviewItem(BaseModel):
    """Selected item payload used in previews and testing."""

    code: str
    dimension: str
    difficulty: ItemDifficulty
    weight: float
    anchor: bool
    critical: bool

    model_config = ConfigDict(extra="forbid")


class BlueprintPreviewResponse(BaseModel):
    """Preview payload bundling template, blueprint, and item info."""

    template: AssessmentTemplateSummary | None
    blueprint: BlueprintSummary
    items: List[BlueprintPreviewItem]

    model_config = ConfigDict(extra="forbid", arbitrary_types_allowed=True)


__all__ = [
    "AssessmentBlueprintDocument",
    "BlueprintPreviewItem",
    "BlueprintPreviewResponse",
    "BlueprintSummary",
    "AnchorItem",
    "BlueprintRegistry",
    "CriticalBlueprint",
    "CriticalDimensionPolicy",
    "DimensionBlueprint",
    "DimensionScoringPolicy",
    "DifficultyQuota",
    "DifficultyWeights",
    "ExposureSettings",
    "SampleItem",
    "ScoringBlueprint",
]
