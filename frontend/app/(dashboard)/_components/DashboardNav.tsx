"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { LogoutButton } from "@/features/auth/components/LogoutButton";
import { UserInfo } from "@/features/auth/components/UserInfo";
import {
  IconWallet,
  IconArrowDownCircle,
  IconArrowUpCircle,
  IconSend,
  IconHistory,
} from "@/components/ui/icons";
import type { ComponentType, SVGProps } from "react";

// Mỗi mục khớp 1 component/route riêng — bấm vào là điều hướng thẳng tới đó.
const NAV_ITEMS: {
  href: string;
  label: string;
  icon: ComponentType<SVGProps<SVGSVGElement>>;
}[] = [
  { href: "/wallet", label: "Tổng quan ví", icon: IconWallet },
  { href: "/wallet/deposit", label: "Nạp tiền", icon: IconArrowDownCircle },
  { href: "/wallet/withdraw", label: "Rút tiền", icon: IconArrowUpCircle },
  { href: "/transfer", label: "Chuyển tiền", icon: IconSend },
  { href: "/transactions", label: "Lịch sử giao dịch", icon: IconHistory },
];

export function DashboardNav() {
  const pathname = usePathname();

  return (
    <aside className="flex w-64 shrink-0 flex-col justify-between border-r border-border bg-card p-4">
      <div className="flex flex-col gap-6">
        <div className="flex items-center gap-2 px-2 py-1">
          <span className="flex h-8 w-8 items-center justify-center rounded-lg bg-primary text-primary-foreground">
            <IconWallet className="h-5 w-5" />
          </span>
          <span className="font-semibold tracking-tight">Mini E-Wallet</span>
        </div>

        <nav className="flex flex-col gap-1">
          {NAV_ITEMS.map(({ href, label, icon: Icon }) => {
            const active = pathname === href;
            return (
              <Link
                key={href}
                href={href}
                aria-current={active ? "page" : undefined}
                className={`flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition-colors ${
                  active
                    ? "bg-primary text-primary-foreground shadow-sm"
                    : "text-foreground hover:bg-muted"
                }`}
              >
                <Icon className="h-5 w-5 shrink-0" />
                {label}
              </Link>
            );
          })}
        </nav>
      </div>

      <div className="flex flex-col gap-1 border-t border-border pt-3">
        <UserInfo />
        <LogoutButton />
      </div>
    </aside>
  );
}
