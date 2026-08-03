import { apiClient } from "@/lib/api-client";
import type { Transaction, TransactionHistory, TransactionType } from "@/types/models";
import type { TransferInput } from "./schemas";

// POST /transactions/transfer
export async function transferRequest(data: TransferInput): Promise<Transaction> {
  const res = await apiClient.post<Transaction>("/transactions/transfer", data);
  return res.data;
}

export interface TransactionHistoryParams {
  skip?: number;
  limit?: number;
  type?: TransactionType;
}

// GET /transactions/me
export async function getTransactionHistory(
  params: TransactionHistoryParams = {},
): Promise<TransactionHistory> {
  const res = await apiClient.get<TransactionHistory>("/transactions/me", { params });
  return res.data;
}

// GET /transactions/{id}
export async function getTransaction(id: string): Promise<Transaction> {
  const res = await apiClient.get<Transaction>(`/transactions/${id}`);
  return res.data;
}
