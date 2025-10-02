"""
Tests for Project CRUD operations and relationships.
"""

import pytest


class TestProjectCRUD:
    """Test basic CRUD operations for projects."""

    def test_create_project(self, client):
        """Test creating a new project."""
        response = client.post(
            "/api/v1/projects/",
            json={"name": "My Project", "description": "A test project"},
        )
        assert response.status_code == 201
        data = response.json()
        assert data["success"] is True
        assert data["data"]["name"] == "My Project"
        assert data["data"]["description"] == "A test project"
        assert "id" in data["data"]
        assert "created_at" in data["data"]

    def test_create_project_duplicate_name(self, client, sample_project):
        """Test creating a project with duplicate name fails."""
        response = client.post(
            "/api/v1/projects/",
            json={"name": sample_project["name"], "description": "Another project"},
        )
        assert response.status_code == 409
        assert "already exists" in response.json()["message"]

    def test_list_projects(self, client, sample_project):
        """Test listing projects with pagination."""
        response = client.get("/api/v1/projects/")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert len(data["data"]) >= 1
        assert data["pagination"]["total"] >= 1

    def test_get_project(self, client, sample_project):
        """Test getting a specific project by ID."""
        response = client.get(f"/api/v1/projects/{sample_project['id']}")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["id"] == sample_project["id"]
        assert data["data"]["name"] == sample_project["name"]

    def test_get_project_not_found(self, client):
        """Test getting a non-existent project returns 404."""
        fake_id = "00000000-0000-0000-0000-000000000000"
        response = client.get(f"/api/v1/projects/{fake_id}")
        assert response.status_code == 404

    def test_update_project(self, client, sample_project):
        """Test updating a project."""
        response = client.put(
            f"/api/v1/projects/{sample_project['id']}",
            json={"name": "Updated Project", "description": "Updated description"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["name"] == "Updated Project"
        assert data["data"]["description"] == "Updated description"

    def test_update_project_duplicate_name(self, client, sample_project):
        """Test updating a project to a duplicate name fails."""
        # Create another project
        response = client.post(
            "/api/v1/projects/",
            json={"name": "Another Project", "description": "Test"},
        )
        another_project = response.json()["data"]

        # Try to update second project to first project's name
        response = client.put(
            f"/api/v1/projects/{another_project['id']}",
            json={"name": sample_project["name"], "description": "Test"},
        )
        assert response.status_code == 409

    def test_delete_project(self, client, sample_project):
        """Test deleting a project."""
        response = client.delete(f"/api/v1/projects/{sample_project['id']}")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "deleted successfully" in data["message"]

        # Verify project is deleted
        response = client.get(f"/api/v1/projects/{sample_project['id']}")
        assert response.status_code == 404


class TestProjectRelationships:
    """Test project relationships with journals."""

    def test_get_project_journals(self, client, sample_project, sample_journal):
        """Test getting all journals for a project."""
        response = client.get(f"/api/v1/projects/{sample_project['id']}/journals")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["count"] >= 1
        assert len(data["data"]) >= 1
        # Verify the journal belongs to the project
        journal_ids = [j["id"] for j in data["data"]]
        assert sample_journal["id"] in journal_ids

    def test_get_project_journals_empty(self, client, sample_project):
        """Test getting journals for a project with no journals."""
        response = client.get(f"/api/v1/projects/{sample_project['id']}/journals")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["count"] == 0
        assert len(data["data"]) == 0

    def test_delete_project_cascade(self, client, sample_project, sample_journal):
        """Test that deleting a project cascades to journals."""
        # Delete the project
        response = client.delete(f"/api/v1/projects/{sample_project['id']}")
        assert response.status_code == 200
        data = response.json()
        assert "cascade deleted" in data["message"]
        assert "journal" in data["message"]

        # Verify journal is also deleted (cascade)
        response = client.get(f"/api/v1/journals/{sample_journal['id']}")
        assert response.status_code == 404
