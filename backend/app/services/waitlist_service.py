from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from sqlalchemy import and_, func
from fastapi import HTTPException, status
from datetime import datetime, timedelta
from app.models.drop import Drop, DropStatus
from app.models.waitlist import Waitlist, WaitlistStatus
from app.models.claim_code import ClaimCode
from app.models.user import User
from app.schemas.waitlist_schema import WaitlistJoinResponse, WaitlistLeaveResponse, ClaimResponse
from app.utils.seed import calculate_priority_score, generate_claim_code
import time


def join_waitlist(drop_id: int, current_user: User, db: Session, request_time_ms: int = None) -> WaitlistJoinResponse:
    """Waitlist'e katıl (Idempotent)"""

    # Drop kontrolü
    drop = db.query(Drop).filter(Drop.id == drop_id).first()
    if not drop:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Drop not found"
        )

    # Drop aktif mi?
    if drop.status != DropStatus.ACTIVE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Drop is not active"
        )

    # Zaten waitlist'te mi?
    existing_entry = db.query(Waitlist).filter(
        and_(
            Waitlist.drop_id == drop_id,
            Waitlist.user_id == current_user.id
        )
    ).first()

    if existing_entry:
        # Idempotent: Zaten katıldıysa mevcut pozisyonu döndür
        position = db.query(func.count(Waitlist.id)).filter(
            and_(
                Waitlist.drop_id == drop_id,
                Waitlist.status == WaitlistStatus.WAITING,
                Waitlist.priority_score < existing_entry.priority_score
            )
        ).scalar() + 1

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Already in waitlist at position {position}"
        )

    # Rapid action kontrolü (aynı drop'a son 1 dakikada kaç kez join/leave yaptı)
    rapid_actions = db.query(func.count(Waitlist.id)).filter(
        and_(
            Waitlist.user_id == current_user.id,
            Waitlist.drop_id == drop_id,
            Waitlist.created_at >= datetime.utcnow() - timedelta(minutes=1)
        )
    ).scalar()

    # Signup latency (request zamanı - server zamanı farkı)
    if request_time_ms is None:
        signup_latency_ms = int(time.time() * 1000) % 1000
    else:
        signup_latency_ms = abs(int(time.time() * 1000) - request_time_ms) % 10000

    # Priority score hesapla
    priority_score = calculate_priority_score(
        user_created_at=current_user.created_at,
        signup_latency_ms=signup_latency_ms,
        rapid_actions_count=rapid_actions
    )

    # Transaction ile ekle
    try:
        new_entry = Waitlist(
            drop_id=drop_id,
            user_id=current_user.id,
            priority_score=priority_score,
            signup_latency_ms=signup_latency_ms,
            account_age_days=(datetime.utcnow() - current_user.created_at).days,
            rapid_actions_count=rapid_actions
        )

        db.add(new_entry)
        db.commit()
        db.refresh(new_entry)

        # Pozisyon hesapla
        position = db.query(func.count(Waitlist.id)).filter(
            and_(
                Waitlist.drop_id == drop_id,
                Waitlist.status == WaitlistStatus.WAITING,
                Waitlist.priority_score < priority_score
            )
        ).scalar() + 1

        return WaitlistJoinResponse(
            message="Successfully joined waitlist",
            position=position,
            priority_score=priority_score
        )

    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Already in waitlist"
        )


def leave_waitlist(drop_id: int, current_user: User, db: Session) -> WaitlistLeaveResponse:
    """Waitlist'ten ayrıl"""

    waitlist_entry = db.query(Waitlist).filter(
        and_(
            Waitlist.drop_id == drop_id,
            Waitlist.user_id == current_user.id
        )
    ).first()

    if not waitlist_entry:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Not in waitlist"
        )

    # Zaten claim yapmış mı?
    if waitlist_entry.status == WaitlistStatus.CLAIMED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot leave after claiming"
        )

    db.delete(waitlist_entry)
    db.commit()

    return WaitlistLeaveResponse(message="Successfully left waitlist")


def claim_drop(drop_id: int, current_user: User, db: Session) -> ClaimResponse:
    """Drop'u claim et (Idempotent + Row Lock)"""

    # Transaction başlat
    try:
        # Drop'u row lock ile al
        drop = db.query(Drop).with_for_update().filter(Drop.id == drop_id).first()

        if not drop:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Drop not found"
            )

        # Claim window açık mı?
        now = datetime.utcnow()
        if now < drop.claim_window_start or now > drop.claim_window_end:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Claim window is not open"
            )

        # Kullanıcı waitlist'te mi?
        waitlist_entry = db.query(Waitlist).filter(
            and_(
                Waitlist.drop_id == drop_id,
                Waitlist.user_id == current_user.id
            )
        ).first()

        if not waitlist_entry:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Not in waitlist"
            )

        # Zaten claim yapmış mı? (Idempotent)
        if waitlist_entry.status == WaitlistStatus.CLAIMED:
            existing_claim = db.query(ClaimCode).filter(
                ClaimCode.waitlist_id == waitlist_entry.id
            ).first()

            return ClaimResponse(
                message="Already claimed",
                claim_code=existing_claim.code,
                expires_at=existing_claim.expires_at
            )

        # Stok kontrolü
        if drop.claimed_count >= drop.total_stock:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Out of stock"
            )

        # Claim işlemi
        waitlist_entry.status = WaitlistStatus.CLAIMED
        waitlist_entry.claimed_at = datetime.utcnow()

        # Claim code oluştur
        claim_code_str = generate_claim_code()
        claim_code = ClaimCode(
            code=claim_code_str,
            waitlist_id=waitlist_entry.id,
            expires_at=datetime.utcnow() + timedelta(hours=24)
        )

        # Claimed count artır
        drop.claimed_count += 1

        db.add(claim_code)
        db.commit()
        db.refresh(claim_code)

        return ClaimResponse(
            message="Claim successful",
            claim_code=claim_code_str,
            expires_at=claim_code.expires_at
        )

    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Claim failed: {str(e)}"
        )
