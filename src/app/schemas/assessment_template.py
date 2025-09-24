"""Pydantic models for complete assessment template definitions."""
from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class AssessmentLinkage(BaseModel):
    course_id: str = Field(..., description="Platform-wide course identifier")
    module_id: str = Field(..., description="Module identifier within the course")
    assessment_set_id: str = Field(..., description="Identifier of the assessment set the template belongs to")


class AssessmentRegulatoryReference(BaseModel):
    framework: str
    article: str | None = None
    topic: str | None = None


class AssessmentMeta(BaseModel):
    title: str
    description: str
    estimated_minutes: str
    language: str
    visibility: str
    tags: list[str]
    category: str
    difficulty: str
    audience: str
    learning_objectives: list[str]
    regulatory_refs: list[AssessmentRegulatoryReference]


class AssessmentGateRules(BaseModel):
    require_video_completion_percent: int
    require_acknowledgement: bool


class AssessmentSettings(BaseModel):
    lead_magnet: bool
    collect_fields: list[str]
    shuffle_questions: bool
    shuffle_options: bool
    time_limit_minutes: int | None
    allow_backtracking: bool
    show_explanations: str
    max_attempts_per_user: int
    retake_cooldown_hours: int
    pass_threshold_percentage: int
    gate_rules: AssessmentGateRules


class AssessmentAccessibility(BaseModel):
    wcag_level: str
    caption_required: bool
    reading_grade_level: str


class AssessmentLocalization(BaseModel):
    default_locale: str
    available_locales: list[str]


class AssessmentUX(BaseModel):
    theme: str
    progress_bar: bool
    question_numbering: str
    accessibility: AssessmentAccessibility
    localization: AssessmentLocalization


class AssessmentAntiCheat(BaseModel):
    tab_switch_limit: int
    copy_paste_allowed: bool
    suspicious_ip_threshold: int
    allow_list_domains: list[str]


class AssessmentProctoring(BaseModel):
    enabled: bool
    photo_check: bool


class AssessmentDataProtection(BaseModel):
    store_personal_fields_hashed: bool
    retain_personal_days: int


class AssessmentSecurity(BaseModel):
    anti_cheat: AssessmentAntiCheat
    proctoring: AssessmentProctoring
    data_protection: AssessmentDataProtection


class AssessmentWebhooks(BaseModel):
    on_pass: str | None
    on_fail: str | None
    on_completion: str | None


class AssessmentLMS(BaseModel):
    scorm: bool
    xapi: bool


class AssessmentPayments(BaseModel):
    enabled: bool
    currency: str
    price_amount: int | float
    sku: str
    is_free: bool


class AssessmentIntegrations(BaseModel):
    webhooks: AssessmentWebhooks
    lms: AssessmentLMS
    payments: AssessmentPayments


class AssessmentCategoryDefinition(BaseModel):
    title: str
    description: str
    icon: str


class AssessmentSection(BaseModel):
    key: str
    title: str
    description: str
    order: int
    gating: str | None


class AssessmentAssets(BaseModel):
    images: list[str]
    attachments: list[str]
    references: list[str]


class AssessmentQuestionOption(BaseModel):
    label: str
    value: str
    correct: bool


class AssessmentQuestionStats(BaseModel):
    views: int
    attempts: int
    correct_rate: float | None
    avg_time_sec: float | None
    discrimination_pb: float | None
    top_distractors: list[str]


class AssessmentQuestion(BaseModel):
    id: int
    section: str
    category: str
    text: str
    type: str
    weight: int | float
    time_limit_sec: int | None
    difficulty_tag: str
    cognitive_level: str
    options: list[AssessmentQuestionOption]
    feedback: str
    hints: list[str]
    tags: list[str]
    stats: AssessmentQuestionStats


class AssessmentScoringSingle(BaseModel):
    correct: str
    incorrect: int | float


class AssessmentScoringMultiple(BaseModel):
    method: str
    credit: str
    penalty: str
    clamp: list[int | float | str]


class AssessmentScoringTrueFalse(BaseModel):
    correct: str
    incorrect: int | float


