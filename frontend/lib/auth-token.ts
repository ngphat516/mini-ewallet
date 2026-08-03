// Lưu token bằng cookie (thay vì localStorage) để middleware.ts đọc được ở edge.
// Lưu ý: cookie set trực tiếp từ client nên vẫn đọc được bằng JS (không phải httpOnly).
// Đủ dùng cho scaffold này; lên production nên chuyển sang Route Handler set cookie httpOnly.

export const ACCESS_TOKEN_COOKIE = "ew_access_token";
export const REFRESH_TOKEN_COOKIE = "ew_refresh_token";

// Khớp JWT_EXPIRE_MINUTES / JWT_REFRESH_EXPIRE_DAYS trong backend/app/core/config.py
const ACCESS_TOKEN_MAX_AGE = 15 * 60;
const REFRESH_TOKEN_MAX_AGE = 7 * 24 * 60 * 60;

function setCookie(name: string, value: string, maxAgeSeconds: number) {
  document.cookie = `${name}=${encodeURIComponent(value)}; path=/; max-age=${maxAgeSeconds}; samesite=lax`;
}

function getCookie(name: string): string | null {
  const match = document.cookie.match(new RegExp(`(?:^|; )${name}=([^;]*)`));
  return match ? decodeURIComponent(match[1]) : null;
}

function deleteCookie(name: string) {
  document.cookie = `${name}=; path=/; max-age=0`;
}

export function setTokens(accessToken: string, refreshToken: string) {
  setCookie(ACCESS_TOKEN_COOKIE, accessToken, ACCESS_TOKEN_MAX_AGE);
  setCookie(REFRESH_TOKEN_COOKIE, refreshToken, REFRESH_TOKEN_MAX_AGE);
}

export function getAccessToken(): string | null {
  if (typeof document === "undefined") return null;
  return getCookie(ACCESS_TOKEN_COOKIE);
}

export function clearTokens() {
  deleteCookie(ACCESS_TOKEN_COOKIE);
  deleteCookie(REFRESH_TOKEN_COOKIE);
}
