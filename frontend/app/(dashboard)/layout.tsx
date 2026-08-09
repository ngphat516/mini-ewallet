import { DashboardNav } from "./_components/DashboardNav";

// Việc chặn truy cập khi chưa đăng nhập nằm ở proxy.ts (chạy trước khi tới đây).
export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div className="flex min-h-screen flex-1 flex-col">
      <DashboardNav />
      <main className="flex flex-1 flex-col bg-background">
        <div className="mx-auto w-full max-w-7xl flex-1 px-4 py-8 sm:px-6 lg:px-8 lg:py-10">
          {children}
        </div>
      </main>
    </div>
  );
}
