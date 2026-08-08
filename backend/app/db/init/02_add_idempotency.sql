USE ebanking;
GO

-- Migration dành cho database đã được tạo từ trước.
IF OBJECT_ID('dbo.IdempotencyKeys', 'U') IS NULL
BEGIN
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

    CREATE INDEX IX_Idempotency_CreatedAt ON IdempotencyKeys(created_at);
END;
GO

-- Nâng cấp an toàn cho bản migration cũ đã tạo bảng nhưng chưa có lifecycle.
IF COL_LENGTH('dbo.IdempotencyKeys', 'status') IS NULL
BEGIN
    ALTER TABLE IdempotencyKeys ADD status VARCHAR(12) NOT NULL
        CONSTRAINT DF_Idempotency_Status DEFAULT 'COMPLETED' WITH VALUES;
END;
GO

IF NOT EXISTS (
    SELECT 1 FROM sys.check_constraints
    WHERE name = 'CHK_Idempotency_Status'
      AND parent_object_id = OBJECT_ID('dbo.IdempotencyKeys')
)
BEGIN
    ALTER TABLE IdempotencyKeys ADD CONSTRAINT CHK_Idempotency_Status
        CHECK (status IN ('PROCESSING', 'COMPLETED'));
END;
GO

ALTER TABLE IdempotencyKeys ALTER COLUMN transaction_id UNIQUEIDENTIFIER NULL;
GO
