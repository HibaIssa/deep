from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_generate_report_for_txt_resume():
    response = client.post(
        "/api/report/generate",
        data={"selected_role": "Backend Developer"},
        files={
            "file": (
                "resume.txt",
                b"Python FastAPI SQL Docker testing REST API developer.",
                "text/plain",
            )
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["selected_role"] == "Backend Developer"
    assert payload["gap_analysis"]["coverage_percent"] > 0
    assert payload["recommendations"]


def test_register_login_and_save_report():
    username = "testuser_api"
    password = "secret123"
    register_response = client.post("/api/auth/register", json={"username": username, "password": password})
    assert register_response.status_code in {200, 409}

    login_response = client.post("/api/auth/login", json={"username": username, "password": password})
    assert login_response.status_code == 200
    token = login_response.json()["token"]

    report_response = client.post(
        "/api/report/generate",
        data={"selected_role": "Data Analyst"},
        files={"file": ("resume.txt", b"SQL Excel Tableau statistics dashboard analyst.", "text/plain")},
    )
    report = report_response.json()

    save_response = client.post(
        "/api/report/saved",
        headers={"Authorization": f"Bearer {token}"},
        json={"title": "Data analyst report", "report": report},
    )
    assert save_response.status_code == 200

    list_response = client.get("/api/report/saved", headers={"Authorization": f"Bearer {token}"})
    assert list_response.status_code == 200
    assert len(list_response.json()) >= 1
