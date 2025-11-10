import pytest
from fastapi import status
from datetime import datetime, timedelta


@pytest.mark.integration
class TestClaimFlow:
    """Test claim functionality end-to-end"""

    def test_claim_success(self, client, active_claim_drop, user_token, db, test_user):
        """Test successful claim"""
        # First join waitlist
        client.post(
            f"/drops/{active_claim_drop.id}/join",
            headers={"Authorization": f"Bearer {user_token}"}
        )

        # Then claim
        response = client.post(
            f"/drops/{active_claim_drop.id}/claim",
            headers={"Authorization": f"Bearer {user_token}"}
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "claim_code" in data
        assert data["claim_code"].startswith("DROPSPOT-")
        assert "expires_at" in data

    def test_claim_idempotency(self, client, active_claim_drop, user_token):
        """Test that claiming twice returns same claim code"""
        # Join
        client.post(
            f"/drops/{active_claim_drop.id}/join",
            headers={"Authorization": f"Bearer {user_token}"}
        )

        # First claim
        response1 = client.post(
            f"/drops/{active_claim_drop.id}/claim",
            headers={"Authorization": f"Bearer {user_token}"}
        )
        claim_code1 = response1.json()["claim_code"]

        # Second claim (idempotent)
        response2 = client.post(
            f"/drops/{active_claim_drop.id}/claim",
            headers={"Authorization": f"Bearer {user_token}"}
        )
        claim_code2 = response2.json()["claim_code"]

        assert response2.status_code == status.HTTP_200_OK
        assert claim_code1 == claim_code2

    def test_claim_without_joining(self, client, active_claim_drop, user_token):
        """Test claim without joining waitlist"""
        response = client.post(
            f"/drops/{active_claim_drop.id}/claim",
            headers={"Authorization": f"Bearer {user_token}"}
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_claim_window_closed(self, client, test_drop, user_token):
        """Test claim when window is closed"""
        # Join
        client.post(
            f"/drops/{test_drop.id}/join",
            headers={"Authorization": f"Bearer {user_token}"}
        )

        # Try to claim (window not open yet)
        response = client.post(
            f"/drops/{test_drop.id}/claim",
            headers={"Authorization": f"Bearer {user_token}"}
        )

        assert response.status_code == status.HTTP_429_TOO_MANY_REQUESTS

    def test_claim_stock_depletion(self, client, db, admin_user):
        """Test that stock is properly depleted"""
        # Create drop with only 2 stock
        from app.models.drop import Drop, DropStatus

        drop = Drop(
            name="Limited Drop",
            description="Only 2 stock",
            total_stock=2,
            claimed_count=0,
            claim_window_start=datetime.utcnow() - timedelta(minutes=10),
            claim_window_end=datetime.utcnow() + timedelta(hours=1),
            status=DropStatus.ACTIVE,
            created_by_user_id=admin_user.id
        )
        db.add(drop)
        db.commit()
        db.refresh(drop)

        # Create 3 users
        tokens = []
        for i in range(3):
            signup_response = client.post(
                "/auth/signup",
                json={
                    "email": f"stock{i}@test.com",
                    "password": "testpass123"
                }
            )
            tokens.append(signup_response.json()["access_token"])

        # All join
        for token in tokens:
            client.post(
                f"/drops/{drop.id}/join",
                headers={"Authorization": f"Bearer {token}"}
            )

        # First 2 claim successfully
        for token in tokens[:2]:
            response = client.post(
                f"/drops/{drop.id}/claim",
                headers={"Authorization": f"Bearer {token}"}
            )
            assert response.status_code == status.HTTP_200_OK

        # Third user should get "Out of stock"
        response = client.post(
            f"/drops/{drop.id}/claim",
            headers={"Authorization": f"Bearer {tokens[2]}"}
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "Out of stock" in response.json()["detail"]
