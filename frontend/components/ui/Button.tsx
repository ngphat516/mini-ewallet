import { ButtonHTMLAttributes } from "react";

type ButtonVariant = "primary" | "success" | "danger";

const VARIANT_CLASSES: Record<ButtonVariant, string> = {
  primary: "bg-primary text-primary-foreground hover:bg-primary/90",
  success: "bg-success text-success-foreground hover:bg-success/90",
  danger: "bg-danger text-danger-foreground hover:bg-danger/90",
};

type ButtonProps = ButtonHTMLAttributes<HTMLButtonElement> & {
  isLoading?: boolean;
  variant?: ButtonVariant;
};

export function Button({
  isLoading,
  variant = "primary",
  disabled,
  className = "",
  children,
  ...props
}: ButtonProps) {
  return (
    <button
      disabled={disabled || isLoading}
      className={`inline-flex h-11 items-center justify-center gap-2 rounded-lg px-5 font-medium shadow-sm transition-colors disabled:cursor-not-allowed disabled:opacity-50 ${VARIANT_CLASSES[variant]} ${className}`}
      {...props}
    >
      {isLoading ? "Đang xử lý..." : children}
    </button>
  );
}
