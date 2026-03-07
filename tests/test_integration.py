"""
Integration tests for the Portfolio API.

These tests exercise the full request/response cycle using FastAPI's TestClient,
which runs the ASGI app in-process without requiring a live server.
"""

import pytest
from fastapi.testclient import TestClient

from app.main import PROJECTS, app


@pytest.fixture(autouse=True)
def reset_projects():
    """Ensure the in-memory projects list is empty before each test."""
    PROJECTS.clear()
    yield
    PROJECTS.clear()


@pytest.fixture
def client():
    return TestClient(app)


# ---------------------------------------------------------------------------
# Health check
# ---------------------------------------------------------------------------


class TestHealthCheck:
    def test_returns_200(self, client: TestClient):
        response = client.get("/health")
        assert response.status_code == 200

    def test_returns_ok_status(self, client: TestClient):
        response = client.get("/health")
        assert response.json() == {"status": "ok"}


# ---------------------------------------------------------------------------
# Profile
# ---------------------------------------------------------------------------


class TestProfile:
    def test_returns_200(self, client: TestClient):
        response = client.get("/profile")
        assert response.status_code == 200

    def test_contains_name(self, client: TestClient):
        response = client.get("/profile")
        assert response.json()["name"] == "Umut Soysal"

    def test_contains_education(self, client: TestClient):
        response = client.get("/profile")
        data = response.json()
        assert "Carnegie Mellon University" in data["education"]

    def test_contains_bio(self, client: TestClient):
        response = client.get("/profile")
        data = response.json()
        assert "production grade applications" in data["bio"]


# ---------------------------------------------------------------------------
# Skills
# ---------------------------------------------------------------------------


class TestSkills:
    def test_returns_200(self, client: TestClient):
        response = client.get("/skills")
        assert response.status_code == 200

    def test_returns_list_of_skills(self, client: TestClient):
        response = client.get("/skills")
        data = response.json()
        assert "skills" in data
        assert isinstance(data["skills"], list)
        assert len(data["skills"]) > 0

    def test_skills_have_name_and_category(self, client: TestClient):
        response = client.get("/skills")
        for skill in response.json()["skills"]:
            assert "name" in skill
            assert "category" in skill

    def test_known_skills_present(self, client: TestClient):
        response = client.get("/skills")
        names = [s["name"] for s in response.json()["skills"]]
        for expected in ["Python", "FastAPI", "Docker", "AWS"]:
            assert expected in names

    def test_filter_by_category_language(self, client: TestClient):
        response = client.get("/skills/language")
        assert response.status_code == 200
        data = response.json()
        assert data["category"] == "language"
        assert all(s["category"] == "language" for s in data["skills"])

    def test_filter_by_category_framework(self, client: TestClient):
        response = client.get("/skills/framework")
        assert response.status_code == 200
        names = [s["name"] for s in response.json()["skills"]]
        assert "FastAPI" in names
        assert "Flutter" in names

    def test_filter_by_category_cloud(self, client: TestClient):
        response = client.get("/skills/cloud")
        assert response.status_code == 200
        names = [s["name"] for s in response.json()["skills"]]
        assert "AWS" in names

    def test_unknown_category_returns_404(self, client: TestClient):
        response = client.get("/skills/unknown_category")
        assert response.status_code == 404

    def test_unknown_category_returns_detail(self, client: TestClient):
        response = client.get("/skills/unknown_category")
        assert "detail" in response.json()


# ---------------------------------------------------------------------------
# Projects
# ---------------------------------------------------------------------------


class TestProjects:
    def test_get_projects_returns_200(self, client: TestClient):
        response = client.get("/projects")
        assert response.status_code == 200

    def test_get_projects_initially_empty(self, client: TestClient):
        response = client.get("/projects")
        assert response.json() == {"projects": []}

    def test_create_project_returns_201(self, client: TestClient):
        payload = {
            "name": "Smart Inventory",
            "description": "Inventory management system with ML-based forecasting",
            "tech_stack": ["Python", "FastAPI", "Docker"],
        }
        response = client.post("/projects", json=payload)
        assert response.status_code == 201

    def test_create_project_returns_project_data(self, client: TestClient):
        payload = {
            "name": "Smart Inventory",
            "description": "Inventory management system with ML-based forecasting",
            "tech_stack": ["Python", "FastAPI", "Docker"],
        }
        response = client.post("/projects", json=payload)
        data = response.json()
        assert data["name"] == payload["name"]
        assert data["description"] == payload["description"]
        assert data["tech_stack"] == payload["tech_stack"]

    def test_created_project_appears_in_list(self, client: TestClient):
        payload = {
            "name": "Portfolio API",
            "description": "FastAPI-based personal portfolio backend",
            "tech_stack": ["Python", "FastAPI", "AWS"],
        }
        client.post("/projects", json=payload)
        response = client.get("/projects")
        projects = response.json()["projects"]
        assert len(projects) == 1
        assert projects[0]["name"] == "Portfolio API"

    def test_multiple_projects_are_stored(self, client: TestClient):
        for i in range(3):
            client.post(
                "/projects",
                json={
                    "name": f"Project {i}",
                    "description": f"Description {i}",
                    "tech_stack": ["Python"],
                },
            )
        response = client.get("/projects")
        assert len(response.json()["projects"]) == 3

    def test_create_project_missing_name_returns_422(self, client: TestClient):
        payload = {"description": "No name project", "tech_stack": ["Python"]}
        response = client.post("/projects", json=payload)
        assert response.status_code == 422

    def test_create_project_missing_description_returns_422(self, client: TestClient):
        payload = {"name": "No desc", "tech_stack": ["Python"]}
        response = client.post("/projects", json=payload)
        assert response.status_code == 422
