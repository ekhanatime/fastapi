# Docs: ./docs/functions/score_template_registry.md | SPOT: ./SPOT.md#function-catalog
"""Typed Pydantic models for score template resources."""

from __future__ import annotations

from enum import Enum
from typing import Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class BucketCode(str, Enum):
    """Canonical identifiers for qualitative score buckets."""

    RED = "RED"
    YELLOW = "YELLOW"
    GREEN = "GREEN"


class ScoreTemplateScale(BaseModel):
    """Permitted global scale values."""

    min: float = Field(default=0, description="Minimum of the normalized scale (must stay at 0).")
    max: float = Field(default=100, description="Maximum of the normalized scale (must stay at 100).")

    model_config = ConfigDict(extra="forbid")

    @model_validator(mode="after")
    def enforce_bounds(self) -> "ScoreTemplateScale":
        if self.min != 0 or self.max != 100:
            raise ValueError("scale must be 0-100 to ensure comparable downstream analytics")
        return self


class ScoreTemplatePublicPolicy(BaseModel):
    """Visibility policy metadata for template publication."""

    allow_public: Optional[bool] = None
    only_from: Optional[str] = None
    min_orgs: Optional[int] = Field(default=None, ge=1)

    model_config = ConfigDict(extra="forbid")


class ScoreTemplateMeta(BaseModel):
    """Top-level descriptive metadata for a score template."""

    key: str
    name: str
    schema_version: str = Field(pattern=r"^[0-9]+\.[0-9]+\.[0-9]+$")
    scale: ScoreTemplateScale
    min_n: int = Field(default=0, ge=0)
    public_policy: Optional[ScoreTemplatePublicPolicy] = None

    model_config = ConfigDict(extra="forbid")


class ScoreBucketRange(BaseModel):
    """Numerical range covered by a qualitative bucket."""

    min: float = Field(ge=0, le=100)
    max: float = Field(ge=0, le=100)

    model_config = ConfigDict(extra="forbid")

    @model_validator(mode="after")
    def validate_range(self) -> "ScoreBucketRange":
        if self.min > self.max:
            raise ValueError("bucket range min cannot exceed max")
        return self


class ScoreBucket(BaseModel):
    """Bucket definition mapping ranges to qualitative outcomes."""

    code: BucketCode
    label: str
    color: str = Field(pattern=r"^#([0-9a-fA-F]{6})$")
    range: ScoreBucketRange
    actions: List[str] = Field(default_factory=list)
    feedback: Optional[str] = None

    model_config = ConfigDict(extra="forbid")


class DimensionBucketOverrides(BaseModel):
    """Optional per-dimension thresholds for qualitative bucket cut-offs."""

    RED_MAX: Optional[float] = Field(default=None, ge=0, le=100)
    YELLOW_MAX: Optional[float] = Field(default=None, ge=0, le=100)

    model_config = ConfigDict(extra="forbid")

    @model_validator(mode="after")
    def validate_order(self) -> "DimensionBucketOverrides":
        red, yellow = self.RED_MAX, self.YELLOW_MAX
        if red is not None and yellow is not None and not (0 <= red < yellow <= 100):
            raise ValueError("bucket override thresholds must respect RED < YELLOW <= 100")
        return self


class TransformCode(str, Enum):
    """Allowed score transformation codes."""

    AVG_TIMES_20 = "avg*20"
    SCALE_1_TO_5 = "scale_1to5"
    CUSTOM = "custom"


class ScoreTemplateDimension(BaseModel):
    """Dimension metadata and weighting instructions."""

    code: str
    name: str
    weight: float = Field(gt=0, le=1)
    items: List[str] = Field(min_length=1)
    transform: TransformCode = TransformCode.AVG_TIMES_20
    bucket_overrides: Optional[DimensionBucketOverrides] = None

    model_config = ConfigDict(extra="forbid")

    @field_validator("items")
    @classmethod
    def ensure_unique_items(cls, value: List[str]) -> List[str]:
        if len(value) != len(set(value)):
            raise ValueError("dimension items must be unique")
        return value


class ScoreTemplateDefinition(BaseModel):
    """Complete score template definition."""

    st_meta: ScoreTemplateMeta
    buckets: List[ScoreBucket]
    dimensions: List[ScoreTemplateDimension]
    tips: Dict[str, List[str]] = Field(default_factory=dict)

    model_config = ConfigDict(extra="forbid")

    @model_validator(mode="after")
    def validate_template(self) -> "ScoreTemplateDefinition":
        self._validate_bucket_ranges()
        self._validate_weights()
        self._validate_tips()
        return self

    def _validate_bucket_ranges(self) -> None:
        if len(self.buckets) < 3:
            raise ValueError("at least three buckets are required")
        sorted_buckets = sorted(self.buckets, key=lambda b: (b.range.min, b.range.max))
        prev_max = 0.0
        for index, bucket in enumerate(sorted_buckets):
            start, end = bucket.range.min, bucket.range.max
            if index == 0 and start > 0:
                raise ValueError("first bucket must start at 0")
            if start < prev_max - 1e-9:
                raise ValueError("bucket ranges overlap or are unordered")
            prev_max = end
        if abs(sorted_buckets[-1].range.max - 100) > 1e-9:
            raise ValueError("last bucket must end at 100")

    def _validate_weights(self) -> None:
        total = sum(d.weight for d in self.dimensions)
        if abs(total - 1.0) > 1e-6:
            raise ValueError(f"dimension weights must sum to 1.0 (got {total:.6f})")

    def _validate_tips(self) -> None:
        dimension_codes = {dimension.code for dimension in self.dimensions}
        for key in self.tips:
            if key not in dimension_codes:
                raise ValueError(f"tips references unknown dimension '{key}'")

    def summary(self) -> "ScoreTemplateSummary":
        """Create a lightweight summary describing the template."""

        return ScoreTemplateSummary(
            key=self.st_meta.key,
            name=self.st_meta.name,
            schema_version=self.st_meta.schema_version,
            dimension_count=len(self.dimensions),
        )


class ScoreTemplateSummary(BaseModel):
    """Minimal summary information for selectors and registries."""

    key: str
    name: str
    schema_version: str
    dimension_count: int

    model_config = ConfigDict(extra="forbid")


__all__ = [
    "BucketCode",
    "DimensionBucketOverrides",
    "ScoreBucket",
    "ScoreBucketRange",
    "ScoreTemplateDefinition",
    "ScoreTemplateDimension",
    "ScoreTemplateMeta",
    "ScoreTemplatePublicPolicy",
    "ScoreTemplateScale",
    "ScoreTemplateSummary",
    "TransformCode",
]
