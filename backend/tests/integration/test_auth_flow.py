import pytest
from fastapi import status


@pytest.mark.integration
class TestAuthFlow:
    """Test authentication flow end-to-end"""

    def test_signup_and_login_flow(self, client):
        """Test complete signup and login flow"""
        # 1. Signup
        signup_response = client.post(
            "/auth/signup",
            json={
                "email": "integration@test.com",
                "password": "testpass123"
            }
        )

        assert signup_response.status_code == status.HTTP_201_CREATED
        signup_data = signup_response.json()
        assert "access_token" in signup_data
        assert signup_data["user"]["email"] == "integration@test.com"

        # 2. Login with same credentials
        login_response = client.post(
            "/auth/login",
            json={
                "email": "integration@test.com",
                "password": "testpass123"
            }
        )

        assert login_response.status_code == status.HTTP_200_OK
        login_data = login_response.json()
        assert "access_token" in login_data

    def test_protected_route_without_token(self, client, test_drop):
        """Test accessing protected route without token"""
        response = client.post(f"/drops/{test_drop.id}/join")

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_protected_route_with_token(self, client, test_drop, user_token):
        """Test accessing protected route with valid token"""
        response = client.post(
            f"/drops/{test_drop.id}/join",
            headers={"Authorization": f"Bearer {user_token}"}
        )

        assert response.status_code in [status.HTTP_200_OK, status.HTTP_400_BAD_REQUEST]
