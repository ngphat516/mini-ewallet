import { RegisterForm } from "@/features/auth/components/RegisterForm";
import { Card } from "@/components/ui/Card";

export default function RegisterPage() {
  return (
    <Card className="flex flex-col gap-6">
      <h1 className="text-xl font-semibold">Đăng ký</h1>
      <RegisterForm />
    </Card>
  );
}
