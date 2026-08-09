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

type NavItem = {
  href: string;
  label: string;
  icon: ComponentType<SVGProps<SVGSVGElement>>;
};

const WALLET_BRANCHES: NavItem[] = [
  { href: "/wallet", label: "Tổng quan", icon: IconWallet },
  { href: "/wallet/deposit", label: "Nạp tiền", icon: IconArrowDownCircle },
  { href: "/wallet/withdraw", label: "Rút tiền", icon: IconArrowUpCircle },
];

const MAIN_BRANCHES: NavItem[] = [
  { href: "/transfer", label: "Chuyển tiền", icon: IconSend },
  { href: "/transactions", label: "Lịch sử giao dịch", icon: IconHistory },
  { href: "/security", label: "Security", icon: IconWallet },
];

function NavLink({ item, active }: { item: NavItem; active: boolean }) {
  const Icon = item.icon;

  return (
    <Link
      href={item.href}
      aria-current={active ? "page" : undefined}
      className={`flex h-10 items-center gap-2 whitespace-nowrap rounded-xl px-3 text-sm font-medium transition-all ${
        active
          ? "bg-primary text-primary-foreground shadow-sm"
          : "text-muted-foreground hover:bg-muted hover:text-foreground"
      }`}
    >
      <Icon className="h-[18px] w-[18px] shrink-0" />
      {item.label}
    </Link>
  );
}

export function DashboardNav() {
  const pathname = usePathname();
  const walletActive = pathname.startsWith("/wallet");

  return (
    <header className="sticky top-0 z-40 border-b border-border/80 bg-card/95 shadow-[0_1px_12px_rgba(15,23,42,0.04)] backdrop-blur">
      <div className="mx-auto flex h-16 w-full max-w-7xl items-center justify-between gap-4 px-4 sm:px-6 lg:px-8">
        <Link href="/wallet" className="flex shrink-0 items-center gap-3" aria-label="Mini E-Wallet - Trang chủ">
          <span className="flex h-10 w-10 items-center justify-center rounded-xl bg-primary text-primary-foreground shadow-sm shadow-primary/25">
            <IconWallet className="h-6 w-6" />
          </span>
          <span className="hidden sm:block">
            <span className="block text-sm font-bold tracking-tight">Mini E-Wallet</span>
            <span className="block text-[11px] text-muted-foreground">Quản lý tài chính</span>
          </span>
        </Link>

        <div className="flex min-w-0 items-center gap-1 sm:gap-2">
          <div className="hidden max-w-56 md:block">
            <UserInfo />
          </div>
          <LogoutButton />
        </div>
      </div>

      <nav className="border-t border-border/70" aria-label="Điều hướng chính">
        <div className="nav-scroll mx-auto flex min-h-16 w-full max-w-7xl items-stretch gap-5 overflow-x-auto px-4 sm:px-6 lg:px-8">
          <div className="relative flex shrink-0 items-center gap-2 py-3">
            <div className={`flex h-10 items-center gap-2 rounded-xl border px-3 text-sm font-semibold ${
              walletActive ? "border-primary/30 bg-primary/5 text-primary" : "border-border text-foreground"
            }`}>
              <IconWallet className="h-[18px] w-[18px]" />
              Ví của tôi
            </div>

            <span className="h-px w-3 bg-border" aria-hidden="true" />
            <div className="relative flex items-center gap-1 pl-2 before:absolute before:bottom-1 before:left-0 before:top-1 before:w-px before:bg-border">
              {WALLET_BRANCHES.map((item) => (
                <div key={item.href} className="relative pl-2 before:absolute before:left-0 before:top-1/2 before:h-px before:w-2 before:bg-border">
                  <NavLink item={item} active={pathname === item.href} />
                </div>
              ))}
            </div>
          </div>

          <span className="my-4 w-px shrink-0 bg-border" aria-hidden="true" />

          <div className="flex shrink-0 items-center gap-1 py-3">
            {MAIN_BRANCHES.map((item) => (
              <NavLink key={item.href} item={item} active={pathname.startsWith(item.href)} />
            ))}
          </div>
        </div>
      </nav>
    </header>
  );
}
