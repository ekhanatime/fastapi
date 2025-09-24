# Docs: ./docs/functions/score_template_registry.md | SPOT: ./SPOT.md#function-catalog
"""Registry utilities for bundled score templates."""

from __future__ import annotations

import json
from collections.abc import Mapping
from functools import lru_cache
from importlib import resources
from types import MappingProxyType
from typing import Dict

from .schema import ScoreTemplateDefinition, ScoreTemplateSummary
from .validation import validate_template

_TEMPLATE_FILES: Mapping[str, str] = MappingProxyType(
    {
        "performance_health_v1": "performance_health_v1.json",
    }
)


@lru_cache(maxsize=1)
def _load_registry() -> Mapping[str, ScoreTemplateDefinition]:
    """Load and validate all bundled score template definitions."""

    registry: Dict[str, ScoreTemplateDefinition] = {}
    base_path = resources.files("app.score_templates.definitions")
    for template_id, filename in _TEMPLATE_FILES.items():
        raw = base_path.joinpath(filename).read_text(encoding="utf-8")
        definition = validate_template(json.loads(raw))
        registry[template_id] = definition
    return MappingProxyType(registry)


def list_score_templates() -> list[ScoreTemplateSummary]:
    """List summaries for every available score template."""

    return [definition.summary() for definition in _load_registry().values()]


def get_score_template(template_id: str) -> ScoreTemplateDefinition | None:
    """Retrieve a score template definition by identifier."""

    return _load_registry().get(template_id)


__all__ = ["get_score_template", "list_score_templates"]
