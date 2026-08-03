"use client";

import Link from "next/link";
import { useForm } from "react-hook-form";
import { Button } from "@/components/ui/Button";
import { Input } from "@/components/ui/Input";
import { ApiError } from "@/lib/http-error";
import { useRegister } from "../hooks";
import { registerSchema, type RegisterInput } from "../schemas";

export function RegisterForm() {
  const {
    register,
    handleSubmit,
    setError,
    formState: { errors },
  } = useForm<RegisterInput>();
  const { mutate, isPending, error } = useRegister();

  const onSubmit = (data: RegisterInput) => {
    const parsed = registerSchema.safeParse(data);
    if (!parsed.success) {
      for (const issue of parsed.error.issues) {
        setError(issue.path[0] as keyof RegisterInput, { message: issue.message });
      }
      return;
    }
    mutate(parsed.data);
  };

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="flex flex-col gap-4">
      <Input label="Họ và tên" {...register("full_name")} error={errors.full_name?.message} />
      <Input label="Email" type="email" {...register("email")} error={errors.email?.message} />
      <Input label="Số điện thoại" {...register("phone")} error={errors.phone?.message} />
      <Input
        label="Mật khẩu"
        type="password"
        {...register("password")}
        error={errors.password?.message}
      />
      {error instanceof ApiError && (
        <p className="rounded-lg bg-danger/10 px-3 py-2 text-sm text-danger">{error.message}</p>
      )}
      <Button type="submit" isLoading={isPending}>
        Đăng ký
      </Button>
      <p className="text-center text-sm text-muted-foreground">
        Đã có tài khoản?{" "}
        <Link href="/login" className="font-medium text-primary hover:underline">
          Đăng nhập
        </Link>
      </p>
    </form>
  );
}
