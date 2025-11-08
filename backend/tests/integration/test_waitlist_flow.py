import pytest
from datetime import datetime, timedelta
from app.models.user import User, UserRole
from app.models.drop import Drop
from app.services.waitlist_service import join_waitlist, claim_drop
from app.utils.jwt_handler import hash_password
from fastapi import HTTPException


def test_waitlist_join_idempotency(db):
    """Waitlist join idempotency testi"""
    # User oluştur
    user = User(email="test@example.com", password_hash=hash_password("test"))
    db.add(user)
    db.commit()
    db.refresh(user)

    # Drop oluştur
    drop = Drop(
        name="Test Drop",
        total_stock=10,
        claim_window_start=datetime.utcnow() + timedelta(hours=1),
        claim_window_end=datetime.utcnow() + timedelta(hours=2)
    )
    db.add(drop)
    db.commit()
    db.refresh(drop)

    # İlk join
    result1 = join_waitlist(drop.id, user, db)
    assert result1.position == 1

    # İkinci join (idempotent)
    with pytest.raises(HTTPException) as exc:
        join_waitlist(drop.id, user, db)

    assert exc.value.status_code == 409


def test_claim_process(db):
    """Claim süreci testi"""
    # User oluştur
    user = User(email="test@example.com", password_hash=hash_password("test"))
    db.add(user)
    db.commit()
    db.refresh(user)

    # Drop oluştur (claim window açık)
    drop = Drop(
        name="Test Drop",
        total_stock=10,
        claim_window_start=datetime.utcnow() - timedelta(minutes=5),
        claim_window_end=datetime.utcnow() + timedelta(hours=1)
    )
    db.add(drop)
    db.commit()
    db.refresh(drop)

    # Waitlist'e katıl
    join_waitlist(drop.id, user, db)

    # Claim yap
    result = claim_drop(drop.id, user, db)

    assert result.claim_code is not None
    assert result.claim_code.startswith("DROPSPOT-")
    assert result.expires_at is not None

    # İkinci claim (idempotent - aynı code döner)
    result2 = claim_drop(drop.id, user, db)
    assert result2.claim_code == result.claim_code
