import { DepositForm } from "@/features/wallet/components/DepositForm";
import { Card } from "@/components/ui/Card";

export default function DepositPage() {
  return (
    <div className="max-w-md">
      <h1 className="mb-6 text-xl font-semibold">Nạp tiền</h1>
      <Card>
        <DepositForm />
      </Card>
    </div>
  );
}
