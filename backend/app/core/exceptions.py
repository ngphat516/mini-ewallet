# app/core/exceptions.py
from fastapi import Request
from fastapi.responses import JSONResponse


class AppException(Exception):
    """Exception gốc — mọi lỗi nghiệp vụ đều kế thừa từ đây"""
    status_code: int = 400
    error_code: str = "APP_ERROR"
    message: str = "Đã xảy ra lỗi"

    def __init__(self, message: str | None = None):
        if message:
            self.message = message
        super().__init__(self.message)


# ── Lỗi xác thực ──────────────────────────────
class UnauthorizedException(AppException):
    status_code = 401
    error_code = "UNAUTHORIZED"
    message = "Chưa xác thực hoặc token không hợp lệ"


class InvalidCredentialsException(AppException):
    status_code = 401
    error_code = "INVALID_CREDENTIALS"
    message = "Email hoặc mật khẩu không đúng"


# ── Lỗi nghiệp vụ user ────────────────────────
class UserAlreadyExistsException(AppException):
    status_code = 409
    error_code = "USER_EXISTS"
    message = "Email đã được đăng ký"


class UserNotVerifiedException(AppException):
    status_code = 403
    error_code = "USER_NOT_VERIFIED"
    message = "Tài khoản chưa được xác minh"


class UserInactiveException(AppException):
    status_code = 403
    error_code = "USER_INACTIVE"
    message = "Tài khoản đã bị vô hiệu hóa"


# ── Lỗi nghiệp vụ ví ──────────────────────────
class WalletNotFoundException(AppException):
    status_code = 404
    error_code = "WALLET_NOT_FOUND"
    message = "Không tìm thấy ví"


class WalletFrozenException(AppException):
    status_code = 400
    error_code = "WALLET_FROZEN"
    message = "Ví đang bị khóa hoặc đã đóng"


class InsufficientBalanceException(AppException):
    status_code = 400
    error_code = "INSUFFICIENT_BALANCE"
    message = "Số dư không đủ để thực hiện giao dịch"


# ── Lỗi nghiệp vụ giao dịch / chuyển tiền ─────
# (khớp với lỗi 50001/50002/50003 do stored procedure sp_Transfer THROW ra)
class TransactionNotFoundException(AppException):
    status_code = 404
    error_code = "TRANSACTION_NOT_FOUND"
    message = "Không tìm thấy giao dịch"


class RecipientWalletNotFoundException(AppException):
    status_code = 404
    error_code = "RECIPIENT_WALLET_NOT_FOUND"
    message = "Số tài khoản người nhận không tồn tại"


class RecipientWalletFrozenException(AppException):
    status_code = 400
    error_code = "RECIPIENT_WALLET_FROZEN"
    message = "Ví người nhận đang bị khóa hoặc đã đóng"


class SameWalletTransferException(AppException):
    status_code = 400
    error_code = "SAME_WALLET_TRANSFER"
    message = "Không thể chuyển tiền đến chính ví của bạn"


# ── Handler: chuyển exception thành JSON response ──
async def app_exception_handler(request: Request, exc: AppException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error_code": exc.error_code,
            "message": exc.message,
        },
    )