import unittest

from fastapi.testclient import TestClient

from app.main import app


class APITests(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_health_endpoint_contains_disclaimer(self):
        response = self.client.get("/api/v1/health")
        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(body["status"], "ok")
        self.assertIn("not guaranteed financial advice", body["disclaimer"])


if __name__ == "__main__":
    unittest.main()
