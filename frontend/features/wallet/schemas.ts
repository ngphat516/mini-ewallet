import { z } from "zod";

// Khớp backend/app/schemas/wallet.py (DepositRequest / WithdrawRequest)
export const amountSchema = z.object({
  amount: z.coerce.number().positive("Số tiền phải lớn hơn 0"),
});
export type AmountInput = z.infer<typeof amountSchema>;
