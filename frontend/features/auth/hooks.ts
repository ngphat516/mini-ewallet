"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useRouter } from "next/navigation";
import { getMe, loginRequest, registerRequest } from "./api";
import { setTokens, clearTokens } from "@/lib/auth-token";
import { useAuthStore } from "./store";

export const authKeys = {
  me: ["auth", "me"] as const,
};

export function useCurrentUser() {
  return useQuery({
    queryKey: authKeys.me,
    queryFn: getMe,
  });
}

export function useRegister() {
  const router = useRouter();

  return useMutation({
    mutationFn: registerRequest,
    onSuccess: () => {
      router.push("/login");
    },
  });
}

export function useLogin() {
  const router = useRouter();
  const setAuthenticated = useAuthStore((s) => s.setAuthenticated);

  return useMutation({
    mutationFn: loginRequest,
    onSuccess: (data) => {
      setTokens(data.access_token, data.refresh_token);
      setAuthenticated(true);
      router.push("/wallet");
    },
  });
}

export function useLogout() {
  const router = useRouter();
  const queryClient = useQueryClient();
  const setAuthenticated = useAuthStore((s) => s.setAuthenticated);

  return () => {
    clearTokens();
    setAuthenticated(false);
    queryClient.clear();
    router.push("/login");
  };
}
