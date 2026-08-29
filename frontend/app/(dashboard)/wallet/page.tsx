"use client";

import { useMemo, useState } from "react";
import Link from "next/link";
import { DashboardNav } from "../_components/DashboardNav";
import { useCurrentUser } from "@/features/auth/hooks";
import { useTransactionHistory } from "@/features/transactions/hooks";
import { useMyWallet } from "@/features/wallet/hooks";
import type { Transaction } from "@/types/models";

type Filter = "ALL" | "INCOMING" | "OUTGOING";

const money = (amount: string) => `\u20ab${Number(amount).toLocaleString("vi-VN")}`;
const incoming = (transaction: Transaction, walletId?: string) => transaction.txn_type === "DEPOSIT" || (transaction.txn_type === "TRANSFER" && transaction.to_wallet_id === walletId);
const name = (transaction: Transaction) => transaction.description || (transaction.txn_type === "DEPOSIT" ? "Deposit" : transaction.txn_type === "WITHDRAW" ? "Withdrawal" : "Transfer");
const detail = (transaction: Transaction) => {
  const type = transaction.txn_type === "DEPOSIT" ? "Bank transfer" : transaction.txn_type === "TRANSFER" ? "Transfer" : "Withdrawal";
  return `${type} \u00b7 ${new Date(transaction.created_at).toLocaleTimeString("vi-VN", { hour: "2-digit", minute: "2-digit" })}`;
};
const group = (timestamp: string) => {
  const date = new Date(timestamp);
  const today = new Date();
  const yesterday = new Date(today);
  yesterday.setDate(today.getDate() - 1);
  if (date.toDateString() === today.toDateString()) return "Today";
  if (date.toDateString() === yesterday.toDateString()) return "Yesterday";
  return "Earlier";
};

