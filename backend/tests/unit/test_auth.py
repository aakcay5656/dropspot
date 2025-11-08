import pytest
from backend.app.services.auth_service import signup_user, login_user
from backend.app.schemas.user_schema import UserSignup, UserLogin
from fastapi import HTTPException


def test_signup_success(db):
    """Başarılı kullanıcı kaydı"""
    signup_data = UserSignup(email="test@example.com", password="password123")
    result = signup_user(signup_data, db)

    assert result.user.email == "test@example.com"
    assert result.access_token is not None


def test_signup_duplicate_email(db):
    """Aynı email ile ikinci kayıt denemesi"""
    signup_data = UserSignup(email="test@example.com", password="password123")
    signup_user(signup_data, db)

    with pytest.raises(HTTPException) as exc:
        signup_user(signup_data, db)

    assert exc.value.status_code == 409


def test_login_success(db):
    """Başarılı giriş"""
    # Önce kayıt
    signup_data = UserSignup(email="test@example.com", password="password123")
    signup_user(signup_data, db)

    # Giriş
    login_data = UserLogin(email="test@example.com", password="password123")
    result = login_user(login_data, db)

    assert result.user.email == "test@example.com"
    assert result.access_token is not None


def test_login_wrong_password(db):
    """Yanlış şifre ile giriş"""
    # Önce kayıt
    signup_data = UserSignup(email="test@example.com", password="password123")
    signup_user(signup_data, db)

    # Yanlış şifre
    login_data = UserLogin(email="test@example.com", password="wrongpassword")

    with pytest.raises(HTTPException) as exc:
        login_user(login_data, db)

    assert exc.value.status_code == 401
