import axios from "axios";
import { getAccessToken, clearTokens } from "./auth-token";
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

apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (axios.isAxiosError(error) && error.response?.status === 401) {
      clearTokens();
    }
    return Promise.reject(normalizeError(error));
  },
);
