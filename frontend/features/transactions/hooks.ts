"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import {
  getTransaction,
  getTransactionHistory,
  transferRequest,
  type TransactionHistoryParams,
} from "./api";
import { walletKeys } from "@/features/wallet/hooks";

export const transactionKeys = {
  history: (params: TransactionHistoryParams) => ["transactions", "history", params] as const,
  detail: (id: string) => ["transactions", "detail", id] as const,
};

export function useTransactionHistory(params: TransactionHistoryParams = {}) {
  return useQuery({
    queryKey: transactionKeys.history(params),
    queryFn: () => getTransactionHistory(params),
  });
}

export function useTransaction(id: string) {
  return useQuery({
    queryKey: transactionKeys.detail(id),
    queryFn: () => getTransaction(id),
    enabled: Boolean(id),
  });
}

export function useTransfer() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: transferRequest,
    onSuccess: () => {
      // Chuyển tiền làm thay đổi số dư ví và lịch sử giao dịch -> invalidate cả hai
      queryClient.invalidateQueries({ queryKey: walletKeys.me });
      queryClient.invalidateQueries({ queryKey: ["transactions", "history"] });
    },
  });
}
