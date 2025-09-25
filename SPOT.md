# SPOT – Security Assessment Platform

**en:** Central hub for backend modules, schemas, and operational checklists that drive the assessment service.

**nb-NO:** Sentral oversikt for backend-moduler, skjemaer og sjekklister som driver vurderingstjenesten.

## Integration Plan – Score Template Expansion
- [x] Align assessment template documentation with SPOT layout (migrate `docs/SPOT_Assessments.md`).
- [x] Implement reusable score template schema validation + registry utilities.
- [x] Expose score template summaries and definitions through FastAPI endpoints and automated tests.
- [x] Update documentation set (function docs, tasklist, ERD, localization) and changelog for the new score template feature.

## Integration Plan – Adaptive Blueprint Selection
- [x] Add blueprint schema resources with anchors, quotas, and scoring metadata.
- [x] Implement stratified selector + scoring engine with exposure handling tests.
- [x] Publish blueprint preview API endpoints and automated coverage.
- [x] Refresh documentation (function doc, SPOT, ERD, localization) and changelog entries.

## Integration Plan – Assessment Item Bank Tracking
- [x] Model persistent assessment versions, item bank entries, response linkage, and exposure statistics.
- [x] Seed Postgres schema for the new tables with constraints and indexes.
- [x] Extend blueprint engine utilities to hydrate pools from item bank records and stats.
- [x] Update documentation set (function doc, SPOT, ERD, changelog, localization, tasklist).

## Function Catalog

### Backend (Python/FastAPI)
- <i class="fas fa-clipboard-check"></i> **Assessment Template Registry** — Bundled template loader & API. _(Function doc pending migration; tracked in integration plan.)_
- <i class="fas fa-layer-group"></i> **Assessment Blueprint Engine** — Stratified item blueprint loader, selector, scoring, and preview API. → `./docs/functions/assessment_blueprint_engine.md`
- <i class="fas fa-chart-gauge"></i> **Score Template Registry** — Schema-validated score template loader with FastAPI exposure. → `./docs/functions/score_template_registry.md`
- <i class="fas fa-network-wired"></i> **API Router v1** — Aggregates versioned public/admin routers. → `./docs/functions/api_router_v1.md`
- <i class="fas fa-cogs"></i> **Core Setup & Lifespan** — FastAPI factory & Redis pool orchestration with test bypass flag. → `./docs/functions/core_setup.md`

#### Bundled Assessment Templates
| ID | Version | Title | Notes |
| --- | --- | --- | --- |
| `course_gdpr_social_email_cookies_v1_no` | 1.1.0 | GDPR, sosial manipulering, e-post og cookies | JSON definition validated at load time |

- Schema models: `src/app/schemas/assessment_template.py`
- Template resources: `src/app/assessment_templates/definitions/*.json`
- Registry module: `src/app/assessment_templates/registry.py`
- API access: `GET /api/v1/assessment/schema`, `GET /api/v1/assessment/schema/{template_id}`

### Frontend (HTML/JS)
- Existing Vuexy-based assets (see `docs/index.md`) pending catalog alignment.

### Database (PostgreSQL)
- <i class="fas fa-database"></i> **Assessment Item Bank Models** — Persistent item bank, response items, and exposure stats backing adaptive selection. → `./docs/functions/assessment_item_bank_models.md`
- Core assessment schema coverage documented in `docs/Database/database_info.md`.

### Infra/Provisioning
- Docker compose stack with Supabase-compatible Postgres (`docker-compose.yml`).

## Documentation Index (Referenced to avoid orphans)
- `README.md`, `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`, `LICENSE.md`
- Getting Started Guides → `docs/getting-started/*.md`
- API Documentation → `docs/API_Documentation.md`
- Authentication Flow → `docs/AUTHENTICATION_FLOW.md`
- Assessment System Guide → `docs/Assessment_System_Guide.md`
- User Flow Overview → `docs/USER_FLOW_COMPLETE.md`
- Database Reference → `docs/Database/database_info.md`
- Comprehensive User Guide Sections → `docs/user-guide/**`

## Task Tracking
- Dynamic tasklist lives at `./docs/tasks/tasklist.md`.

