from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status
from app.models.user import User
from app.schemas.user_schema import UserSignup, UserLogin, TokenResponse, UserResponse
from app.utils.jwt_handler import hash_password, verify_password, create_access_token


def signup_user(signup_data: UserSignup, db: Session) -> TokenResponse:
    """Yeni kullanıcı kaydı"""
    # Email kontrolü
    existing_user = db.query(User).filter(User.email == signup_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered"
        )

    # Kullanıcı oluştur
    hashed_password = hash_password(signup_data.password)
    new_user = User(
        email=signup_data.email,
        password=hashed_password
    )

    try:
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered"
        )

    # Token oluştur
    access_token = create_access_token(data={"sub": new_user.id})

    return TokenResponse(
        access_token=access_token,
        user=UserResponse.model_validate(new_user)
    )


def login_user(login_data: UserLogin, db: Session) -> TokenResponse:
    """Kullanıcı girişi"""
    user = db.query(User).filter(User.email == login_data.email).first()

    if not user or not verify_password(login_data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    # Token oluştur
    access_token = create_access_token(data={"sub": user.id})

    return TokenResponse(
        access_token=access_token,
        user=UserResponse.model_validate(user)
    )
