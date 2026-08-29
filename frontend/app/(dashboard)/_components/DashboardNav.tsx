"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

const items = [["/wallet", "Wallet"], ["/transactions", "Activity"], ["/security", "Account"]] as const;

export function DashboardNav() {
  const pathname = usePathname();

  return (
    <nav className="flex gap-5" aria-label="Main navigation">
      {items.map(([href, label]) => {
        const active = pathname === href || (href !== "/wallet" && pathname.startsWith(href));
        return <Link key={href} href={href} className={`text-sm font-medium ${active ? "text-white" : "text-white/55 hover:text-white"}`}>{label}</Link>;
      })}
    </nav>
  );
}
