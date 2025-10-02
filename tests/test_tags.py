"""
Tests for Tag CRUD operations and note relationships.
"""


class TestTagCRUD:
    """Test basic CRUD operations for tags."""

    def test_create_tag(self, client):
        """Test creating a new tag."""
        response = client.post(
            "/api/v1/tags/",
            json={"name": "important"},
        )
        assert response.status_code == 201
        data = response.json()
        assert data["success"] is True
        assert data["data"]["name"] == "important"
        assert "id" in data["data"]
        assert "created_at" in data["data"]

    def test_create_tag_duplicate_name(self, client, sample_tag):
        """Test creating a tag with duplicate name fails."""
        response = client.post(
            "/api/v1/tags/",
            json={"name": sample_tag["name"]},
        )
        assert response.status_code == 409
        assert "already exists" in response.json()["message"]

    def test_list_tags(self, client, sample_tag):
        """Test listing tags with pagination."""
        response = client.get("/api/v1/tags/")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert len(data["data"]) >= 1
        assert data["pagination"]["total"] >= 1

    def test_get_tag(self, client, sample_tag):
        """Test getting a specific tag by ID."""
        response = client.get(f"/api/v1/tags/{sample_tag['id']}")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["id"] == sample_tag["id"]
        assert data["data"]["name"] == sample_tag["name"]

    def test_get_tag_not_found(self, client):
        """Test getting a non-existent tag returns 404."""
        fake_id = "00000000-0000-0000-0000-000000000000"
        response = client.get(f"/api/v1/tags/{fake_id}")
        assert response.status_code == 404

    def test_update_tag(self, client, sample_tag):
        """Test updating a tag."""
        response = client.put(
            f"/api/v1/tags/{sample_tag['id']}",
            json={"name": "updated-tag"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["name"] == "updated-tag"

    def test_update_tag_duplicate_name(self, client, sample_tag):
        """Test updating a tag to a duplicate name fails."""
        # Create another tag
        response = client.post(
            "/api/v1/tags/",
            json={"name": "another-tag"},
        )
        another_tag = response.json()["data"]

        # Try to update second tag to first tag's name
        response = client.put(
            f"/api/v1/tags/{another_tag['id']}",
            json={"name": sample_tag["name"]},
        )
        assert response.status_code == 409

    def test_delete_tag(self, client, sample_tag):
        """Test deleting a tag."""
        response = client.delete(f"/api/v1/tags/{sample_tag['id']}")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "deleted successfully" in data["message"]

        # Verify tag is deleted
        response = client.get(f"/api/v1/tags/{sample_tag['id']}")
        assert response.status_code == 404


class TestTagNoteRelationships:
    """Test tag-note relationships."""

    def test_get_tag_notes(self, client, sample_tag):
        """Test getting notes for a tag."""
        response = client.get(f"/api/v1/tags/{sample_tag['id']}/notes")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["count"] == 0  # No notes initially
        assert isinstance(data["data"], list)

    def test_get_tag_notes_with_associations(self, client, sample_tag, sample_note):
        """Test getting notes for a tag with associations."""
        # Add note to tag
        client.post(f"/api/v1/notes/{sample_note['id']}/tags/{sample_tag['id']}")

        # Get tag's notes
        response = client.get(f"/api/v1/tags/{sample_tag['id']}/notes")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["count"] == 1
        assert data["data"][0]["id"] == sample_note["id"]

    def test_delete_tag_with_notes(self, client, sample_tag, sample_note):
        """Test deleting a tag removes it from all notes."""
        # Add note to tag
        client.post(f"/api/v1/notes/{sample_note['id']}/tags/{sample_tag['id']}")

        # Delete tag
        response = client.delete(f"/api/v1/tags/{sample_tag['id']}")
        assert response.status_code == 200
        data = response.json()
        assert "removed from" in data["message"]
        assert "note" in data["message"]

        # Note should still exist
        response = client.get(f"/api/v1/notes/{sample_note['id']}")
        assert response.status_code == 200

        # Note should have no tags
        response = client.get(f"/api/v1/notes/{sample_note['id']}/tags")
        data = response.json()
        assert data["count"] == 0
