# SPOT: Assessment Templates & Schema Registry

This Single Point Of Truth (SPOT) keeps the canonical reference for assessment templates that ship with the platform.

## Current Templates

| ID | Version | Title | Notes |
| --- | --- | --- | --- |
| `course_gdpr_social_email_cookies_v1_no` | 1.1.0 | GDPR, sosial manipulering, e-post og cookies | Bundled JSON definition validated at load time |

- **Schema models**: `src/app/schemas/assessment_template.py`
- **Template resources**: `src/app/assessment_templates/definitions/*.json`
- **Registry module**: `src/app/assessment_templates/registry.py`
- **API access**:
  - `GET /api/v1/assessment/schema` — list available templates
  - `GET /api/v1/assessment/schema/{template_id}` — fetch complete definition

## Implementation Notes

- Template definitions are validated using `AssessmentDefinition` to guarantee contract stability.
- Responses serialize using field aliases (e.g. `time_window.from`) to stay JSON schema compliant.
- Add new templates by dropping a JSON file into `src/app/assessment_templates/definitions/` and referencing it from `_TEMPLATE_FILES` in `registry.py`; update this SPOT table in tandem.

## Deployment & Infrastructure

- The development stack now runs against a Supabase Postgres container (`supabase-db`).
- `.env` configuration continues to drive connection settings—only the host name changed.
- Docker Compose applies seed scripts automatically, so bundled templates remain available after container rebuilds.

Keep this file synchronized whenever templates or infrastructure touch points evolve.
