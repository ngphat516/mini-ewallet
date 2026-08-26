import asyncio
import json
import unittest
from unittest.mock import AsyncMock, Mock, patch

from app.main import health_check


class HealthCheckTests(unittest.TestCase):
    def test_returns_200_when_all_dependencies_are_healthy(self):
        connection = Mock()
        connection.__enter__ = Mock(return_value=connection)
        connection.__exit__ = Mock(return_value=False)
        mongo = Mock()
        mongo.command = AsyncMock()
        redis = Mock()
        redis.ping = AsyncMock()

        with (
            patch("app.main.engine.connect", return_value=connection),
            patch("app.main.get_mongo_db", return_value=mongo),
            patch("app.main.get_redis", return_value=redis),
        ):
            response = asyncio.run(health_check())

        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.body), {
            "sqlserver": "ok", "mongodb": "ok", "redis": "ok",
        })

    def test_returns_503_when_a_dependency_is_unhealthy(self):
        mongo = Mock()
        mongo.command = AsyncMock()
        redis = Mock()
        redis.ping = AsyncMock()

        with (
            patch("app.main.engine.connect", side_effect=RuntimeError("offline")),
            patch("app.main.get_mongo_db", return_value=mongo),
            patch("app.main.get_redis", return_value=redis),
        ):
            response = asyncio.run(health_check())

        body = json.loads(response.body)
        self.assertEqual(response.status_code, 503)
        self.assertEqual(body["sqlserver"], "lỗi: RuntimeError")
        self.assertEqual(body["mongodb"], "ok")
        self.assertEqual(body["redis"], "ok")


if __name__ == "__main__":
    unittest.main()
