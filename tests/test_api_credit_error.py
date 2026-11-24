"""Offline check: credit shortage is distinct from request rate limiting."""
import io
import sys
import unittest
import urllib.error
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "app"))
import solar_engine


class APIQuotaErrorTests(unittest.TestCase):
    @staticmethod
    def request_error(code, response):
        def fake_open(request, timeout):
            raise urllib.error.HTTPError(
                url=request.full_url, code=code, msg="test error", hdrs={},
                fp=io.BytesIO(response.encode("utf-8"))
            )
        return fake_open

    def invoke(self, code, response):
        return solar_engine.request_solar(
            "fake-api-key", "safe system prompt", "x@example.com", "공지",
            "가상 테스트", opener=self.request_error(code, response)
        )

    def test_payment_required(self):
        with self.assertRaises(solar_engine.CreditsExhaustedError):
            self.invoke(402, '{"error": "payment_required"}')

    def test_insufficient_balance_with_403(self):
        with self.assertRaises(solar_engine.CreditsExhaustedError):
            self.invoke(403, '{"error": {"code": "insufficient_balance", "message": "No credits"}}')

    def test_insufficient_quota_with_429(self):
        with self.assertRaises(solar_engine.CreditsExhaustedError):
            self.invoke(429, '{"error": {"code": "insufficient_quota"}}')

    def test_plain_429_is_rate_limit_not_credit_shortage(self):
        with self.assertRaises(solar_engine.ProviderError) as caught:
            self.invoke(429, '{"error": {"code": "rate_limit_exceeded", "message": "too many requests"}}')
        self.assertNotIsInstance(caught.exception, solar_engine.CreditsExhaustedError)
        self.assertIn('요청 횟수', str(caught.exception))

    def test_plain_401_is_not_credit_shortage(self):
        with self.assertRaises(solar_engine.ProviderError) as caught:
            self.invoke(401, '{"error": "invalid_api_key"}')
        self.assertNotIsInstance(caught.exception, solar_engine.CreditsExhaustedError)


if __name__ == '__main__':
    unittest.main(verbosity=2)
