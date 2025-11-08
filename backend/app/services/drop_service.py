from sqlalchemy.orm import Session
from sqlalchemy import and_
from fastapi import HTTPException, status
from typing import List, Optional
from datetime import datetime
from app.models.drop import Drop, DropStatus
from app.models.waitlist import Waitlist, WaitlistStatus
from app.models.user import User
from app.schemas.drop_schema import DropCreate, DropUpdate, DropResponse


def get_drops(
        db: Session,
        current_user: Optional[User] = None,
        status_filter: Optional[str] = None,
        limit: int = 20,
        offset: int = 0
) -> List[DropResponse]:
    """Aktif drop'ları listele"""
    query = db.query(Drop)

    # Status filter
    if status_filter:
        query = query.filter(Drop.status == status_filter)
    else:
        query = query.filter(Drop.status == DropStatus.ACTIVE)

    drops = query.order_by(Drop.claim_window_start.desc()).limit(limit).offset(offset).all()

    # User joined kontrolü
    drop_responses = []
    for drop in drops:
        drop_dict = DropResponse.model_validate(drop).model_dump()

        # Kullanıcı bu drop'a katıldı mı?
        if current_user:
            waitlist_entry = db.query(Waitlist).filter(
                and_(
                    Waitlist.drop_id == drop.id,
                    Waitlist.user_id == current_user.id
                )
            ).first()
            drop_dict['user_joined'] = waitlist_entry is not None

        drop_responses.append(DropResponse(**drop_dict))

    return drop_responses


def get_drop_by_id(db: Session, drop_id: int, current_user: Optional[User] = None) -> DropResponse:
    """Drop detayı getir"""
    drop = db.query(Drop).filter(Drop.id == drop_id).first()

    if not drop:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Drop not found"
        )

    drop_dict = DropResponse.model_validate(drop).model_dump()

    # User joined kontrolü
    if current_user:
        waitlist_entry = db.query(Waitlist).filter(
            and_(
                Waitlist.drop_id == drop.id,
                Waitlist.user_id == current_user.id
            )
        ).first()
        drop_dict['user_joined'] = waitlist_entry is not None

    return DropResponse(**drop_dict)


def create_drop(drop_data: DropCreate, creator: User, db: Session) -> Drop:
    """Yeni drop oluştur (Admin)"""
    # Zaman kontrolü
    if drop_data.claim_window_start >= drop_data.claim_window_end:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Claim window start must be before end time"
        )

    new_drop = Drop(
        name=drop_data.name,
        description=drop_data.description,
        total_stock=drop_data.total_stock,
        claim_window_start=drop_data.claim_window_start,
        claim_window_end=drop_data.claim_window_end,
        created_by_user_id=creator.id
    )

    db.add(new_drop)
    db.commit()
    db.refresh(new_drop)

    return new_drop


def update_drop(drop_id: int, drop_data: DropUpdate, db: Session) -> Drop:
    """Drop güncelle (Admin)"""
    drop = db.query(Drop).filter(Drop.id == drop_id).first()

    if not drop:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Drop not found"
        )

    # Update fields
    update_data = drop_data.model_dump(exclude_unset=True)

    # Zaman kontrolü
    if 'claim_window_start' in update_data and 'claim_window_end' in update_data:
        if update_data['claim_window_start'] >= update_data['claim_window_end']:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Claim window start must be before end time"
            )

    for key, value in update_data.items():
        setattr(drop, key, value)

    db.commit()
    db.refresh(drop)

    return drop


def delete_drop(drop_id: int, db: Session):
    """Drop sil (Admin)"""
    drop = db.query(Drop).filter(Drop.id == drop_id).first()

    if not drop:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Drop not found"
        )

    db.delete(drop)
    db.commit()
