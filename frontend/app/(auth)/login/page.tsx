import { LoginForm } from "@/features/auth/components/LoginForm";
import { Card } from "@/components/ui/Card";

export default function LoginPage() {
  return (
    <Card className="flex flex-col gap-6">
      <h1 className="text-xl font-semibold">Đăng nhập</h1>
      <LoginForm />
    </Card>
  );
}
