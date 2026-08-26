import unittest
from types import SimpleNamespace
from unittest.mock import Mock, patch
from uuid import uuid4

from fastapi.security import HTTPAuthorizationCredentials

from app.api.deps import get_current_user_id
from app.core.exceptions import PhoneAlreadyExistsException, UserInactiveException
from app.services.auth_service import AuthService


class AccountStatusTests(unittest.TestCase):
    def test_login_rejects_inactive_user_before_issuing_tokens(self):
        db = Mock()
        user = SimpleNamespace(is_active=False, password_hash="hashed-password")
        data = SimpleNamespace(email="user@example.com", password="Password1")

        with (
            patch("app.services.auth_service.UserRepository") as user_repo,
            patch("app.services.auth_service.verify_password", return_value=True),
        ):
            user_repo.return_value.get_by_email.return_value = user

            with self.assertRaises(UserInactiveException):
                AuthService().login(db, data, "test-device", None)

        db.commit.assert_not_called()

    def test_refresh_revokes_all_tokens_for_an_inactive_user(self):
        db = Mock()
        user_id = uuid4()
        session_id = uuid4()
        stored = SimpleNamespace(user_id=user_id, session_id=session_id)

        with (
            patch("app.services.auth_service.decode_token", return_value={"sub": str(user_id), "sid": str(session_id)}),
            patch("app.services.auth_service.hash_token", return_value="hash"),
            patch("app.services.auth_service.RefreshTokenRepository") as refresh_repo,
            patch("app.services.auth_service.UserRepository") as user_repo,
        ):
            refresh_repo.return_value.get_by_hash_for_update.return_value = stored
            user_repo.return_value.get_by_id.return_value = SimpleNamespace(is_active=False)

            with self.assertRaises(UserInactiveException):
                AuthService().refresh(db, "refresh-token", "test-device", None)

        refresh_repo.return_value.revoke_all.assert_called_once()
        db.commit.assert_called_once()

    def test_authenticated_request_rejects_inactive_user(self):
        user_id = uuid4()
        credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials="access-token")

        with (
            patch("app.api.deps.decode_token", return_value={"sub": str(user_id)}),
            patch("app.api.deps.UserRepository") as user_repo,
        ):
            user_repo.return_value.get_by_id.return_value = SimpleNamespace(is_active=False)

            with self.assertRaises(UserInactiveException):
                get_current_user_id(credentials=credentials, db=Mock())


class RegistrationTests(unittest.TestCase):
    def test_register_rejects_a_phone_number_that_is_already_used(self):
        db = Mock()
        data = SimpleNamespace(
            full_name="Test User",
            email="new@example.com",
            phone="0912345678",
            password="Password1",
        )

        with patch("app.services.auth_service.UserRepository") as user_repo:
            user_repo.return_value.get_by_email.return_value = None
            user_repo.return_value.get_by_phone.return_value = SimpleNamespace()

            with self.assertRaises(PhoneAlreadyExistsException):
                AuthService().register(db, data)

        db.commit.assert_not_called()


if __name__ == "__main__":
    unittest.main()
