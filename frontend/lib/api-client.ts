import axios, { AxiosError, InternalAxiosRequestConfig } from "axios";
import { getAccessToken, getRefreshToken, setTokens, clearTokens } from "./auth-token";
import { normalizeError } from "./http-error";

// Base URL không có prefix /api/v1 vì backend include router thẳng với
// prefix riêng từng domain (/auth, /wallets, /transactions) trong app/main.py
export const apiClient = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL,
});

apiClient.interceptors.request.use((config) => {
  const token = getAccessToken();
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

type RetryConfig = InternalAxiosRequestConfig & { _retry?: boolean };
let refreshPromise: Promise<string> | null = null;

async function refreshAccessToken(): Promise<string> {
  const token = getRefreshToken();
  if (!token) throw new Error("Missing refresh token");
  const response = await axios.post<{ access_token: string; refresh_token: string }>(
    `${process.env.NEXT_PUBLIC_API_URL}/auth/refresh`, { refresh_token: token },
  );
  setTokens(response.data.access_token, response.data.refresh_token);
  return response.data.access_token;
}

apiClient.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const config = error.config as RetryConfig | undefined;
    const isLoginRequest = config?.url === "/auth/login";
    if (error.response?.status === 401 && config && !config._retry && !isLoginRequest && getRefreshToken()) {
      config._retry = true;
      try {
        refreshPromise ??= refreshAccessToken().finally(() => { refreshPromise = null; });
        config.headers.Authorization = `Bearer ${await refreshPromise}`;
        return apiClient(config);
      } catch {
        clearTokens();
      }
    }
    return Promise.reject(normalizeError(error));
  },
);
