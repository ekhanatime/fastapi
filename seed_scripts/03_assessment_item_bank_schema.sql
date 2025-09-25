-- Docs: ./docs/functions/assessment_item_bank_models.md
-- SPOT: ./SPOT.md#function-catalog

-- Ensure UUID generation helpers are available
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- Catalog of assessment versions and blueprint releases
CREATE TABLE IF NOT EXISTS assessment_versions (
    version_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    template_id text NOT NULL,
    blueprint_name text NOT NULL,
    blueprint_version text NOT NULL,
    notes text,
    is_active boolean NOT NULL DEFAULT true,
    created_at timestamptz NOT NULL DEFAULT now(),
    updated_at timestamptz,
    CONSTRAINT uq_assessment_versions_template_blueprint
        UNIQUE (template_id, blueprint_name, blueprint_version)
);

CREATE INDEX IF NOT EXISTS idx_assessment_versions_template
    ON assessment_versions (template_id);

-- Item bank entries governed by blueprint quotas
CREATE TABLE IF NOT EXISTS assessment_item_bank (
    item_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    version_id uuid NOT NULL REFERENCES assessment_versions(version_id) ON DELETE CASCADE,
    code text NOT NULL,
    dimension text NOT NULL,
    difficulty text NOT NULL CHECK (difficulty IN ('easy','medium','hard')),
    weight numeric NOT NULL DEFAULT 1.0,
    critical boolean NOT NULL DEFAULT false,
    anchor boolean NOT NULL DEFAULT false,
    discrimination numeric,
    exposure_cap numeric,
    tags jsonb NOT NULL DEFAULT '[]'::jsonb,
    meta jsonb,
    created_at timestamptz NOT NULL DEFAULT now(),
    CONSTRAINT uq_assessment_item_bank_version_code UNIQUE (version_id, code)
);

CREATE INDEX IF NOT EXISTS idx_assessment_item_bank_dimension
    ON assessment_item_bank (dimension);
CREATE INDEX IF NOT EXISTS idx_assessment_item_bank_difficulty
    ON assessment_item_bank (difficulty);
CREATE INDEX IF NOT EXISTS idx_assessment_item_bank_anchor
    ON assessment_item_bank (anchor);

-- Exposure and performance statistics per item
CREATE TABLE IF NOT EXISTS assessment_item_stats (
    item_id uuid PRIMARY KEY REFERENCES assessment_item_bank(item_id) ON DELETE CASCADE,
    shown integer NOT NULL DEFAULT 0,
    correct integer NOT NULL DEFAULT 0,
    facility numeric,
    discrimination numeric,
    exposure numeric,
    last_seen_at timestamptz
);

CREATE INDEX IF NOT EXISTS idx_assessment_item_stats_exposure
    ON assessment_item_stats (exposure);

-- Captured responses to individual blueprint-driven items
CREATE TABLE IF NOT EXISTS assessment_response_items (
    assessment_id uuid NOT NULL REFERENCES assessments(id) ON DELETE CASCADE,
    item_id uuid NOT NULL REFERENCES assessment_item_bank(item_id) ON DELETE RESTRICT,
    answer jsonb,
    score numeric,
    responded_at timestamptz NOT NULL DEFAULT now(),
    PRIMARY KEY (assessment_id, item_id)
);

CREATE INDEX IF NOT EXISTS idx_assessment_response_items_item
    ON assessment_response_items (item_id);
