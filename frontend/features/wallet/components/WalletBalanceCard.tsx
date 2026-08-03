"use client";

import { Card } from "@/components/ui/Card";
import { Badge } from "@/components/ui/Badge";
import { IconWallet } from "@/components/ui/icons";
import { useMyWallet } from "../hooks";
import type { WalletStatus } from "@/types/models";

const STATUS_TONE: Record<WalletStatus, "success" | "warning" | "danger"> = {
  ACTIVE: "success",
  FROZEN: "warning",
  CLOSED: "danger",
};

const STATUS_LABEL: Record<WalletStatus, string> = {
  ACTIVE: "Đang hoạt động",
  FROZEN: "Đang bị khóa",
  CLOSED: "Đã đóng",
};

export function WalletBalanceCard() {
  const { data: wallet, isLoading, error } = useMyWallet();

  if (isLoading) return <Card className="text-muted-foreground">Đang tải ví...</Card>;
  if (error || !wallet)
    return <Card className="text-danger">Không thể tải thông tin ví.</Card>;

  return (
    <Card className="relative overflow-hidden bg-linear-to-br from-primary to-primary/80 text-primary-foreground">
      <div className="flex items-start justify-between">
        <div className="flex flex-col gap-1">
          <span className="text-sm text-primary-foreground/70">
            Số tài khoản
          </span>
          <span className="font-mono text-sm tracking-wide">
            {wallet.account_number}
          </span>
        </div>
        <span className="flex h-10 w-10 items-center justify-center rounded-full bg-white/15">
          <IconWallet className="h-5 w-5" />
        </span>
      </div>

      <div className="mt-6 flex flex-col gap-1">
        <span className="text-sm text-primary-foreground/70">Số dư khả dụng</span>
        <span className="text-4xl font-semibold tracking-tight">
          {Number(wallet.balance).toLocaleString("vi-VN")}{" "}
          <span className="text-lg font-normal text-primary-foreground/70">
            {wallet.currency}
          </span>
        </span>
      </div>

      <div className="mt-6">
        <Badge tone={STATUS_TONE[wallet.status]} className="bg-white/15 text-primary-foreground">
          {STATUS_LABEL[wallet.status]}
        </Badge>
      </div>
    </Card>
  );
}
