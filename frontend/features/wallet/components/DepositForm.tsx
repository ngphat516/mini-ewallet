"use client";

import { useState } from "react";
import { useForm } from "react-hook-form";
import { Button } from "@/components/ui/Button";
import { Input } from "@/components/ui/Input";
import { IconArrowDownCircle } from "@/components/ui/icons";
import { ApiError } from "@/lib/http-error";
import { useDeposit } from "../hooks";
import { amountSchema, type AmountInput } from "../schemas";

export function DepositForm() {
  const [idempotencyKey, setIdempotencyKey] = useState(() => crypto.randomUUID());
  const { register, handleSubmit, setError, reset, formState: { errors } } =
    useForm<AmountInput>();
  const { mutate, isPending, error } = useDeposit();

  const onSubmit = (data: AmountInput) => {
    const parsed = amountSchema.safeParse(data);
    if (!parsed.success) {
      setError("amount", { message: parsed.error.issues[0].message });
      return;
    }
    mutate(
      { data: parsed.data, idempotencyKey },
      {
        onSuccess: () => {
          setIdempotencyKey(crypto.randomUUID());
          reset();
        },
      },
    );
  };

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="flex flex-col gap-4">
      <div className="flex items-center gap-3">
        <span className="flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-success/10 text-success">
          <IconArrowDownCircle className="h-5 w-5" />
        </span>
        <p className="text-sm text-muted-foreground">
          Số tiền sẽ được cộng ngay vào số dư khả dụng.
        </p>
      </div>
      <Input
        label="Số tiền nạp"
        type="number"
        step="0.01"
        placeholder="0"
        {...register("amount")}
        error={errors.amount?.message}
      />
      {error instanceof ApiError && <p className="text-sm text-danger">{error.message}</p>}
      <Button type="submit" variant="success" isLoading={isPending}>
        Nạp tiền
      </Button>
    </form>
  );
}
