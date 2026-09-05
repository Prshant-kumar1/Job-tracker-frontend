"""
Tests for authentication endpoints.
"""
import pytest


def test_register_success(client):
    """Test successful user registration."""
    response = client.post("/auth/register", json={
        "name": "New User",
        "email": "newuser@example.com",
        "password": "securepass123"
    })
    
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "newuser@example.com"
    assert data["name"] == "New User"
    assert "id" in data
    assert "hashed_password" not in data  # Should not expose password


def test_register_duplicate_email(client, test_user):
    """Test registration with existing email fails."""
    response = client.post("/auth/register", json={
        "name": "Another User",
        "email": test_user["email"],  # Same email as test_user
        "password": "differentpass"
    })
    
    assert response.status_code == 400
    assert "already exists" in response.json()["detail"].lower()


def test_register_invalid_email(client):
    """Test registration with invalid email format."""
    response = client.post("/auth/register", json={
        "name": "Test User",
        "email": "not-an-email",
        "password": "securepass123"
    })
    
    assert response.status_code == 422  # Validation error


def test_register_short_password(client):
    """Test registration with password shorter than 6 chars."""
    response = client.post("/auth/register", json={
        "name": "Test User",
        "email": "test@example.com",
        "password": "short"
    })
    
    assert response.status_code == 422


def test_login_success(client, test_user):
    """Test successful login."""
    response = client.post("/auth/login", json={
        "email": test_user["email"],
        "password": test_user["password"]
    })
    
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"


def test_login_wrong_password(client, test_user):
    """Test login with wrong password."""
    response = client.post("/auth/login", json={
        "email": test_user["email"],
        "password": "wrongpassword"
    })
    
    assert response.status_code == 401
    assert "incorrect" in response.json()["detail"].lower()


def test_login_nonexistent_user(client):
    """Test login with non-existent email."""
    response = client.post("/auth/login", json={
        "email": "nonexistent@example.com",
        "password": "anypassword"
    })
    
    assert response.status_code == 401


def test_refresh_token_success(client, test_user):
    """Test refresh token endpoint."""
    # Login to get tokens
    login_response = client.post("/auth/login", json={
        "email": test_user["email"],
        "password": test_user["password"]
    })
    refresh_token = login_response.json()["refresh_token"]
    
    # Use refresh token to get new tokens
    response = client.post("/auth/refresh", json={
        "refresh_token": refresh_token
    })
    
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["access_token"] != login_response.json()["access_token"]  # Should be new


def test_refresh_token_invalid(client):
    """Test refresh with invalid token."""
    response = client.post("/auth/refresh", json={
        "refresh_token": "invalid_token"
    })
    
    assert response.status_code == 401


def test_refresh_token_with_access_token(client, test_user):
    """Test that access tokens can't be used for refresh."""
    # Login to get tokens
    login_response = client.post("/auth/login", json={
        "email": test_user["email"],
        "password": test_user["password"]
    })
    access_token = login_response.json()["access_token"]
    
    # Try to use access token as refresh token
    response = client.post("/auth/refresh", json={
        "refresh_token": access_token
    })
    
    assert response.status_code == 401
