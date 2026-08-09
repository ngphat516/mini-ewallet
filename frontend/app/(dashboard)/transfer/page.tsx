import { TransferForm } from "@/features/transactions/components/TransferForm";
import { Card } from "@/components/ui/Card";

export default function TransferPage() {
  return (
    <div className="w-full max-w-md">
      <h1 className="mb-6 text-xl font-semibold">Chuyển tiền</h1>
      <Card>
        <TransferForm />
      </Card>
    </div>
  );
}
