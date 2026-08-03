import { IconWallet } from "@/components/ui/icons";

export default function AuthLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div className="flex flex-1 items-center justify-center bg-linear-to-b from-primary/5 to-background p-8">
      <div className="flex w-full max-w-sm flex-col gap-6">
        <div className="flex flex-col items-center gap-2 text-center">
          <span className="flex h-12 w-12 items-center justify-center rounded-xl bg-primary text-primary-foreground shadow-sm">
            <IconWallet className="h-6 w-6" />
          </span>
          <span className="font-semibold tracking-tight">Mini E-Wallet</span>
        </div>
        {children}
      </div>
    </div>
  );
}
