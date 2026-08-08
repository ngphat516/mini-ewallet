import unittest
from decimal import Decimal

from app.services.idempotency_service import request_fingerprint


class RequestFingerprintTests(unittest.TestCase):
    def test_equivalent_money_representations_have_same_fingerprint(self):
        fingerprints = {
            request_fingerprint("DEPOSIT", amount=Decimal(value))
            for value in ("500", "500.0", "500.00")
        }

        self.assertEqual(len(fingerprints), 1)

    def test_different_money_values_have_different_fingerprints(self):
        first = request_fingerprint("DEPOSIT", amount=Decimal("500.00"))
        second = request_fingerprint("DEPOSIT", amount=Decimal("500.01"))

        self.assertNotEqual(first, second)

    def test_operation_and_payload_are_part_of_fingerprint(self):
        deposit = request_fingerprint("DEPOSIT", amount=Decimal("500"))
        withdraw = request_fingerprint("WITHDRAW", amount=Decimal("500"))

        self.assertNotEqual(deposit, withdraw)


if __name__ == "__main__":
    unittest.main()
