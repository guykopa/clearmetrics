import pytest
from clearmetrics.domain.models.user import User, UserRole


class TestUserRole:
    def test_valid_roles_exist(self) -> None:
        assert UserRole.ADMIN.value == "admin"
        assert UserRole.ANALYST.value == "analyst"
        assert UserRole.VIEWER.value == "viewer"


class TestUserCreation:
    def test_creates_valid_user(self) -> None:
        user = User(
            id="usr-001",
            email="admin@clearmetrics.io",
            role=UserRole.ADMIN,
            hashed_password="hashed_secret",
        )
        assert user.id == "usr-001"
        assert user.email == "admin@clearmetrics.io"
        assert user.role == UserRole.ADMIN
        assert user.hashed_password == "hashed_secret"

    def test_user_is_immutable(self) -> None:
        user = User(
            id="usr-001",
            email="viewer@clearmetrics.io",
            role=UserRole.VIEWER,
            hashed_password="hashed_secret",
        )
        with pytest.raises(Exception):
            user.role = UserRole.ADMIN  # type: ignore[misc]

    def test_raises_on_empty_id(self) -> None:
        with pytest.raises(ValueError):
            User(
                id="",
                email="user@clearmetrics.io",
                role=UserRole.ANALYST,
                hashed_password="hashed_secret",
            )

    def test_raises_on_invalid_email(self) -> None:
        with pytest.raises(ValueError):
            User(
                id="usr-002",
                email="not-an-email",
                role=UserRole.ANALYST,
                hashed_password="hashed_secret",
            )

    def test_raises_on_empty_email(self) -> None:
        with pytest.raises(ValueError):
            User(
                id="usr-003",
                email="",
                role=UserRole.ANALYST,
                hashed_password="hashed_secret",
            )

    def test_raises_on_empty_hashed_password(self) -> None:
        with pytest.raises(ValueError):
            User(
                id="usr-004",
                email="user@clearmetrics.io",
                role=UserRole.ANALYST,
                hashed_password="",
            )

    def test_all_roles_accepted(self) -> None:
        for role in UserRole:
            user = User(
                id="usr-005",
                email="user@clearmetrics.io",
                role=role,
                hashed_password="hashed_secret",
            )
            assert user.role == role
