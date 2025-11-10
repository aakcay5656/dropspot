import pytest
from fastapi import status
from app.models.waitlist import Waitlist, WaitlistStatus


@pytest.mark.integration
class TestWaitlistFlow:
    """Test waitlist join/leave flow"""

    def test_join_waitlist_success(self, client, test_drop, user_token):
        """Test joining waitlist successfully"""
        response = client.post(
            f"/drops/{test_drop.id}/join",
            headers={"Authorization": f"Bearer {user_token}"}
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "position" in data
        assert "priority_score" in data
        assert data["message"] == "Successfully joined waitlist"

    def test_join_waitlist_idempotency(self, client, test_drop, user_token):
        """Test that joining twice returns 409 Conflict"""
        # First join
        response1 = client.post(
            f"/drops/{test_drop.id}/join",
            headers={"Authorization": f"Bearer {user_token}"}
        )
        assert response1.status_code == status.HTTP_200_OK

        # Second join (idempotent)
        response2 = client.post(
            f"/drops/{test_drop.id}/join",
            headers={"Authorization": f"Bearer {user_token}"}
        )
        assert response2.status_code == status.HTTP_409_CONFLICT
        assert "Already in waitlist" in response2.json()["detail"]

    def test_leave_waitlist_success(self, client, test_drop, user_token):
        """Test leaving waitlist"""
        # First join
        client.post(
            f"/drops/{test_drop.id}/join",
            headers={"Authorization": f"Bearer {user_token}"}
        )

        # Then leave
        response = client.post(
            f"/drops/{test_drop.id}/leave",
            headers={"Authorization": f"Bearer {user_token}"}
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.json()["message"] == "Successfully left waitlist"

    def test_leave_waitlist_not_joined(self, client, test_drop, user_token):
        """Test leaving when not in waitlist"""
        response = client.post(
            f"/drops/{test_drop.id}/leave",
            headers={"Authorization": f"Bearer {user_token}"}
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_multiple_users_priority_ordering(self, client, db, test_drop):
        """Test that multiple users get different priority scores"""
        # Create 3 users and join
        users_data = []

        for i in range(3):
            # Signup
            signup_response = client.post(
                "/auth/signup",
                json={
                    "email": f"user{i}@test.com",
                    "password": "testpass123"
                }
            )
            token = signup_response.json()["access_token"]

            # Join waitlist
            join_response = client.post(
                f"/drops/{test_drop.id}/join",
                headers={"Authorization": f"Bearer {token}"}
            )

            users_data.append({
                "token": token,
                "priority_score": join_response.json()["priority_score"]
            })

        # Check that all scores are different
        scores = [u["priority_score"] for u in users_data]
        assert len(scores) == len(set(scores)), "All priority scores should be unique"
