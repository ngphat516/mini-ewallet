import unittest
from pydantic import ValidationError

from app.core.config import Settings


class SettingsTests(unittest.TestCase):
    def settings_values(self, **overrides):
        values = {
            "SQLSERVER_HOST": "localhost",
            "SQLSERVER_DB": "ebanking",
            "SQLSERVER_USER": "sa",
            "SQLSERVER_PASSWORD": "password",
            "MONGODB_URL": "mongodb://localhost:27017",
            "MONGODB_DB": "ebanking_logs",
            "REDIS_URL": "redis://localhost:6379/0",
            "JWT_SECRET": "a" * 32,
        }
        values.update(overrides)
        return Settings(**values)

    def test_parses_multiple_cors_origins(self):
        settings = self.settings_values(CORS_ORIGINS="https://wallet.example.com, https://admin.example.com/")
        self.assertEqual(settings.cors_origins, [
            "https://wallet.example.com",
            "https://admin.example.com",
        ])

    def test_rejects_short_jwt_secret(self):
        with self.assertRaises(ValidationError):
            self.settings_values(JWT_SECRET="too-short")

    def test_rejects_wildcard_cors_with_credentials(self):
        with self.assertRaises(ValidationError):
            self.settings_values(CORS_ORIGINS="*")


if __name__ == "__main__":
    unittest.main()
