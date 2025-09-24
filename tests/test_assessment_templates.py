from fastapi.testclient import TestClient

from app.assessment_templates import (
    get_assessment_template,
    list_assessment_templates,
)

TEMPLATE_ID = "course_gdpr_social_email_cookies_v1_no"


def test_list_assessment_templates(client: TestClient) -> None:
    response = client.get("/api/v1/assessment/schema")
    assert response.status_code == 200

    payload = response.json()
    assert isinstance(payload, list)
    assert any(item["id"] == TEMPLATE_ID for item in payload)


def test_get_assessment_template_detail(client: TestClient) -> None:
    response = client.get(f"/api/v1/assessment/schema/{TEMPLATE_ID}")
    assert response.status_code == 200

    payload = response.json()
    assert payload["id"] == TEMPLATE_ID
    assert payload["meta"]["title"].startswith("Kurs: GDPR")
    assert payload["computed_kpis"]["time_window"]["from"] is None


def test_get_assessment_template_not_found(client: TestClient) -> None:
    response = client.get("/api/v1/assessment/schema/unknown")
    assert response.status_code == 404
    assert response.json()["detail"] == "Assessment template not found"


def test_registry_exposes_bundled_template() -> None:
    summaries = list_assessment_templates()
    assert any(summary.id == TEMPLATE_ID for summary in summaries)

    definition = get_assessment_template(TEMPLATE_ID)
    assert definition is not None
    assert definition.meta.category == "GDPR & Sikkerhet"
