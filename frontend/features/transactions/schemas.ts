import { z } from "zod";

// Khớp backend/app/schemas/transaction.py (TransferRequest)
export const transferSchema = z.object({
  to_account_number: z
    .string()
    .length(12, "Số tài khoản phải đủ 12 số")
    .regex(/^\d+$/, "Số tài khoản chỉ được chứa chữ số"),
  amount: z.coerce.number().positive("Số tiền phải lớn hơn 0"),
  description: z.string().max(255).optional(),
});
export type TransferInput = z.infer<typeof transferSchema>;
