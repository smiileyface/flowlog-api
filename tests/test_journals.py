"""
Tests for Journal CRUD operations and relationships.
"""


class TestJournalCRUD:
    """Test basic CRUD operations for journals."""

    def test_create_journal(self, client, sample_project):
        """Test creating a new journal."""
        response = client.post(
            "/api/v1/journals/",
            json={"date": "2024-01-15", "project_id": sample_project["id"]},
        )
        assert response.status_code == 201
        data = response.json()
        assert data["success"] is True
        assert data["data"]["date"] == "2024-01-15"
        assert data["data"]["project_id"] == sample_project["id"]
        assert "id" in data["data"]

    def test_create_journal_without_project(self, client):
        """Test creating a journal without a project."""
        response = client.post(
            "/api/v1/journals/",
            json={"date": "2024-01-15"},
        )
        assert response.status_code == 201
        data = response.json()
        assert data["data"]["project_id"] is None

    def test_create_journal_invalid_project(self, client):
        """Test creating a journal with non-existent project fails."""
        fake_id = "00000000-0000-0000-0000-000000000000"
        response = client.post(
            "/api/v1/journals/",
            json={"date": "2024-01-15", "project_id": fake_id},
        )
        assert response.status_code == 404
        assert "Project" in response.json()["message"]

    def test_list_journals(self, client, sample_journal):
        """Test listing journals with pagination."""
        response = client.get("/api/v1/journals/")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert len(data["data"]) >= 1
        assert data["pagination"]["total"] >= 1

    def test_list_journals_filter_by_project(
        self, client, sample_project, sample_journal
    ):
        """Test filtering journals by project_id."""
        response = client.get(f"/api/v1/journals/?project_id={sample_project['id']}")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert len(data["data"]) >= 1
        # Verify all journals belong to the project
        for journal in data["data"]:
            assert journal["project_id"] == sample_project["id"]

    def test_get_journal(self, client, sample_journal):
        """Test getting a specific journal by ID."""
        response = client.get(f"/api/v1/journals/{sample_journal['id']}")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["id"] == sample_journal["id"]

    def test_get_journal_not_found(self, client):
        """Test getting a non-existent journal returns 404."""
        fake_id = "00000000-0000-0000-0000-000000000000"
        response = client.get(f"/api/v1/journals/{fake_id}")
        assert response.status_code == 404

    def test_update_journal(self, client, sample_journal, sample_project):
        """Test updating a journal."""
        response = client.put(
            f"/api/v1/journals/{sample_journal['id']}",
            json={
                "date": "2024-02-01",
                "processed_markdown": "# Test",
                "notes_snapshot": {"count": 5},
                "project_id": sample_project["id"],
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["date"] == "2024-02-01"
        assert data["data"]["processed_markdown"] == "# Test"

    def test_update_journal_invalid_project(self, client, sample_journal):
        """Test updating journal with invalid project fails."""
        fake_id = "00000000-0000-0000-0000-000000000000"
        response = client.put(
            f"/api/v1/journals/{sample_journal['id']}",
            json={"date": "2024-02-01", "project_id": fake_id},
        )
        assert response.status_code == 404

    def test_delete_journal(self, client, sample_journal):
        """Test deleting a journal."""
        response = client.delete(f"/api/v1/journals/{sample_journal['id']}")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "deleted successfully" in data["message"]


class TestJournalRelationships:
    """Test journal relationships with notes and AI jobs."""

    def test_get_journal_notes(self, client, sample_journal, sample_note):
        """Test getting all notes for a journal."""
        response = client.get(f"/api/v1/journals/{sample_journal['id']}/notes")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["count"] >= 1
        assert len(data["data"]) >= 1
        note_ids = [n["id"] for n in data["data"]]
        assert sample_note["id"] in note_ids

    def test_get_journal_notes_empty(self, client, sample_journal):
        """Test getting notes for a journal with no notes."""
        response = client.get(f"/api/v1/journals/{sample_journal['id']}/notes")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["count"] == 0

    def test_get_journal_ai_jobs(self, client, sample_journal, sample_ai_job):
        """Test getting all AI jobs for a journal."""
        response = client.get(f"/api/v1/journals/{sample_journal['id']}/ai-jobs")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["count"] >= 1
        job_ids = [j["id"] for j in data["data"]]
        assert sample_ai_job["id"] in job_ids

    def test_get_journal_ai_jobs_empty(self, client, sample_journal):
        """Test getting AI jobs for a journal with no jobs."""
        response = client.get(f"/api/v1/journals/{sample_journal['id']}/ai-jobs")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["count"] == 0

    def test_delete_journal_with_relations(
        self, client, sample_journal, sample_note, sample_ai_job
    ):
        """Test deleting a journal shows affected relations."""
        response = client.delete(f"/api/v1/journals/{sample_journal['id']}")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        # Message should mention orphaned notes or affected AI jobs
        message = data["message"].lower()
        assert "note" in message or "job" in message
