from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.middleware.auth_middleware import require_admin
from app.models.user import User
from app.schemas.drop_schema import DropCreate, DropUpdate, DropResponse
from app.services.drop_service import create_drop, update_drop, delete_drop

router = APIRouter(prefix="/admin", tags=["Admin"])

@router.post("/drops", response_model=DropResponse, status_code=status.HTTP_201_CREATED)
def admin_create_drop(
    drop_data: DropCreate,
    db: Session = Depends(get_db),
    admin_user: User = Depends(require_admin)
):
    """Yeni drop oluştur (Admin only)"""
    return create_drop(drop_data, admin_user, db)

@router.put("/drops/{drop_id}", response_model=DropResponse)
def admin_update_drop(
    drop_id: int,
    drop_data: DropUpdate,
    db: Session = Depends(get_db),
    admin_user: User = Depends(require_admin)
):
    """Drop güncelle (Admin only)"""
    return update_drop(drop_id, drop_data, db)

@router.delete("/drops/{drop_id}", status_code=status.HTTP_204_NO_CONTENT)
def admin_delete_drop(
    drop_id: int,
    db: Session = Depends(get_db),
    admin_user: User = Depends(require_admin)
):
    """Drop sil (Admin only)"""
    delete_drop(drop_id, db)
    return None
