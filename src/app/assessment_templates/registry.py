"""Registry utilities for bundled assessment templates."""
from __future__ import annotations

from collections.abc import Mapping
from functools import lru_cache
from importlib import resources
from types import MappingProxyType

from app.schemas.assessment_template import (
    AssessmentDefinition,
    AssessmentTemplateSummary,
)

_TEMPLATE_FILES = MappingProxyType(
    {
        "course_gdpr_social_email_cookies_v1_no": "course_gdpr_social_email_cookies_v1_no.json",
    }
)


@lru_cache(maxsize=1)
def _load_registry() -> Mapping[str, AssessmentDefinition]:
    """Load and validate all bundled template definitions."""

    registry: dict[str, AssessmentDefinition] = {}
    base_path = resources.files("app.assessment_templates.definitions")
    for template_id, filename in _TEMPLATE_FILES.items():
        data = base_path.joinpath(filename).read_text(encoding="utf-8")
        registry[template_id] = AssessmentDefinition.model_validate_json(data)
    return MappingProxyType(registry)


def list_assessment_templates() -> list[AssessmentTemplateSummary]:
    """Return summaries for all registered templates."""

    return [
        AssessmentTemplateSummary.from_definition(definition)
        for definition in _load_registry().values()
    ]


def get_assessment_template(template_id: str) -> AssessmentDefinition | None:
    """Retrieve a template definition by identifier, if present."""

    return _load_registry().get(template_id)


__all__ = [
    "get_assessment_template",
    "list_assessment_templates",
]