class AssessmentScoringShortAnswer(BaseModel):
    method: str
    min_keywords_for_full: int
    case_sensitive: bool


class AssessmentScoringNormalization(BaseModel):
    max_score: int | float | None
    scale_to_percentage: bool


class AssessmentScoring(BaseModel):
    single: AssessmentScoringSingle
    multiple: AssessmentScoringMultiple
    true_false: AssessmentScoringTrueFalse
    short_answer: AssessmentScoringShortAnswer
    normalization: AssessmentScoringNormalization


class AssessmentResultBucket(BaseModel):
    min_percentage: int
    label: str
    description: str


class AssessmentAnalyticsSpec(BaseModel):
    events: list[str]
    dimensions: list[str]
    metrics: list[str]


class AssessmentKpiTargets(BaseModel):
    completion_rate_pct: int
    pass_rate_pct: int
    avg_score_pct: int
    median_time_min: int
    abandonment_rate_pct: int
    avg_attempts_to_pass: float
    category_min_accuracy_pct: dict[str, int]


class AssessmentTimeWindow(BaseModel):
    from_: datetime | None = Field(default=None, alias="from")
    to: datetime | None = None

    model_config = ConfigDict(populate_by_name=True)


class AssessmentOverallKpi(BaseModel):
    starts: int
    completions: int
    completion_rate_pct: float | None
    passes: int
    pass_rate_pct: float | None
    avg_score_pct: float | None
    median_time_min: float | None
    avg_attempts_to_pass: float | None
    abandonment_rate_pct: float | None
    bounce_time_sec: float | None
    reliability_kr20: float | None


class AssessmentCategoryKpi(BaseModel):
    accuracy_pct: float | None
    avg_time_sec: float | None
    attempts: int


class AssessmentSectionKpi(BaseModel):
    dropoff_pct: float | None
    avg_time_sec: float | None


class AssessmentErrorPattern(BaseModel):
    question_id: int | None
    common_wrong_option_value: str | None
    rate_pct: float | None


class AssessmentDeviceLocaleSplits(BaseModel):
    by_device: dict[str, int]
    by_locale: dict[str, int]


class AssessmentComputedKpis(BaseModel):
    time_window: AssessmentTimeWindow
    overall: AssessmentOverallKpi
    by_category: dict[str, AssessmentCategoryKpi]
    by_section: dict[str, AssessmentSectionKpi]
    top_error_patterns: list[AssessmentErrorPattern]
    device_locale_splits: AssessmentDeviceLocaleSplits


class AssessmentAuditChange(BaseModel):
    version: str
    date: datetime
    notes: str


class AssessmentAudit(BaseModel):
    created_by: str
    created_at: datetime
    updated_at: datetime
    changelog: list[AssessmentAuditChange]


class AssessmentDefinition(BaseModel):
    id: str
    version: str
    org_id: str
    linkage: AssessmentLinkage
    meta: AssessmentMeta
    settings: AssessmentSettings
    ux: AssessmentUX
    security: AssessmentSecurity
    integrations: AssessmentIntegrations
    categories: dict[str, AssessmentCategoryDefinition]
    sections: list[AssessmentSection]
    assets: AssessmentAssets
    questions: list[AssessmentQuestion]
    scoring: AssessmentScoring
    result_buckets: list[AssessmentResultBucket]
    analytics_spec: AssessmentAnalyticsSpec
    kpi_targets: AssessmentKpiTargets
    computed_kpis: AssessmentComputedKpis
    audit: AssessmentAudit


class AssessmentTemplateSummary(BaseModel):
    """Concise view that can be used to populate template selectors."""

    id: str
    version: str
    title: str
    category: str
    difficulty: str
    estimated_minutes: str
    tags: list[str]

    @classmethod
    def from_definition(cls, definition: AssessmentDefinition) -> AssessmentTemplateSummary:
        meta = definition.meta
        return cls(
            id=definition.id,
            version=definition.version,
            title=meta.title,
            category=meta.category,
            difficulty=meta.difficulty,
            estimated_minutes=meta.estimated_minutes,
            tags=meta.tags,
        )


__all__ = [
    "AssessmentDefinition",
    "AssessmentTemplateSummary",
]
