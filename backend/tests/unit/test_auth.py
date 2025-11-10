import pytest
from fastapi import status
from app.schemas.user_schema import UserSignup, UserLogin
from app.services.auth_service import signup_user, login_user
from app.utils.jwt_handler import hash_password, verify_password, decode_token


@pytest.mark.unit
class TestAuthService:
    """Test authentication service functions"""

    def test_signup_success(self, db):
        """Test successful user signup"""
        signup_data = UserSignup(
            email="newuser@example.com",
            password="securepassword123"
        )

        result = signup_user(signup_data, db)

        assert result.user.email == "newuser@example.com"
        assert result.user.role == "user"
        assert result.access_token is not None
        assert result.token_type == "bearer"

    def test_signup_duplicate_email(self, db, test_user):
        """Test signup with duplicate email returns 409"""
        signup_data = UserSignup(
            email=test_user.email,
            password="password123"
        )

        with pytest.raises(Exception) as exc:
            signup_user(signup_data, db)

        assert exc.value.status_code == status.HTTP_409_CONFLICT

    def test_login_success(self, db, test_user):
        """Test successful login"""
        login_data = UserLogin(
            email="test@example.com",
            password="testpassword123"
        )

        result = login_user(login_data, db)

        assert result.user.email == test_user.email
        assert result.access_token is not None

    def test_login_wrong_password(self, db, test_user):
        """Test login with wrong password"""
        login_data = UserLogin(
            email="test@example.com",
            password="wrongpassword"
        )

        with pytest.raises(Exception) as exc:
            login_user(login_data, db)

        assert exc.value.status_code == status.HTTP_401_UNAUTHORIZED

    def test_login_nonexistent_user(self, db):
        """Test login with non-existent user"""
        login_data = UserLogin(
            email="nonexistent@example.com",
            password="password123"
        )

        with pytest.raises(Exception) as exc:
            login_user(login_data, db)

        assert exc.value.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.unit
class TestJWTHandler:
    """Test JWT token operations"""

    def test_password_hashing(self):
        """Test password hashing and verification"""
        password = "mysecurepassword"
        hashed = hash_password(password)

        assert hashed != password
        assert verify_password(password, hashed) is True
        assert verify_password("wrongpassword", hashed) is False

    def test_token_creation_and_decode(self):
        """Test JWT token creation and decoding"""
        from app.utils.jwt_handler import create_access_token

        user_id = 123
        token = create_access_token(data={"sub": user_id})

        assert token is not None

        payload = decode_token(token)
        assert payload is not None
        assert payload.get("sub") == str(user_id)  # JWT converts to string

    def test_invalid_token_decode(self):
        """Test decoding invalid token"""
        invalid_token = "invalid.token.here"

        payload = decode_token(invalid_token)

        assert payload is None
