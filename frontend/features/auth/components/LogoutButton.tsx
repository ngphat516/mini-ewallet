"use client";

import { useLogout } from "../hooks";
import { IconLogout } from "@/components/ui/icons";

export function LogoutButton() {
  const logout = useLogout();
  return (
    <button
      onClick={logout}
      className="flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium text-muted-foreground transition-colors hover:bg-muted hover:text-danger"
    >
      <IconLogout className="h-5 w-5 shrink-0" />
      Đăng xuất
    </button>
  );
}
