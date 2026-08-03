import Link from "next/link";
import { IconWallet } from "@/components/ui/icons";

export default function Home() {
  return (
    <div className="flex flex-1 flex-col items-center justify-center gap-6 bg-linear-to-b from-primary/5 to-background p-8 text-center">
      <span className="flex h-14 w-14 items-center justify-center rounded-2xl bg-primary text-primary-foreground shadow-sm">
        <IconWallet className="h-7 w-7" />
      </span>
      <h1 className="text-3xl font-semibold tracking-tight">Mini E-Wallet</h1>
      <p className="max-w-md text-muted-foreground">
        Nạp tiền, rút tiền và chuyển khoản trong vài giây.
      </p>
      <div className="flex gap-4">
        <Link
          href="/login"
          className="flex h-11 items-center rounded-lg bg-primary px-5 font-medium text-primary-foreground shadow-sm transition-colors hover:bg-primary/90"
        >
          Đăng nhập
        </Link>
        <Link
          href="/register"
          className="flex h-11 items-center rounded-lg border border-border bg-card px-5 font-medium transition-colors hover:bg-muted"
        >
          Đăng ký
        </Link>
      </div>
    </div>
  );
}
