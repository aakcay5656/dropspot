import pytest
from fastapi import status
from datetime import datetime, timedelta


@pytest.mark.integration
class TestAdminCRUD:
    """Test admin CRUD operations"""

    def test_create_drop_as_admin(self, client, admin_token):
        """Test creating drop as admin"""
        response = client.post(
            "/admin/drops",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={
                "name": "Admin Created Drop",
                "description": "Test drop",
                "total_stock": 100,
                "claim_window_start": (datetime.utcnow() + timedelta(hours=1)).isoformat(),
                "claim_window_end": (datetime.utcnow() + timedelta(hours=2)).isoformat()
            }
        )

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["name"] == "Admin Created Drop"

    def test_create_drop_as_regular_user(self, client, user_token):
        """Test that regular user cannot create drop"""
        response = client.post(
            "/admin/drops",
            headers={"Authorization": f"Bearer {user_token}"},
            json={
                "name": "User Drop",
                "description": "Should fail",
                "total_stock": 50,
                "claim_window_start": (datetime.utcnow() + timedelta(hours=1)).isoformat(),
                "claim_window_end": (datetime.utcnow() + timedelta(hours=2)).isoformat()
            }
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_update_drop_as_admin(self, client, test_drop, admin_token):
        """Test updating drop as admin"""
        response = client.put(
            f"/admin/drops/{test_drop.id}",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={
                "name": "Updated Drop Name",
                "total_stock": 200
            }
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["name"] == "Updated Drop Name"
        assert data["total_stock"] == 200

    def test_delete_drop_as_admin(self, client, test_drop, admin_token):
        """Test deleting drop as admin"""
        response = client.delete(
            f"/admin/drops/{test_drop.id}",
            headers={"Authorization": f"Bearer {admin_token}"}
        )

        assert response.status_code == status.HTTP_204_NO_CONTENT

        # Verify drop is deleted
        get_response = client.get(f"/drops/{test_drop.id}")
        assert get_response.status_code == status.HTTP_404_NOT_FOUND
