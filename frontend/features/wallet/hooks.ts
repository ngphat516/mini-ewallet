"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { depositRequest, getMyWallet, withdrawRequest } from "./api";

export const walletKeys = {
  me: ["wallet", "me"] as const,
};

export function useMyWallet() {
  return useQuery({
    queryKey: walletKeys.me,
    queryFn: getMyWallet,
  });
}

export function useDeposit() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: depositRequest,
    onSuccess: (wallet) => {
      queryClient.setQueryData(walletKeys.me, wallet);
    },
  });
}

export function useWithdraw() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: withdrawRequest,
    onSuccess: (wallet) => {
      queryClient.setQueryData(walletKeys.me, wallet);
    },
  });
}
