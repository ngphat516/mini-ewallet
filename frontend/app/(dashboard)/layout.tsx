import { DashboardNav } from "./_components/DashboardNav";

// Việc chặn truy cập khi chưa đăng nhập nằm ở proxy.ts (chạy trước khi tới đây).
export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div className="flex flex-1">
      <DashboardNav />
      <main className="flex flex-1 flex-col items-center gap-6 bg-background p-8">{children}</main>
    </div>
  );
}
