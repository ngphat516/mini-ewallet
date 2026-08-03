import { create } from "zustand";

// Chỉ giữ trạng thái đăng nhập ở đây; thông tin User đầy đủ lấy qua
// useCurrentUser() (react-query, gọi GET /auth/me) thay vì lưu trong store.
interface AuthState {
  isAuthenticated: boolean;
  setAuthenticated: (value: boolean) => void;
}

export const useAuthStore = create<AuthState>((set) => ({
  isAuthenticated: false,
  setAuthenticated: (value) => set({ isAuthenticated: value }),
}));
