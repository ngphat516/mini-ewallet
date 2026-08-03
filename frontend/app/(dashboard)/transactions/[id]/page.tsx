import { TransactionDetail } from "@/features/transactions/components/TransactionDetail";

export default async function TransactionDetailPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;
  return (
    <div className="max-w-md">
      <TransactionDetail id={id} />
    </div>
  );
}
