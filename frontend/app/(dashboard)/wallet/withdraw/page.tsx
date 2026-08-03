import { WithdrawForm } from "@/features/wallet/components/WithdrawForm";
import { Card } from "@/components/ui/Card";

export default function WithdrawPage() {
  return (
    <div className="max-w-md">
      <h1 className="mb-6 text-xl font-semibold">Rút tiền</h1>
      <Card>
        <WithdrawForm />
      </Card>
    </div>
  );
}
