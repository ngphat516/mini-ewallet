import { z } from "zod";

// Khớp validation trong backend/app/schemas/user.py (RegisterRequest)
export const registerSchema = z.object({
  full_name: z.string().min(2, "Tối thiểu 2 ký tự").max(100),
  email: z.string().email("Email không hợp lệ"),
  phone: z
    .string()
    .min(9, "Tối thiểu 9 số")
    .max(15)
    .regex(/^\d+$/, "Số điện thoại chỉ được chứa chữ số"),
  password: z
    .string()
    .min(8, "Tối thiểu 8 ký tự")
    .max(72)
    .regex(/\d/, "Mật khẩu phải chứa ít nhất 1 chữ số"),
});
export type RegisterInput = z.infer<typeof registerSchema>;

// Khớp LoginRequest
export const loginSchema = z.object({
  email: z.string().email("Email không hợp lệ"),
  password: z.string().min(1, "Vui lòng nhập mật khẩu"),
});
export type LoginInput = z.infer<typeof loginSchema>;
