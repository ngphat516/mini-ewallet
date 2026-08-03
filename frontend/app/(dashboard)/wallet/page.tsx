import { WalletBalanceCard } from "@/features/wallet/components/WalletBalanceCard";

export default function WalletPage() {
  return (
    <div className="flex flex-col gap-6 max-w-md">
      <h1 className="text-xl font-semibold">Tổng quan ví</h1>
      <WalletBalanceCard />
    </div>
  );
}
