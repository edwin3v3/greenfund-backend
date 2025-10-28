import pytest
from fastapi import status


@pytest.fixture
def auth_headers(client, test_user):
    response = client.post(
        "/api/auth/token",
        data={"username": test_user.email, "password": "test123"}
    )
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_get_users_me_unauthenticated(client):
    """Unauthenticated requests should be rejected with 401."""
    response = client.get("/api/users/me")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_get_users_me_authenticated(client, test_user, auth_headers):
    """Authenticated user can fetch their own profile."""
    response = client.get("/api/users/me", headers=auth_headers)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["email"] == test_user.email
    assert data["full_name"] == test_user.full_name


def test_badges_flow(client, test_db, test_user, auth_headers):
    """Create a Badge in the DB, award it via API, then verify listing and count endpoints."""
    from app.models import Badge

    # 1) create a badge record directly in the test DB
    badge = Badge(name="eco-warrior", description="Awarded for eco actions")
    test_db.add(badge)
    test_db.commit()
    test_db.refresh(badge)

    # 2) award it to the test user via the test-only endpoint
    award_resp = client.post(f"/api/badges/me/award_test/{badge.name}", headers=auth_headers)
    assert award_resp.status_code == status.HTTP_200_OK
    award_data = award_resp.json()
    # The returned object should include a nested badge with the correct name
    assert "badge" in award_data
    assert award_data["badge"]["name"] == badge.name

    # 3) fetch the user's badges
    my_badges = client.get("/api/badges/me", headers=auth_headers)
    assert my_badges.status_code == status.HTTP_200_OK
    badges_list = my_badges.json()
    assert isinstance(badges_list, list)
    assert any(b["badge"]["name"] == badge.name for b in badges_list)

    # 4) check the count endpoint
    count_resp = client.get("/api/badges/me/count", headers=auth_headers)
    assert count_resp.status_code == status.HTTP_200_OK
    assert count_resp.json().get("count") >= 1
