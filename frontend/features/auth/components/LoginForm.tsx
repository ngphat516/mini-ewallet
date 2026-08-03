"use client";

import Link from "next/link";
import { useForm } from "react-hook-form";
import { Button } from "@/components/ui/Button";
import { Input } from "@/components/ui/Input";
import { ApiError } from "@/lib/http-error";
import { useLogin } from "../hooks";
import { loginSchema, type LoginInput } from "../schemas";

export function LoginForm() {
  const {
    register,
    handleSubmit,
    setError,
    formState: { errors },
  } = useForm<LoginInput>();
  const { mutate, isPending, error } = useLogin();

  const onSubmit = (data: LoginInput) => {
    const parsed = loginSchema.safeParse(data);
    if (!parsed.success) {
      for (const issue of parsed.error.issues) {
        setError(issue.path[0] as keyof LoginInput, { message: issue.message });
      }
      return;
    }
    mutate(parsed.data);
  };

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="flex flex-col gap-4">
      <Input label="Email" type="email" {...register("email")} error={errors.email?.message} />
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
        Đăng nhập
      </Button>
      <p className="text-center text-sm text-muted-foreground">
        Chưa có tài khoản?{" "}
        <Link href="/register" className="font-medium text-primary hover:underline">
          Đăng ký
        </Link>
      </p>
    </form>
  );
}
