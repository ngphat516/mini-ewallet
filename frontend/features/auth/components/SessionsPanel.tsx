"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useRouter } from "next/navigation";
import { Card } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";
import { clearTokens } from "@/lib/auth-token";
import { getSessions, logoutAllRequest, revokeSession } from "../api";

const sessionsKey = ["auth", "sessions"] as const;

export function SessionsPanel() {
  const queryClient = useQueryClient();
  const router = useRouter();
  const sessions = useQuery({ queryKey: sessionsKey, queryFn: getSessions });
  const revoke = useMutation({ mutationFn: revokeSession, onSuccess: () => queryClient.invalidateQueries({ queryKey: sessionsKey }) });
  const logoutAll = useMutation({
    mutationFn: logoutAllRequest,
    onSuccess: () => { clearTokens(); queryClient.clear(); router.push("/login"); },
  });

  return <div className="space-y-6">
    <div className="flex flex-wrap items-start justify-between gap-4">
      <div><h1 className="text-2xl font-bold">Security</h1><p className="mt-1 text-sm text-muted-foreground">Các thiết bị đang đăng nhập vào tài khoản của bạn.</p></div>
      <Button variant="danger" isLoading={logoutAll.isPending} onClick={() => logoutAll.mutate()}>Đăng xuất tất cả</Button>
    </div>
    {sessions.isLoading && <p className="text-muted-foreground">Đang tải phiên...</p>}
    {sessions.isError && <p className="text-danger">Không thể tải danh sách phiên.</p>}
    <div className="grid gap-4">{sessions.data?.map((session) => <Card key={session.session_id} className="flex flex-wrap items-center justify-between gap-4">
      <div className="min-w-0"><h2 className="truncate font-semibold">{session.device_name}</h2>
        <p className="mt-1 text-sm text-muted-foreground">IP: {session.ip_address ?? "Không rõ"} · Hoạt động: {new Date(session.last_used_at).toLocaleString("vi-VN")}</p>
        <p className="mt-1 text-xs text-muted-foreground">Tạo {new Date(session.created_at).toLocaleString("vi-VN")} · Hết hạn {new Date(session.expires_at).toLocaleString("vi-VN")}</p>
      </div>
      <Button variant="danger" isLoading={revoke.isPending && revoke.variables === session.session_id} onClick={() => revoke.mutate(session.session_id)}>Revoke</Button>
    </Card>)}</div>
  </div>;
}
