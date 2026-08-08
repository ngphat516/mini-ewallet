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
        transaction_id UNIQUEIDENTIFIER NOT NULL REFERENCES Transactions(txn_id),
        response_balance DECIMAL(18,2) NULL,
        created_at      DATETIME2 NOT NULL DEFAULT GETDATE(),
        CONSTRAINT UQ_Idempotency_User_Key UNIQUE (user_id, [key])
    );

    CREATE INDEX IX_Idempotency_CreatedAt ON IdempotencyKeys(created_at);
END;
GO
