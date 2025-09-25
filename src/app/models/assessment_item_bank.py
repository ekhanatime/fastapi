"""Docs: ./docs/functions/assessment_item_bank_models.md | SPOT: ./SPOT.md#function-catalog"""
from __future__ import annotations

import uuid

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Column,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    Text,
    UniqueConstraint,
    text,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.sql import func

from app.core.db.database import Base


class AssessmentVersion(Base):
    """Catalog entry linking templates and blueprint releases."""

    __tablename__ = "assessment_versions"

    version_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    template_id = Column(String(128), nullable=False)
    blueprint_name = Column(String(128), nullable=False)
    blueprint_version = Column(String(64), nullable=False)
    notes = Column(Text, nullable=True)
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    __table_args__ = (
        UniqueConstraint(
            "template_id",
            "blueprint_name",
            "blueprint_version",
            name="uq_assessment_versions_template_blueprint",
        ),
        Index("idx_assessment_versions_template", "template_id"),
    )


class AssessmentItemBank(Base):
    """Persisted item metadata for adaptive selection routines."""

    __tablename__ = "assessment_item_bank"

    item_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    version_id = Column(
        UUID(as_uuid=True),
        ForeignKey("assessment_versions.version_id", ondelete="CASCADE"),
        nullable=False,
    )
    code = Column(String(128), nullable=False)
    dimension = Column(String(64), nullable=False)
    difficulty = Column(String(16), nullable=False)
    weight = Column(Numeric(8, 4), nullable=False, server_default=text("1.0"))
    critical = Column(Boolean, nullable=False, server_default=text("false"))
    anchor = Column(Boolean, nullable=False, server_default=text("false"))
    discrimination = Column(Numeric(8, 4), nullable=True)
    exposure_cap = Column(Numeric(6, 4), nullable=True)
    tags = Column(JSONB, nullable=False, server_default=text("'[]'::jsonb"))
    meta = Column(JSONB, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        CheckConstraint(
            "difficulty IN ('easy','medium','hard')",
            name="chk_assessment_item_bank_difficulty",
        ),
        UniqueConstraint("version_id", "code", name="uq_assessment_item_bank_version_code"),
        Index("idx_assessment_item_bank_dimension", "dimension"),
        Index("idx_assessment_item_bank_difficulty", "difficulty"),
        Index("idx_assessment_item_bank_anchor", "anchor"),
    )


class AssessmentItemStats(Base):
    """Aggregated usage statistics for blueprint items."""

    __tablename__ = "assessment_item_stats"

    item_id = Column(
        UUID(as_uuid=True),
        ForeignKey("assessment_item_bank.item_id", ondelete="CASCADE"),
        primary_key=True,
    )
    shown = Column(Integer, nullable=False, server_default=text("0"))
    correct = Column(Integer, nullable=False, server_default=text("0"))
    facility = Column(Numeric(6, 4), nullable=True)
    discrimination = Column(Numeric(6, 4), nullable=True)
    exposure = Column(Numeric(6, 4), nullable=True)
    last_seen_at = Column(DateTime(timezone=True), nullable=True)

    __table_args__ = (
        Index("idx_assessment_item_stats_exposure", "exposure"),
    )


class AssessmentResponseItem(Base):
    """Link table storing rendered items and participant scoring."""

    __tablename__ = "assessment_response_items"

    assessment_id = Column(
        UUID(as_uuid=True),
        ForeignKey("assessments.id", ondelete="CASCADE"),
        primary_key=True,
    )
    item_id = Column(
        UUID(as_uuid=True),
        ForeignKey("assessment_item_bank.item_id", ondelete="RESTRICT"),
        primary_key=True,
    )
    answer = Column(JSONB, nullable=True)
    score = Column(Numeric(6, 4), nullable=True)
    responded_at = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        Index("idx_assessment_response_items_item", "item_id"),
    )


__all__ = [
    "AssessmentItemBank",
    "AssessmentItemStats",
    "AssessmentResponseItem",
    "AssessmentVersion",
]
