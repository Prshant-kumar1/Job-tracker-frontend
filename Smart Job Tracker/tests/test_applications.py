"""
Tests for job applications CRUD endpoints.
"""
import pytest


def test_create_application_success(client, auth_headers):
    """Test creating a job application."""
    response = client.post("/applications/", headers=auth_headers, json={
        "company": "Google",
        "role": "Software Engineer",
        "status": "applied",
        "location": "Mountain View, CA",
        "date_applied": "2024-01-15"
    })
    
    assert response.status_code == 201
    data = response.json()
    assert data["company"] == "Google"
    assert data["role"] == "Software Engineer"
    assert data["status"] == "applied"
    assert "id" in data


def test_create_application_requires_auth(client):
    """Test that creating application requires authentication."""
    response = client.post("/applications/", json={
        "company": "Google",
        "role": "Software Engineer",
        "status": "applied"
    })
    
    assert response.status_code == 401


def test_create_application_validation(client, auth_headers):
    """Test input validation on application creation."""
    # Empty company name
    response = client.post("/applications/", headers=auth_headers, json={
        "company": "   ",
        "role": "Engineer",
        "status": "applied"
    })
    assert response.status_code == 422
    
    # Invalid URL
    response = client.post("/applications/", headers=auth_headers, json={
        "company": "Google",
        "role": "Engineer",
        "apply_link": "not-a-url"
    })
    assert response.status_code == 422


def test_list_applications(client, auth_headers):
    """Test listing applications with pagination."""
    # Create a few applications
    for i in range(5):
        client.post("/applications/", headers=auth_headers, json={
            "company": f"Company {i}",
            "role": "Engineer",
            "status": "applied"
        })
    
    # Get first page
    response = client.get("/applications/?page=1&page_size=3", headers=auth_headers)
    assert response.status_code == 200
    
    data = response.json()
    assert "items" in data
    assert "total" in data
    assert "page" in data
    assert "total_pages" in data
    assert data["total"] == 5
    assert len(data["items"]) == 3
    assert data["page"] == 1
    assert data["total_pages"] == 2
    assert data["has_next"] is True
    assert data["has_prev"] is False


def test_list_applications_filter_by_status(client, auth_headers):
    """Test filtering applications by status."""
    # Create applications with different statuses
    client.post("/applications/", headers=auth_headers, json={
        "company": "Company A",
        "role": "Engineer",
        "status": "applied"
    })
    client.post("/applications/", headers=auth_headers, json={
        "company": "Company B",
        "role": "Engineer",
        "status": "interview"
    })
    
    # Filter by interview status
    response = client.get("/applications/?status=interview", headers=auth_headers)
    assert response.status_code == 200
    
    data = response.json()
    assert data["total"] == 1
    assert data["items"][0]["status"] == "interview"


def test_get_application(client, auth_headers):
    """Test getting a single application."""
    # Create application
    create_response = client.post("/applications/", headers=auth_headers, json={
        "company": "Google",
        "role": "Engineer",
        "status": "applied"
    })
    app_id = create_response.json()["id"]
    
    # Get application
    response = client.get(f"/applications/{app_id}", headers=auth_headers)
    assert response.status_code == 200
    
    data = response.json()
    assert data["id"] == app_id
    assert data["company"] == "Google"


def test_get_application_not_found(client, auth_headers):
    """Test getting non-existent application."""
    response = client.get("/applications/99999", headers=auth_headers)
    assert response.status_code == 404


def test_update_application(client, auth_headers):
    """Test updating an application."""
    # Create application
    create_response = client.post("/applications/", headers=auth_headers, json={
        "company": "Google",
        "role": "Engineer",
        "status": "applied"
    })
    app_id = create_response.json()["id"]
    
    # Update application
    response = client.put(f"/applications/{app_id}", headers=auth_headers, json={
        "status": "interview",
        "notes": "First round scheduled"
    })
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "interview"
    assert data["notes"] == "First round scheduled"
    assert data["company"] == "Google"  # Unchanged


def test_delete_application(client, auth_headers):
    """Test deleting an application."""
    # Create application
    create_response = client.post("/applications/", headers=auth_headers, json={
        "company": "Google",
        "role": "Engineer",
        "status": "applied"
    })
    app_id = create_response.json()["id"]
    
    # Delete application
    response = client.delete(f"/applications/{app_id}", headers=auth_headers)
    assert response.status_code == 204
    
    # Verify it's deleted
    get_response = client.get(f"/applications/{app_id}", headers=auth_headers)
    assert get_response.status_code == 404


def test_applications_isolated_by_user(client, test_user):
    """Test that users can only see their own applications."""
    # Create first user and application
    login1 = client.post("/auth/login", json={
        "email": test_user["email"],
        "password": test_user["password"]
    })
    headers1 = {"Authorization": f"Bearer {login1.json()['access_token']}"}
    
    app_response = client.post("/applications/", headers=headers1, json={
        "company": "Google",
        "role": "Engineer",
        "status": "applied"
    })
    app_id = app_response.json()["id"]
    
    # Create second user
    client.post("/auth/register", json={
        "name": "User Two",
        "email": "user2@example.com",
        "password": "pass123"
    })
    login2 = client.post("/auth/login", json={
        "email": "user2@example.com",
        "password": "pass123"
    })
    headers2 = {"Authorization": f"Bearer {login2.json()['access_token']}"}
    
    # User 2 should not be able to access User 1's application
    response = client.get(f"/applications/{app_id}", headers=headers2)
    assert response.status_code == 404
    
    # User 2 should not see User 1's applications in list
    list_response = client.get("/applications/", headers=headers2)
    assert list_response.json()["total"] == 0
