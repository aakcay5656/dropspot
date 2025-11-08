from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.user_schema import UserSignup, UserLogin, TokenResponse
from app.services.auth_service import signup_user, login_user

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/signup", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
def signup(signup_data: UserSignup, db: Session = Depends(get_db)):
    """Yeni kullanıcı kaydı"""
    return signup_user(signup_data, db)

@router.post("/login", response_model=TokenResponse)
def login(login_data: UserLogin, db: Session = Depends(get_db)):
    """Kullanıcı girişi"""
    return login_user(login_data, db)
