import pytest
from fastapi import status


@pytest.fixture
def auth_headers(client, test_user):
    response = client.post(
        "/api/auth/token",
        data={
            "username": test_user.email,
            "password": "test123"
        }
    )
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_register_user(client):
    response = client.post(
        "/api/auth/register",
        json={
            "email": "newuser@example.com",
            "password": "test123",  # Using a shorter password
            "full_name": "New User",
            "location": "New Location"
        }
    )
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["email"] == "newuser@example.com"
    assert data["full_name"] == "New User"
    assert data["location"] == "New Location"
    assert "id" in data


def test_register_existing_user(client, test_user):
    response = client.post(
        "/api/auth/register",
        json={
            "email": test_user.email,
            "password": "test123",  # Using a shorter password
            "full_name": "Another User",
            "location": "Another Location"
        }
    )
    assert response.status_code == status.HTTP_409_CONFLICT


def test_login_success(client, test_user):
    response = client.post(
        "/api/auth/token",
        data={
            "username": test_user.email,
            "password": "test123"  # Must match password used in test_user fixture
        }
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_wrong_password(client, test_user):
    response = client.post(
        "/api/auth/token",
        data={
            "username": test_user.email,
            "password": "wrongpass"
        }
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_login_non_existent_user(client):
    response = client.post(
        "/api/auth/token",
        data={
            "username": "nonexistent@example.com",
            "password": "test123"
        }
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_register_invalid_email(client):
    response = client.post(
        "/api/auth/register",
        json={
            "email": "invalid-email",  # Invalid email format
            "password": "test123",
            "full_name": "Test User",
            "location": "Test Location"
        }
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


def test_register_empty_required_fields(client):
    response = client.post(
        "/api/auth/register",
        json={
            "email": "",  # Empty email
            "password": "",  # Empty password
            "full_name": None,  # Optional field can be None
            "location": None  # Optional field can be None
        }
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


def test_update_user_data(client, test_user, auth_headers):
    new_data = {
        "full_name": "Updated Name",
        "location": "Updated Location"
    }
    response = client.put(
        "/api/users/me",  # Using PUT for full user data updates
        json=new_data,
        headers=auth_headers
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["full_name"] == new_data["full_name"]
    assert data["location"] == new_data["location"]
    assert data["email"] == test_user.email  # Email should remain unchanged


def test_change_user_password(client, test_user, auth_headers):
    # Try changing password
    change_data = {
        "old_password": "test123",  # Current password from test_user fixture
        "new_password": "newpass123"  # New password must be at least 8 chars
    }
    response = client.post(
        "/api/users/me/change-password",
        json=change_data,
        headers=auth_headers
    )
    assert response.status_code == status.HTTP_204_NO_CONTENT

    # Try logging in with new password
    login_response = client.post(
        "/api/auth/token",
        data={
            "username": test_user.email,
            "password": "newpass123"
        }
    )
    assert login_response.status_code == status.HTTP_200_OK
    assert "access_token" in login_response.json()

    # Try logging in with old password (should fail)
    old_login_response = client.post(
        "/api/auth/token",
        data={
            "username": test_user.email,
            "password": "test123"
        }
    )
    assert old_login_response.status_code == status.HTTP_401_UNAUTHORIZED
