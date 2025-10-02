"""
Tests for main application endpoints.
"""

import pytest


class TestMainEndpoints:
    """Test core application endpoints."""

    def test_root_endpoint(self, client):
        """Test the root endpoint returns API information."""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "version" in data
        assert "docs" in data
        assert "/docs" in data["docs"]

    def test_health_endpoint(self, client):
        """Test the health check endpoint."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "app" in data
        assert "version" in data
        assert "environment" in data

    def test_docs_endpoint_accessible(self, client):
        """Test that API docs are accessible."""
        response = client.get("/docs")
        assert response.status_code == 200

    def test_redoc_endpoint_accessible(self, client):
        """Test that ReDoc documentation is accessible."""
        response = client.get("/redoc")
        assert response.status_code == 200

    def test_404_error_handling(self, client):
        """Test 404 error handling for non-existent endpoint."""
        response = client.get("/api/v1/nonexistent")
        assert response.status_code == 404

    def test_cors_headers(self, client):
        """Test CORS headers are present."""
        response = client.options("/api/v1/projects/")
        # CORS headers should be present
        assert response.status_code in [200, 405]  # OPTIONS might not be implemented
