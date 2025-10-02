"""
Tests for AI Job CRUD operations.
"""


class TestAIJobCRUD:
    """Test basic CRUD operations for AI jobs."""

    def test_create_ai_job(self, client, sample_journal):
        """Test creating a new AI job."""
        response = client.post(
            "/api/v1/ai-jobs/",
            json={
                "journal_id": sample_journal["id"],
                "model_name": "gpt-4",
                "model_version": "turbo",
                "prompt": "Analyze this journal entry",
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert data["success"] is True
        assert data["data"]["journal_id"] == sample_journal["id"]
        assert data["data"]["model_name"] == "gpt-4"
        assert data["data"]["model_version"] == "turbo"
        assert data["data"]["prompt"] == "Analyze this journal entry"
        assert data["data"]["status"] == "queued"
        assert "id" in data["data"]

    def test_create_ai_job_invalid_journal(self, client):
        """Test creating AI job with non-existent journal fails."""
        fake_id = "00000000-0000-0000-0000-000000000000"
        response = client.post(
            "/api/v1/ai-jobs/",
            json={
                "journal_id": fake_id,
                "model_name": "gpt-4",
                "prompt": "Test",
            },
        )
        assert response.status_code == 404
        assert "Journal" in response.json()["message"]

    def test_list_ai_jobs(self, client, sample_ai_job):
        """Test listing AI jobs with pagination."""
        response = client.get("/api/v1/ai-jobs/")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert len(data["data"]) >= 1
        assert data["pagination"]["total"] >= 1

    def test_list_ai_jobs_filter_by_status(self, client, sample_ai_job):
        """Test filtering AI jobs by status."""
        response = client.get("/api/v1/ai-jobs/?status=queued")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        # All returned jobs should have queued status
        for job in data["data"]:
            assert job["status"] == "queued"

    def test_list_ai_jobs_filter_by_journal(
        self, client, sample_journal, sample_ai_job
    ):
        """Test filtering AI jobs by journal_id."""
        response = client.get(f"/api/v1/ai-jobs/?journal_id={sample_journal['id']}")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert len(data["data"]) >= 1
        for job in data["data"]:
            assert job["journal_id"] == sample_journal["id"]

    def test_get_ai_job(self, client, sample_ai_job):
        """Test getting a specific AI job by ID."""
        response = client.get(f"/api/v1/ai-jobs/{sample_ai_job['id']}")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["id"] == sample_ai_job["id"]

    def test_get_ai_job_not_found(self, client):
        """Test getting a non-existent AI job returns 404."""
        fake_id = "00000000-0000-0000-0000-000000000000"
        response = client.get(f"/api/v1/ai-jobs/{fake_id}")
        assert response.status_code == 404

    def test_update_ai_job_status(self, client, sample_ai_job):
        """Test updating AI job status."""
        response = client.put(
            f"/api/v1/ai-jobs/{sample_ai_job['id']}",
            json={"status": "processing"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["status"] == "processing"

    def test_update_ai_job_with_response(self, client, sample_ai_job):
        """Test updating AI job with response data."""
        response = client.put(
            f"/api/v1/ai-jobs/{sample_ai_job['id']}",
            json={
                "status": "success",
                "response": {"summary": "Test summary", "sentiment": "positive"},
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["status"] == "success"
        assert data["data"]["response"]["summary"] == "Test summary"

    def test_update_ai_job_with_error(self, client, sample_ai_job):
        """Test updating AI job with error."""
        response = client.put(
            f"/api/v1/ai-jobs/{sample_ai_job['id']}",
            json={
                "status": "error",
                "error_message": "API rate limit exceeded",
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["status"] == "error"
        assert data["data"]["error_message"] == "API rate limit exceeded"

    def test_delete_ai_job(self, client, sample_ai_job):
        """Test deleting an AI job."""
        response = client.delete(f"/api/v1/ai-jobs/{sample_ai_job['id']}")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "deleted successfully" in data["message"]

        # Verify AI job is deleted
        response = client.get(f"/api/v1/ai-jobs/{sample_ai_job['id']}")
        assert response.status_code == 404


class TestAIJobWorkflow:
    """Test realistic AI job workflow scenarios."""

    def test_ai_job_lifecycle(self, client, sample_journal):
        """Test complete AI job lifecycle from creation to completion."""
        # 1. Create AI job
        response = client.post(
            "/api/v1/ai-jobs/",
            json={
                "journal_id": sample_journal["id"],
                "model_name": "gpt-4",
                "prompt": "Summarize",
            },
        )
        assert response.status_code == 201
        job = response.json()["data"]
        assert job["status"] == "queued"

        # 2. Update to processing
        response = client.put(
            f"/api/v1/ai-jobs/{job['id']}",
            json={"status": "processing"},
        )
        assert response.status_code == 200
        assert response.json()["data"]["status"] == "processing"

        # 3. Complete with success
        response = client.put(
            f"/api/v1/ai-jobs/{job['id']}",
            json={
                "status": "success",
                "response": {"result": "Completed successfully"},
            },
        )
        assert response.status_code == 200
        data = response.json()["data"]
        assert data["status"] == "success"
        assert data["response"]["result"] == "Completed successfully"

    def test_multiple_jobs_for_journal(self, client, sample_journal):
        """Test creating multiple AI jobs for the same journal."""
        # Create multiple jobs
        for i in range(3):
            response = client.post(
                "/api/v1/ai-jobs/",
                json={
                    "journal_id": sample_journal["id"],
                    "model_name": f"model-{i}",
                    "prompt": f"Task {i}",
                },
            )
            assert response.status_code == 201

        # Get all jobs for the journal
        response = client.get(f"/api/v1/journals/{sample_journal['id']}/ai-jobs")
        assert response.status_code == 200
        data = response.json()
        assert data["count"] >= 3
