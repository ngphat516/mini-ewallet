import { apiClient } from "@/lib/api-client";
import type { User } from "@/types/models";
import type { LoginInput, RegisterInput } from "./schemas";

// Khớp schemas/user.py: TokenResponse
export interface TokenResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
}

// POST /auth/register
export async function registerRequest(data: RegisterInput): Promise<User> {
  const res = await apiClient.post<User>("/auth/register", data);
  return res.data;
}

// POST /auth/login
export async function loginRequest(data: LoginInput): Promise<TokenResponse> {
  const res = await apiClient.post<TokenResponse>("/auth/login", data);
  return res.data;
}

// GET /auth/me
export async function getMe(): Promise<User> {
  const res = await apiClient.get<User>("/auth/me");
  return res.data;
}
