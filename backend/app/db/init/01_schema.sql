USE ebanking;
GO

-- ── Users ────────────────────────────────────────────────
CREATE TABLE Users (
    user_id       UNIQUEIDENTIFIER  PRIMARY KEY DEFAULT NEWID(),
    full_name     NVARCHAR(100)     NOT NULL,
    email         VARCHAR(150)      NOT NULL UNIQUE,
    phone         VARCHAR(15)       NOT NULL UNIQUE,
    password_hash VARCHAR(255)      NOT NULL,
    is_active     BIT               NOT NULL DEFAULT 1,
    is_verified   BIT               NOT NULL DEFAULT 0,
    created_at    DATETIME2         NOT NULL DEFAULT GETDATE(),
    updated_at    DATETIME2         NOT NULL DEFAULT GETDATE()
);
GO

-- ═══════════════════════════════════════════════════════════
-- [FIX #3] Trigger tự cập nhật updated_at khi UPDATE Users.
-- SQL Server không có ON UPDATE CURRENT_TIMESTAMP như MySQL,
-- nên dùng trigger để DB tự lo, Python không phải nhớ set tay.
-- ═══════════════════════════════════════════════════════════
CREATE TRIGGER TR_Users_UpdatedAt
ON Users
AFTER UPDATE
AS
BEGIN
    SET NOCOUNT ON;
    -- Chỉ update nếu cột updated_at KHÔNG nằm trong câu UPDATE gốc
    -- (tránh vòng lặp và tránh ghi đè khi ai đó cố tình set updated_at)
    IF NOT UPDATE(updated_at)
    BEGIN
        UPDATE u
        SET u.updated_at = GETDATE()
        FROM Users u
        INNER JOIN inserted i ON u.user_id = i.user_id;
    END
END;
GO

-- ── RefreshTokens ─────────────────────────────────────────
CREATE TABLE RefreshTokens (
    token_id    UNIQUEIDENTIFIER  PRIMARY KEY DEFAULT NEWID(),
    user_id     UNIQUEIDENTIFIER  NOT NULL
                REFERENCES Users(user_id) ON DELETE CASCADE,
    session_id  UNIQUEIDENTIFIER  NOT NULL,
    family_id   UNIQUEIDENTIFIER  NOT NULL,
    token_hash  VARCHAR(64)       NOT NULL UNIQUE,
    device_name NVARCHAR(255)     NOT NULL DEFAULT 'Unknown device',
    ip_address  VARCHAR(45)       NULL,
    expires_at  DATETIME2         NOT NULL,
    revoked_at  DATETIME2         NULL,
    revoked_reason VARCHAR(20)     NULL,
    replaced_by_token_id UNIQUEIDENTIFIER NULL REFERENCES RefreshTokens(token_id),
    created_at  DATETIME2         NOT NULL DEFAULT GETUTCDATE(),
    last_used_at DATETIME2        NOT NULL DEFAULT GETUTCDATE()
);
GO

-- ── Wallets ───────────────────────────────────────────────
CREATE TABLE Wallets (
    wallet_id      UNIQUEIDENTIFIER  PRIMARY KEY DEFAULT NEWID(),
    user_id        UNIQUEIDENTIFIER  NOT NULL UNIQUE
                   REFERENCES Users(user_id),
    account_number VARCHAR(12)       NOT NULL UNIQUE,
    balance        DECIMAL(18,2)     NOT NULL DEFAULT 0.00
                   CONSTRAINT CHK_Balance_NonNegative CHECK (balance >= 0),
    currency       CHAR(3)           NOT NULL DEFAULT 'VND',
    status         VARCHAR(10)       NOT NULL DEFAULT 'ACTIVE'
                   CONSTRAINT CHK_Wallet_Status
                   CHECK (status IN ('ACTIVE','FROZEN','CLOSED')),
    created_at     DATETIME2         NOT NULL DEFAULT GETDATE(),
    updated_at     DATETIME2         NOT NULL DEFAULT GETDATE()
);
GO

CREATE TRIGGER TR_Wallets_UpdatedAt
ON Wallets
AFTER UPDATE
AS
BEGIN
    SET NOCOUNT ON;
    IF NOT UPDATE(updated_at)
    BEGIN
        UPDATE w
        SET w.updated_at = GETDATE()
        FROM Wallets w
        INNER JOIN inserted i ON w.wallet_id = i.wallet_id;
    END
END;
GO

-- ── Transactions ──────────────────────────────────────────
CREATE TABLE Transactions (
    txn_id               UNIQUEIDENTIFIER  PRIMARY KEY DEFAULT NEWID(),
    reference_code       VARCHAR(30)       NOT NULL UNIQUE,
    txn_type             VARCHAR(10)       NOT NULL
                         CONSTRAINT CHK_Txn_Type
                         CHECK (txn_type IN ('DEPOSIT','WITHDRAW','TRANSFER')),
    from_wallet_id       UNIQUEIDENTIFIER  NULL
                         REFERENCES Wallets(wallet_id),
    to_wallet_id         UNIQUEIDENTIFIER  NULL
                         REFERENCES Wallets(wallet_id),
    amount               DECIMAL(18,2)     NOT NULL
                         CONSTRAINT CHK_Txn_Amount CHECK (amount > 0),
    fee                  DECIMAL(18,2)     NOT NULL DEFAULT 0.00,
    from_balance_before  DECIMAL(18,2)     NULL,
    from_balance_after   DECIMAL(18,2)     NULL,
    to_balance_before    DECIMAL(18,2)     NULL,
    to_balance_after     DECIMAL(18,2)     NULL,
    status               VARCHAR(10)       NOT NULL DEFAULT 'SUCCESS'
                         CONSTRAINT CHK_Txn_Status
                         CHECK (status IN ('SUCCESS','FAILED')),
    description          NVARCHAR(255)     NULL,
    created_at           DATETIME2         NOT NULL DEFAULT GETDATE()
);
GO

-- ── Indexes ───────────────────────────────────────────────
CREATE INDEX IX_Txn_FromWallet ON Transactions(from_wallet_id, created_at DESC);
CREATE INDEX IX_Txn_ToWallet   ON Transactions(to_wallet_id,   created_at DESC);
CREATE INDEX IX_Txn_Type       ON Transactions(txn_type,       created_at DESC);
CREATE INDEX IX_RefToken_User  ON RefreshTokens(user_id);
GO

-- ── Idempotency keys ─────────────────────────────────────
-- Một key chỉ thuộc một user và trỏ tới giao dịch đã hoàn tất. Unique constraint
-- là hàng rào cuối cùng khi hai request giống nhau tới hai worker đồng thời.
CREATE TABLE IdempotencyKeys (
    idempotency_id  UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
    user_id         UNIQUEIDENTIFIER NOT NULL REFERENCES Users(user_id),
    [key]           VARCHAR(64) NOT NULL,
    operation       VARCHAR(20) NOT NULL,
    request_hash    CHAR(64) NOT NULL,
    status          VARCHAR(12) NOT NULL DEFAULT 'PROCESSING'
                    CONSTRAINT CHK_Idempotency_Status
                    CHECK (status IN ('PROCESSING', 'COMPLETED')),
    transaction_id UNIQUEIDENTIFIER NULL REFERENCES Transactions(txn_id),
    response_balance DECIMAL(18,2) NULL,
    created_at      DATETIME2 NOT NULL DEFAULT GETDATE(),
    CONSTRAINT UQ_Idempotency_User_Key UNIQUE (user_id, [key])
);
GO

CREATE INDEX IX_Idempotency_CreatedAt ON IdempotencyKeys(created_at);
GO

-- ═══════════════════════════════════════════════════════════
-- Stored Procedure: Transfer (bản đã fix)
-- CREATE OR ALTER: nếu DB đã tồn tại, chỉ cần chạy lại từ đây
-- trở xuống là được, không cần tạo lại bảng.
-- ═══════════════════════════════════════════════════════════
CREATE OR ALTER PROCEDURE sp_Transfer
    @from_wallet_id  UNIQUEIDENTIFIER,
    @to_wallet_id    UNIQUEIDENTIFIER,
    @amount          DECIMAL(18,2),
    @fee             DECIMAL(18,2) = 0.00,   -- [FIX #2] thêm tham số phí,
                                             -- mặc định 0 nên code cũ gọi SP
                                             -- không truyền fee vẫn chạy được
    @description     NVARCHAR(255),
    @reference_code  VARCHAR(30)
AS
BEGIN
    SET NOCOUNT ON;
    SET XACT_ABORT OFF;  -- [FIX #4] tắt XACT_ABORT để TRY/CATCH tự kiểm soát
                         -- rollback, sau đó còn INSERT được record FAILED

    DECLARE @from_bal_before DECIMAL(18,2);
    DECLARE @from_bal_after  DECIMAL(18,2);
    DECLARE @to_bal_before   DECIMAL(18,2);
    DECLARE @to_bal_after    DECIMAL(18,2);
    DECLARE @total_debit     DECIMAL(18,2) = @amount + @fee;  -- [FIX #2]
                                             -- người gửi bị trừ tiền + phí

    BEGIN TRY
        BEGIN TRANSACTION;

            -- ═══════════════════════════════════════════════
            -- [FIX #1] Chống deadlock: LUÔN lock ví theo thứ tự
            -- wallet_id tăng dần, bất kể ai là người gửi/nhận.
            -- Nhờ vậy 2 giao dịch A→B và B→A cùng lúc sẽ xếp
            -- hàng chờ nhau thay vì khóa chéo lẫn nhau.
            -- ═══════════════════════════════════════════════
            IF @from_wallet_id < @to_wallet_id
            BEGIN
                -- Lock ví gửi trước (ID nhỏ hơn)
                SELECT @from_bal_before = balance
                FROM Wallets WITH (UPDLOCK, ROWLOCK)
                WHERE wallet_id = @from_wallet_id AND status = 'ACTIVE';

                SELECT @to_bal_before = balance
                FROM Wallets WITH (UPDLOCK, ROWLOCK)
                WHERE wallet_id = @to_wallet_id AND status = 'ACTIVE';
            END
            ELSE
            BEGIN
                -- Lock ví nhận trước (ID nhỏ hơn)
                SELECT @to_bal_before = balance
                FROM Wallets WITH (UPDLOCK, ROWLOCK)
                WHERE wallet_id = @to_wallet_id AND status = 'ACTIVE';

                SELECT @from_bal_before = balance
                FROM Wallets WITH (UPDLOCK, ROWLOCK)
                WHERE wallet_id = @from_wallet_id AND status = 'ACTIVE';
            END

            -- ── Validate (sau khi đã lock xong cả 2 ví) ──
            IF @from_bal_before IS NULL
                THROW 50001, 'SOURCE_WALLET_UNAVAILABLE', 1;
                -- Ví gửi không tồn tại hoặc FROZEN/CLOSED

            IF @to_bal_before IS NULL
                THROW 50002, 'DEST_WALLET_UNAVAILABLE', 1;
                -- Ví nhận không tồn tại hoặc FROZEN/CLOSED

            IF @from_bal_before < @total_debit
                THROW 50003, 'INSUFFICIENT_BALANCE', 1;
                -- [FIX #2] so với amount + fee chứ không chỉ amount

            -- ── Tính toán và cập nhật ──
            SET @from_bal_after = @from_bal_before - @total_debit;  -- [FIX #2]
            SET @to_bal_after   = @to_bal_before   + @amount;
            -- Người nhận chỉ nhận @amount, phí không chuyển cho họ

            UPDATE Wallets SET balance = @from_bal_after
            WHERE wallet_id = @from_wallet_id;

            UPDATE Wallets SET balance = @to_bal_after
            WHERE wallet_id = @to_wallet_id;

            INSERT INTO Transactions (
                reference_code, txn_type,
                from_wallet_id, to_wallet_id,
                amount, fee,                              -- [FIX #2] ghi fee
                from_balance_before, from_balance_after,
                to_balance_before,   to_balance_after,
                status, description
            ) VALUES (
                @reference_code, 'TRANSFER',
                @from_wallet_id, @to_wallet_id,
                @amount, @fee,
                @from_bal_before, @from_bal_after,
                @to_bal_before,   @to_bal_after,
                'SUCCESS', @description
            );

        COMMIT;

        SELECT 'SUCCESS' AS result, @from_bal_after AS new_balance;
    END TRY
    BEGIN CATCH
        -- ═══════════════════════════════════════════════════
        -- [FIX #4] Ghi lại giao dịch FAILED để thống kê/audit.
        -- Phải ROLLBACK trước rồi mới INSERT, vì nếu insert bên
        -- trong transaction thì rollback sẽ xóa luôn record này.
        -- INSERT sau rollback chạy ở chế độ autocommit riêng.
        -- ═══════════════════════════════════════════════════
        IF @@TRANCOUNT > 0
            ROLLBACK;

        DECLARE @err_msg NVARCHAR(255) = ERROR_MESSAGE();
        DECLARE @err_num INT           = ERROR_NUMBER();

        INSERT INTO Transactions (
            reference_code, txn_type,
            from_wallet_id, to_wallet_id,
            amount, fee,
            from_balance_before,  -- balance lúc check (có thể NULL nếu
            to_balance_before,    -- lỗi xảy ra trước khi kịp đọc)
            status, description
        ) VALUES (
            @reference_code, 'TRANSFER',
            @from_wallet_id, @to_wallet_id,
            @amount, @fee,
            @from_bal_before,
            @to_bal_before,
            'FAILED', @err_msg    -- lưu lý do fail vào description
        );

        -- Ném lại lỗi gốc cho tầng Python (pyodbc) nhận được,
        -- repository sẽ dịch mã lỗi 50001/50002/50003 thành
        -- exception nghiệp vụ tương ứng
        THROW;
    END CATCH
END;
GO
