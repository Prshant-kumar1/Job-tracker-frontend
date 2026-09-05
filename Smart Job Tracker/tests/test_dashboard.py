"""
Tests for dashboard endpoint.
"""
import pytest


def test_dashboard_summary(client, auth_headers):
    """Test getting dashboard summary."""
    # Create applications with different statuses
    statuses = ["applied", "applied", "oa", "interview", "rejected", "offer"]
    for status in statuses:
        client.post("/applications/", headers=auth_headers, json={
            "company": f"Company {status}",
            "role": "Engineer",
            "status": status
        })
    
    # Get dashboard summary
    response = client.get("/dashboard/summary", headers=auth_headers)
    assert response.status_code == 200
    
    data = response.json()
    assert data["total_applications"] == 6
    assert data["applied_count"] == 2
    assert data["oa_count"] == 1
    assert data["interview_count"] == 1
    assert data["rejected_count"] == 1
    assert data["offer_count"] == 1
    assert "recent_applications" in data
    assert "upcoming_followups" in data


def test_dashboard_empty(client, auth_headers):
    """Test dashboard with no applications."""
    response = client.get("/dashboard/summary", headers=auth_headers)
    assert response.status_code == 200
    
    data = response.json()
    assert data["total_applications"] == 0
    assert data["applied_count"] == 0
    assert len(data["recent_applications"]) == 0
    assert len(data["upcoming_followups"]) == 0


def test_dashboard_requires_auth(client):
    """Test that dashboard requires authentication."""
    response = client.get("/dashboard/summary")
    assert response.status_code == 401


def test_dashboard_upcoming_followups(client, auth_headers):
    """Test that upcoming follow-ups are included."""
    # Create application with future follow-up date
    client.post("/applications/", headers=auth_headers, json={
        "company": "Google",
        "role": "Engineer",
        "status": "applied",
        "follow_up_date": "2025-12-31"
    })
    
    response = client.get("/dashboard/summary", headers=auth_headers)
    data = response.json()
    
    assert len(data["upcoming_followups"]) == 1
    assert data["upcoming_followups"][0]["company"] == "Google"
