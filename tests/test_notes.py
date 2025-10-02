"""
Tests for Note CRUD operations and tag relationships.
"""

import pytest


class TestNoteCRUD:
    """Test basic CRUD operations for notes."""

    def test_create_note(self, client, sample_journal):
        """Test creating a new note."""
        response = client.post(
            "/api/v1/notes/",
            json={
                "text": "My test note",
                "journal_id": sample_journal["id"],
                "meta": {"key": "value"},
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert data["success"] is True
        assert data["data"]["text"] == "My test note"
        assert data["data"]["journal_id"] == sample_journal["id"]
        assert data["data"]["meta"] == {"key": "value"}
        assert "id" in data["data"]

    def test_create_note_without_journal(self, client):
        """Test creating a note without a journal."""
        response = client.post(
            "/api/v1/notes/",
            json={"text": "Standalone note"},
        )
        assert response.status_code == 201
        data = response.json()
        assert data["data"]["journal_id"] is None

    def test_create_note_invalid_journal(self, client):
        """Test creating a note with non-existent journal fails."""
        fake_id = "00000000-0000-0000-0000-000000000000"
        response = client.post(
            "/api/v1/notes/",
            json={"text": "Test", "journal_id": fake_id},
        )
        assert response.status_code == 404
        assert "Journal" in response.json()["message"]

    def test_list_notes(self, client, sample_note):
        """Test listing notes with pagination."""
        response = client.get("/api/v1/notes/")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert len(data["data"]) >= 1
        assert data["pagination"]["total"] >= 1

    def test_list_notes_filter_by_journal(self, client, sample_journal, sample_note):
        """Test filtering notes by journal_id."""
        response = client.get(f"/api/v1/notes/?journal_id={sample_journal['id']}")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert len(data["data"]) >= 1
        for note in data["data"]:
            assert note["journal_id"] == sample_journal["id"]

    def test_get_note(self, client, sample_note):
        """Test getting a specific note by ID."""
        response = client.get(f"/api/v1/notes/{sample_note['id']}")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["id"] == sample_note["id"]

    def test_get_note_not_found(self, client):
        """Test getting a non-existent note returns 404."""
        fake_id = "00000000-0000-0000-0000-000000000000"
        response = client.get(f"/api/v1/notes/{fake_id}")
        assert response.status_code == 404

    def test_update_note(self, client, sample_note, sample_journal):
        """Test updating a note."""
        response = client.put(
            f"/api/v1/notes/{sample_note['id']}",
            json={
                "text": "Updated note text",
                "journal_id": sample_journal["id"],
                "meta": {"updated": True},
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["text"] == "Updated note text"
        assert data["data"]["meta"]["updated"] is True

    def test_update_note_invalid_journal(self, client, sample_note):
        """Test updating note with invalid journal fails."""
        fake_id = "00000000-0000-0000-0000-000000000000"
        response = client.put(
            f"/api/v1/notes/{sample_note['id']}",
            json={"text": "Test", "journal_id": fake_id},
        )
        assert response.status_code == 404
        assert "Journal" in response.json()["message"]

    def test_delete_note(self, client, sample_note):
        """Test deleting a note."""
        response = client.delete(f"/api/v1/notes/{sample_note['id']}")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "deleted successfully" in data["message"]


class TestNoteTagRelationships:
    """Test note-tag many-to-many relationships."""

    def test_get_note_tags(self, client, sample_note):
        """Test getting tags for a note."""
        response = client.get(f"/api/v1/notes/{sample_note['id']}/tags")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["count"] == 0  # No tags initially
        assert isinstance(data["data"], list)

    def test_add_tag_to_note(self, client, sample_note, sample_tag):
        """Test adding a tag to a note."""
        response = client.post(
            f"/api/v1/notes/{sample_note['id']}/tags/{sample_tag['id']}"
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert sample_tag["name"] in data["message"]

        # Verify tag is associated
        response = client.get(f"/api/v1/notes/{sample_note['id']}/tags")
        data = response.json()
        assert data["count"] == 1
        assert data["data"][0]["id"] == sample_tag["id"]

    def test_add_duplicate_tag_to_note(self, client, sample_note, sample_tag):
        """Test adding the same tag twice fails."""
        # Add tag first time
        client.post(f"/api/v1/notes/{sample_note['id']}/tags/{sample_tag['id']}")

        # Try to add again
        response = client.post(
            f"/api/v1/notes/{sample_note['id']}/tags/{sample_tag['id']}"
        )
        assert response.status_code == 409
        assert "already associated" in response.json()["message"]

    def test_add_nonexistent_tag_to_note(self, client, sample_note):
        """Test adding non-existent tag fails."""
        fake_id = "00000000-0000-0000-0000-000000000000"
        response = client.post(f"/api/v1/notes/{sample_note['id']}/tags/{fake_id}")
        assert response.status_code == 404
        assert "Tag" in response.json()["message"]

    def test_remove_tag_from_note(self, client, sample_note, sample_tag):
        """Test removing a tag from a note."""
        # Add tag first
        client.post(f"/api/v1/notes/{sample_note['id']}/tags/{sample_tag['id']}")

        # Remove tag
        response = client.delete(
            f"/api/v1/notes/{sample_note['id']}/tags/{sample_tag['id']}"
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "removed" in data["message"]

        # Verify tag is removed
        response = client.get(f"/api/v1/notes/{sample_note['id']}/tags")
        data = response.json()
        assert data["count"] == 0

    def test_remove_unassociated_tag_from_note(self, client, sample_note, sample_tag):
        """Test removing a tag that's not associated fails."""
        response = client.delete(
            f"/api/v1/notes/{sample_note['id']}/tags/{sample_tag['id']}"
        )
        assert response.status_code == 404
        assert "not associated" in response.json()["message"]

    def test_delete_note_with_tags(self, client, sample_note, sample_tag):
        """Test deleting a note with tags removes associations."""
        # Add tag to note
        client.post(f"/api/v1/notes/{sample_note['id']}/tags/{sample_tag['id']}")

        # Delete note
        response = client.delete(f"/api/v1/notes/{sample_note['id']}")
        assert response.status_code == 200
        data = response.json()
        assert "tag association" in data["message"]

        # Tag should still exist
        response = client.get(f"/api/v1/tags/{sample_tag['id']}")
        assert response.status_code == 200
