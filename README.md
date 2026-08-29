# Mini E-Wallet

Đây là project cá nhân mình làm để học và thực hành **backend development**.

Ứng dụng mô phỏng một ví điện tử nhỏ: người dùng có thể đăng ký, đăng nhập, quản lý ví, nạp tiền, chuyển tiền và xem lịch sử giao dịch. Frontend chỉ đóng vai trò giao diện để gọi và kiểm tra API; trọng tâm chính của project là thiết kế, triển khai và kiểm thử backend.

## Những nội dung backend đã thực hành

- Xây dựng REST API với FastAPI và Python.
- Xác thực bằng access token và refresh token.
- Phân quyền/trạng thái tài khoản: tài khoản bị vô hiệu hóa không thể tiếp tục dùng token.
- Quản lý ví và giao dịch nạp, rút, chuyển tiền.
- Xử lý đồng thời khi chuyển tiền bằng transaction và row lock trên SQL Server.
- Idempotency để tránh xử lý trùng một yêu cầu giao dịch.
- Audit log cho các giao dịch thất bại.
- Health check/readiness check cho SQL Server, MongoDB và Redis.
- Quản lý schema database bằng các script migration chạy khi khởi tạo.
- Viết test cho các luồng và cấu hình quan trọng.
- Đóng gói môi trường phát triển bằng Docker Compose.

## Công nghệ

- Backend: Python, FastAPI, SQLAlchemy
- Database: SQL Server, MongoDB, Redis
- Frontend: Next.js, TypeScript, Tailwind CSS
- Infrastructure: Docker, Docker Compose

## Chạy project

Yêu cầu: Docker Desktop đang chạy.

```powershell
cd backend
docker compose up --build
```

Sau khi chạy:

- Backend API: `http://localhost:8000`
- API health check: `http://localhost:8000/health`
- Frontend: `http://localhost:3000`

## Lưu ý

Project phục vụ mục đích học tập. Đây không phải sản phẩm ví điện tử sẵn sàng cho production; các yêu cầu về bảo mật, tuân thủ pháp lý, giám sát và vận hành thực tế cần được mở rộng thêm trước khi sử dụng thật.
