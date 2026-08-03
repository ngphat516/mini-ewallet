// Mirrors backend/app/schemas/*.py — giữ đồng bộ thủ công khi backend đổi response_model.

export interface User {
  user_id: string;
  full_name: string;
  email: string;
  phone: string;
  is_active: boolean;
  is_verified: boolean;
  created_at: string;
}

export type WalletStatus = "ACTIVE" | "FROZEN" | "CLOSED";

export interface Wallet {
  wallet_id: string;
  user_id: string;
  account_number: string;
  balance: string; // Decimal -> serialize thành string
  currency: string;
  status: WalletStatus;
  created_at: string;
}

export type TransactionType = "DEPOSIT" | "WITHDRAW" | "TRANSFER";
export type TransactionStatus = "SUCCESS" | "FAILED";

export interface Transaction {
  txn_id: string;
  reference_code: string;
  txn_type: TransactionType;
  from_wallet_id: string | null;
  to_wallet_id: string | null;
  amount: string;
  fee: string;
  from_balance_before: string | null;
  from_balance_after: string | null;
  to_balance_before: string | null;
  to_balance_after: string | null;
  status: TransactionStatus;
  description: string | null;
  created_at: string;
}

export interface TransactionHistory {
  total: number;
  skip: number;
  limit: number;
  items: Transaction[];
}
