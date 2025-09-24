# Docs: ./docs/functions/score_template_registry.md | SPOT: ./SPOT.md#function-catalog
"""API endpoints exposing bundled score template metadata."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException

from app.score_templates import get_score_template, list_score_templates
from app.score_templates.schema import ScoreTemplateDefinition, ScoreTemplateSummary

router = APIRouter(prefix="/score-templates", tags=["score-templates"])


@router.get("/", response_model=list[ScoreTemplateSummary])
def list_available_score_templates() -> list[ScoreTemplateSummary]:
    """Return summaries for all bundled score templates."""

    return list_score_templates()


@router.get("/{template_id}", response_model=ScoreTemplateDefinition)
def get_score_template_definition(template_id: str) -> ScoreTemplateDefinition:
    """Fetch the detailed definition for a specific score template."""

    definition = get_score_template(template_id)
    if not definition:
        raise HTTPException(status_code=404, detail="Score template not found")

    return definition


__all__ = ["router"]
