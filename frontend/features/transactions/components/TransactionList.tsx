"use client";

import Link from "next/link";
import { Badge } from "@/components/ui/Badge";
import { useMyWallet } from "@/features/wallet/hooks";
import type { Transaction } from "@/types/models";
import { useTransactionHistory } from "../hooks";
import { TXN_TYPE_ICON, TXN_TYPE_LABEL } from "../constants";

function isIncoming(txn: Transaction, myWalletId?: string) {
  if (txn.txn_type === "DEPOSIT") return true;
  if (txn.txn_type === "WITHDRAW") return false;
  return txn.to_wallet_id === myWalletId;
}

export function TransactionList() {
  const { data: wallet } = useMyWallet();
  const { data, isLoading, error } = useTransactionHistory({ limit: 20 });

  if (isLoading) return <p className="text-muted-foreground">Đang tải lịch sử giao dịch...</p>;
  if (error || !data) return <p className="text-danger">Không thể tải lịch sử giao dịch.</p>;
  if (data.items.length === 0)
    return <p className="text-muted-foreground">Chưa có giao dịch nào.</p>;

  return (
    <ul className="flex flex-col overflow-hidden rounded-xl border border-border bg-card">
      {data.items.map((txn) => {
        const Icon = TXN_TYPE_ICON[txn.txn_type];
        const incoming = isIncoming(txn, wallet?.wallet_id);
        return (
          <li key={txn.txn_id} className="border-b border-border last:border-b-0">
            <Link
              href={`/transactions/${txn.txn_id}`}
              className="grid grid-cols-[auto_1fr_auto_auto] items-center gap-6 px-6 py-4 transition-colors hover:bg-muted"
            >
              <span
                className={`flex h-11 w-11 shrink-0 items-center justify-center rounded-full ${
                  incoming ? "bg-success/10 text-success" : "bg-danger/10 text-danger"
                }`}
              >
                <Icon className="h-5 w-5" />
              </span>

              <div className="flex min-w-0 flex-col items-start gap-1">
                <Badge tone="neutral" className="w-fit">
                  {TXN_TYPE_LABEL[txn.txn_type]}
                </Badge>
                <span className="truncate text-sm text-muted-foreground">
                  {txn.description || txn.reference_code}
                </span>
              </div>

              <span className="whitespace-nowrap text-sm text-muted-foreground">
                {new Date(txn.created_at).toLocaleString("vi-VN")}
              </span>

              <div className="flex flex-col items-end gap-1">
                <span className={`font-semibold ${incoming ? "text-success" : "text-danger"}`}>
                  {incoming ? "+" : "-"}
                  {Number(txn.amount).toLocaleString("vi-VN")}
                </span>
                <Badge tone={txn.status === "SUCCESS" ? "success" : "danger"}>
                  {txn.status}
                </Badge>
              </div>
            </Link>
          </li>
        );
      })}
    </ul>
  );
}
