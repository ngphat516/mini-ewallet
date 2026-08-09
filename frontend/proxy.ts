import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";
import { ACCESS_TOKEN_COOKIE } from "@/lib/auth-token";

// `middleware.ts` đã bị đổi tên thành `proxy.ts` kể từ Next.js 16.
// Đây là nơi duy nhất chặn truy cập route (dashboard) khi chưa đăng nhập,
// thay vì rải rác check token trong từng page (~ giống api/deps.py phía backend).
export function proxy(request: NextRequest) {
  const hasToken = request.cookies.has(ACCESS_TOKEN_COOKIE);

  if (!hasToken) {
    return NextResponse.redirect(new URL("/login", request.url));
  }
}

export const config = {
  matcher: ["/wallet/:path*", "/transactions/:path*", "/transfer/:path*", "/security/:path*"],
};
