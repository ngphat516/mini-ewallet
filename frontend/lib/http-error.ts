import { AxiosError } from "axios";

export interface ApiErrorBody {
  success: false;
  error_code: string;
  message: string;
}

export class ApiError extends Error {
  status: number;
  errorCode: string;

  constructor(status: number, body: ApiErrorBody) {
    super(body.message);
    this.status = status;
    this.errorCode = body.error_code;
  }
}

export function normalizeError(error: unknown): ApiError {
  if (error instanceof AxiosError && error.response) {
    const body = error.response.data as Partial<ApiErrorBody>;
    return new ApiError(error.response.status, {
      success: false,
      error_code: body.error_code ?? "UNKNOWN_ERROR",
      message: body.message ?? "Đã xảy ra lỗi không xác định",
    });
  }
  return new ApiError(0, {
    success: false,
    error_code: "NETWORK_ERROR",
    message: "Không thể kết nối tới máy chủ",
  });
}
