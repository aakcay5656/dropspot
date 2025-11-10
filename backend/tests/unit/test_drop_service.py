import pytest
from datetime import datetime, timedelta
from app.services.drop_service import get_drops, create_drop
from app.schemas.drop_schema import DropCreate


@pytest.mark.unit
class TestDropService:
    """Test drop service functions"""

    def test_get_drops_empty(self, db):
        """Test getting drops from empty database"""
        drops = get_drops(db)

        assert drops == []

    def test_get_drops_with_data(self, db, test_drop):
        """Test getting drops with existing data"""
        drops = get_drops(db)

        assert len(drops) == 1
        assert drops[0].name == test_drop.name

    def test_create_drop(self, db, admin_user):
        """Test creating a drop"""
        drop_data = DropCreate(
            name="New Drop",
            description="Test drop",
            total_stock=50,
            claim_window_start=datetime.utcnow() + timedelta(hours=1),
            claim_window_end=datetime.utcnow() + timedelta(hours=2)
        )

        created_drop = create_drop(drop_data, admin_user, db)

        assert created_drop.name == "New Drop"
        assert created_drop.total_stock == 50
        assert created_drop.claimed_count == 0
        assert created_drop.created_by_user_id == admin_user.id

    def test_create_drop_invalid_window(self, db, admin_user):
        """Test creating drop with invalid claim window"""
        drop_data = DropCreate(
            name="Invalid Drop",
            description="Test",
            total_stock=50,
            claim_window_start=datetime.utcnow() + timedelta(hours=2),
            claim_window_end=datetime.utcnow() + timedelta(hours=1)  # End before start
        )

        with pytest.raises(Exception) as exc:
            create_drop(drop_data, admin_user, db)

        assert exc.value.status_code == 400