export default function WalletPage() {
  const [filter, setFilter] = useState<Filter>("ALL");
  const [selected, setSelected] = useState<Transaction | null>(null);
  const { data: wallet, isLoading: walletLoading } = useMyWallet();
  const { data: user } = useCurrentUser();
  const { data: history, isLoading: transactionsLoading } = useTransactionHistory({ limit: 12 });
  const walletNumber = wallet?.account_number ?? "";
  const maskedNumber = walletNumber ? `**** ${walletNumber.slice(-4)}` : "****";
  const visibleTransactions = useMemo(() => (history?.items ?? []).filter((transaction) => filter === "ALL" || (filter === "INCOMING" ? incoming(transaction, wallet?.wallet_id) : !incoming(transaction, wallet?.wallet_id))), [filter, history?.items, wallet?.wallet_id]);
  const groups = useMemo(() => ["Today", "Yesterday", "Earlier"].map((label) => [label, visibleTransactions.filter((transaction) => group(transaction.created_at) === label)] as const).filter(([, transactions]) => transactions.length), [visibleTransactions]);

  return (
    <div className="min-h-screen lg:grid lg:grid-cols-[2fr_3fr]">
      <section className="flex min-h-[48vh] flex-col bg-[#181a1e] px-7 py-8 text-white sm:px-10 lg:min-h-screen lg:px-12 lg:py-11 xl:px-16">
        <div className="flex items-center justify-between">
          <Link href="/wallet" className="text-[21px] font-semibold tracking-[-.055em]">MiniWallet</Link>
          <span className="font-mono text-xs tracking-[.13em] text-white/45">WALLET</span>
        </div>
        <div className="my-auto py-14 lg:py-0">
          <p className="text-xs font-semibold tracking-[.15em] text-white/52">AVAILABLE BALANCE</p>
          <h1 className="mt-5 text-[52px] font-semibold leading-none tracking-[-.075em] sm:text-[65px] xl:text-[76px]">
            {walletLoading || !wallet ? "—" : money(wallet.balance)}
          </h1>
          <p className="mt-7 font-mono text-base tracking-[.14em] text-white/80">{maskedNumber}</p>
          <p className="mt-4 text-sm text-[#7fa6ff]">+₫2,400,000 <span className="text-white/48">this month</span></p>
          <div className="mt-11 flex flex-wrap items-center gap-x-7 gap-y-4">
            <Link href="/transfer" className="text-base font-semibold text-white underline decoration-[#2463d8] decoration-2 underline-offset-8 hover:text-[#a9c3ff]">Send money →</Link>
            <Link href="/wallet/deposit" className="text-sm font-medium text-white/60 transition-colors hover:text-white">Add money</Link>
          </div>
        </div>
        <div className="flex items-end justify-between gap-5 border-t border-white/12 pt-6">
          <div><p className="text-sm font-medium">{user?.full_name ?? "Your wallet"}</p><p className="mt-1 text-xs text-white/43">ID · {wallet?.wallet_id.slice(0, 8).toUpperCase() ?? "—"}</p></div>
          <DashboardNav />
        </div>
      </section>

      <section className="bg-[#fcfcfa] px-7 py-9 sm:px-10 lg:px-12 lg:py-11 xl:px-16">
        <div className="mx-auto max-w-[680px]">
          <header className="flex flex-wrap items-end justify-between gap-5 border-b border-[#deded9] pb-6">
            <div><p className="text-xs font-semibold tracking-[.15em] text-[#747983]">WALLET HISTORY</p><h2 className="mt-2 text-[32px] font-semibold tracking-[-.05em] text-[#15171b]">Activity</h2></div>
            <div className="flex gap-4" role="tablist" aria-label="Transaction filter">
              {(["ALL", "INCOMING", "OUTGOING"] as const).map((item) => <button key={item} type="button" onClick={() => setFilter(item)} className={`border-b-2 pb-1 text-sm font-medium transition-colors ${filter === item ? "border-[#2463d8] text-[#2463d8]" : "border-transparent text-[#777c85] hover:text-[#17191d]"}`}>{item[0]}{item.slice(1).toLowerCase()}</button>)}
            </div>
          </header>
          <div className="mt-8">
            {transactionsLoading ? <p className="py-8 text-sm text-[#747983]">Loading transactions…</p> : groups.length ? groups.map(([title, transactions]) => <section key={title} className="mb-9 last:mb-0"><h3 className="border-b border-[#deded9] pb-3 text-xs font-semibold tracking-[.13em] text-[#747983]">{title.toUpperCase()}</h3>{transactions.map((transaction) => { const isIncoming = incoming(transaction, wallet?.wallet_id); return <button key={transaction.txn_id} type="button" onClick={() => setSelected(transaction)} className="flex w-full items-center justify-between gap-5 border-b border-[#e7e7e3] py-5 text-left transition-colors hover:bg-[#f6f6f3]"><span className="min-w-0"><span className="block truncate text-[15px] font-semibold text-[#1c2025]">{name(transaction)}</span><span className="mt-1 block text-sm text-[#747983]">{detail(transaction)} · {transaction.status === "SUCCESS" ? "Completed" : "Failed"}</span></span><span className={`shrink-0 text-[15px] font-semibold ${isIncoming ? "text-[#23734d]" : "text-[#343941]"}`}>{isIncoming ? "+" : "−"}{money(transaction.amount)}</span></button>; })}</section>) : <p className="py-8 text-sm text-[#747983]">No transactions match this filter.</p>}
          </div>
        </div>
      </section>

      {selected && <><button type="button" aria-label="Close transaction details" className="fixed inset-0 z-10 bg-black/20" onClick={() => setSelected(null)} /><aside className="fixed inset-y-0 right-0 z-20 flex w-full max-w-[390px] flex-col bg-white px-7 py-8 shadow-[-16px_0_40px_rgba(20,22,26,0.12)] sm:px-9"><div className="flex items-center justify-between border-b border-[#e2e2de] pb-5"><p className="text-lg font-semibold text-[#17191d]">Transaction details</p><button type="button" onClick={() => setSelected(null)} className="text-sm font-medium text-[#6e747d] hover:text-[#17191d]">Close</button></div><div className="py-8"><p className="text-sm text-[#747983]">{detail(selected)}</p><p className={`mt-3 text-3xl font-semibold tracking-[-.045em] ${incoming(selected, wallet?.wallet_id) ? "text-[#23734d]" : "text-[#1a1d22]"}`}>{incoming(selected, wallet?.wallet_id) ? "+" : "−"}{money(selected.amount)}</p><dl className="mt-10 space-y-5 text-sm"><div className="flex justify-between gap-5"><dt className="text-[#747983]">Name</dt><dd className="text-right font-medium text-[#20242a]">{name(selected)}</dd></div><div className="flex justify-between gap-5"><dt className="text-[#747983]">Status</dt><dd className="font-medium text-[#23734d]">{selected.status === "SUCCESS" ? "Completed" : "Failed"}</dd></div><div className="flex justify-between gap-5"><dt className="text-[#747983]">Reference</dt><dd className="font-mono text-xs text-[#20242a]">{selected.reference_code}</dd></div></dl></div></aside></>}
    </div>
  );
}
