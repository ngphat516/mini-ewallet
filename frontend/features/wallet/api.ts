import { apiClient } from "@/lib/api-client";
import type { Wallet } from "@/types/models";
import type { AmountInput } from "./schemas";

// GET /wallets/me
export async function getMyWallet(): Promise<Wallet> {
  const res = await apiClient.get<Wallet>("/wallets/me");
  return res.data;
}

// POST /wallets/deposit
export async function depositRequest(data: AmountInput): Promise<Wallet> {
  const res = await apiClient.post<Wallet>("/wallets/deposit", data);
  return res.data;
}

// POST /wallets/withdraw
export async function withdrawRequest(data: AmountInput): Promise<Wallet> {
  const res = await apiClient.post<Wallet>("/wallets/withdraw", data);
  return res.data;
}
