import { TransactionList } from "@/features/transactions/components/TransactionList";

export default function TransactionsPage() {
  return (
    <div className="w-full max-w-5xl">
      <h1 className="mb-6 text-xl font-semibold">Lịch sử giao dịch</h1>
      <TransactionList />
    </div>
  );
}
