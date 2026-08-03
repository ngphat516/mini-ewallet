"use client";

import { Card } from "@/components/ui/Card";
import { Badge } from "@/components/ui/Badge";
import { useTransaction } from "../hooks";
import { TXN_TYPE_ICON, TXN_TYPE_LABEL } from "../constants";

export function TransactionDetail({ id }: { id: string }) {
  const { data: txn, isLoading, error } = useTransaction(id);

  if (isLoading) return <Card className="text-muted-foreground">Đang tải giao dịch...</Card>;
  if (error || !txn) return <Card className="text-danger">Không tìm thấy giao dịch.</Card>;

  const Icon = TXN_TYPE_ICON[txn.txn_type];
  const rows: [string, string][] = [
    ["Mã tham chiếu", txn.reference_code],
    ["Phí", `${Number(txn.fee).toLocaleString("vi-VN")} VND`],
    ["Nội dung", txn.description ?? "—"],
    ["Thời gian", new Date(txn.created_at).toLocaleString("vi-VN")],
  ];

  return (
    <Card className="flex flex-col gap-6">
      <div className="flex items-center gap-4">
        <span className="flex h-12 w-12 shrink-0 items-center justify-center rounded-full bg-primary/10 text-primary">
          <Icon className="h-6 w-6" />
        </span>
        <div className="flex flex-col gap-1">
          <span className="font-semibold">{TXN_TYPE_LABEL[txn.txn_type]}</span>
          <Badge tone={txn.status === "SUCCESS" ? "success" : "danger"}>
            {txn.status}
          </Badge>
        </div>
        <span className="ml-auto text-2xl font-semibold">
          {Number(txn.amount).toLocaleString("vi-VN")}{" "}
          <span className="text-sm font-normal text-muted-foreground">VND</span>
        </span>
      </div>

      <div className="flex flex-col divide-y divide-border border-t border-border">
        {rows.map(([label, value]) => (
          <div key={label} className="flex justify-between gap-4 py-2.5">
            <span className="text-muted-foreground">{label}</span>
            <span className="font-medium">{value}</span>
          </div>
        ))}
      </div>
    </Card>
  );
}
