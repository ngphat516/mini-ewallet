"use client";

import { useCurrentUser } from "../hooks";

export function UserInfo() {
  const { data: user, isLoading } = useCurrentUser();

  if (isLoading || !user) {
    return (
      <div className="flex items-center gap-3 px-3 py-2">
        <span className="h-9 w-9 shrink-0 animate-pulse rounded-full bg-muted" />
        <div className="flex flex-1 flex-col gap-1.5">
          <span className="h-3 w-24 animate-pulse rounded bg-muted" />
          <span className="h-3 w-32 animate-pulse rounded bg-muted" />
        </div>
      </div>
    );
  }

  const initial = user.full_name.trim().charAt(0).toUpperCase();

  return (
    <div className="flex items-center gap-3 px-3 py-2">
      <span className="flex h-9 w-9 shrink-0 items-center justify-center rounded-full bg-primary/10 text-sm font-semibold text-primary">
        {initial}
      </span>
      <div className="flex min-w-0 flex-col">
        <span className="truncate text-sm font-medium">{user.full_name}</span>
        <span className="truncate text-xs text-muted-foreground">{user.email}</span>
      </div>
    </div>
  );
}
