import unittest
from decimal import Decimal
from unittest.mock import Mock, patch
from uuid import uuid4

from app.services.transaction_service import TransactionService


class FailedTransferAuditTests(unittest.TestCase):
    def test_failed_transfer_is_committed_in_a_separate_session(self):
        audit_db = Mock()
        from_wallet_id = uuid4()
        to_wallet_id = uuid4()

        with (
            patch("app.services.transaction_service.SessionLocal", return_value=audit_db),
            patch("app.services.transaction_service.TransactionRepository") as repository,
        ):
            repository.return_value.get_by_reference_code.return_value = None

            TransactionService()._record_failed_transfer(
                reference_code="TXNFAILEDTEST",
                from_wallet_id=from_wallet_id,
                to_wallet_id=to_wallet_id,
                amount=Decimal("25.00"),
                error_message="INSUFFICIENT_BALANCE",
            )

        repository.return_value.create.assert_called_once_with(
            txn_type="TRANSFER",
            amount=Decimal("25.00"),
            from_wallet_id=from_wallet_id,
            to_wallet_id=to_wallet_id,
            status="FAILED",
            description="INSUFFICIENT_BALANCE",
            reference_code="TXNFAILEDTEST",
        )
        audit_db.commit.assert_called_once()
        audit_db.close.assert_called_once()

    def test_known_failures_have_safe_audit_descriptions(self):
        self.assertEqual(
            TransactionService._failure_description("error: INSUFFICIENT_BALANCE"),
            "INSUFFICIENT_BALANCE",
        )
        self.assertEqual(
            TransactionService._failure_description("driver connection failed"),
            "TRANSFER_PROCESSING_ERROR",
        )


if __name__ == "__main__":
    unittest.main()
