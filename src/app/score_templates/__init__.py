# Docs: ./docs/functions/score_template_registry.md | SPOT: ./SPOT.md#function-catalog
"""Public interface for bundled score template registry utilities."""

from .registry import get_score_template, list_score_templates

__all__ = ["get_score_template", "list_score_templates"]
