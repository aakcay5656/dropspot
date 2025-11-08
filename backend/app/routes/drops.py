from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app.middleware.auth_middleware import get_current_user
from app.models.user import User
from app.schemas.drop_schema import DropResponse
from app.schemas.waitlist_schema import WaitlistJoinResponse, WaitlistLeaveResponse, ClaimResponse
from app.services.drop_service import get_drops, get_drop_by_id
from app.services.waitlist_service import join_waitlist, leave_waitlist, claim_drop

router = APIRouter(prefix="/drops", tags=["Drops"])

@router.get("", response_model=List[DropResponse])
def list_drops(
    status_filter: Optional[str] = Query(None, description="Filter by status"),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user)
):
    """Aktif drop'ları listele"""
    return get_drops(db, current_user, status_filter, limit, offset)

@router.get("/{drop_id}", response_model=DropResponse)
def get_drop(
    drop_id: int,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user)
):
    """Drop detayı"""
    return get_drop_by_id(db, drop_id, current_user)

@router.post("/{drop_id}/join", response_model=WaitlistJoinResponse)
def join_drop_waitlist(
    drop_id: int,
    request_time_ms: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Waitlist'e katıl"""
    return join_waitlist(drop_id, current_user, db, request_time_ms)

@router.post("/{drop_id}/leave", response_model=WaitlistLeaveResponse)
def leave_drop_waitlist(
    drop_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Waitlist'ten ayrıl"""
    return leave_waitlist(drop_id, current_user, db)

@router.post("/{drop_id}/claim", response_model=ClaimResponse)
def claim_drop_item(
    drop_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Drop'u claim et"""
    return claim_drop(drop_id, current_user, db)
