"use client";

import { useForm } from "react-hook-form";
import { Button } from "@/components/ui/Button";
import { Input } from "@/components/ui/Input";
import { IconSend } from "@/components/ui/icons";
import { ApiError } from "@/lib/http-error";
import { useTransfer } from "../hooks";
import { transferSchema, type TransferInput } from "../schemas";

export function TransferForm() {
  const { register, handleSubmit, setError, reset, formState: { errors } } =
    useForm<TransferInput>();
  const { mutate, isPending, isSuccess, error } = useTransfer();

  const onSubmit = (data: TransferInput) => {
    const parsed = transferSchema.safeParse(data);
    if (!parsed.success) {
      for (const issue of parsed.error.issues) {
        setError(issue.path[0] as keyof TransferInput, { message: issue.message });
      }
      return;
    }
    mutate(parsed.data, { onSuccess: () => reset() });
  };

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="flex flex-col gap-4">
      <div className="flex items-center gap-3">
        <span className="flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-primary/10 text-primary">
          <IconSend className="h-5 w-5" />
        </span>
        <p className="text-sm text-muted-foreground">
          Chuyển tiền tức thời tới số tài khoản 12 số.
        </p>
      </div>
      <Input
        label="Số tài khoản người nhận"
        placeholder="VD: 804076490710"
        {...register("to_account_number")}
        error={errors.to_account_number?.message}
      />
      <Input
        label="Số tiền"
        type="number"
        step="0.01"
        placeholder="0"
        {...register("amount")}
        error={errors.amount?.message}
      />
      <Input
        label="Nội dung (không bắt buộc)"
        placeholder="VD: Trả tiền ăn trưa"
        {...register("description")}
        error={errors.description?.message}
      />
      {error instanceof ApiError && <p className="text-sm text-danger">{error.message}</p>}
      {isSuccess && !isPending && (
        <p className="rounded-lg bg-success/10 px-3 py-2 text-sm text-success">
          Chuyển tiền thành công.
        </p>
      )}
      <Button type="submit" isLoading={isPending}>
        Chuyển tiền
      </Button>
    </form>
  );
}
