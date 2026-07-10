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

-- ── RefreshTokens ─────────────────────────────────────────
CREATE TABLE RefreshTokens (
    token_id    UNIQUEIDENTIFIER  PRIMARY KEY DEFAULT NEWID(),
    user_id     UNIQUEIDENTIFIER  NOT NULL
                REFERENCES Users(user_id) ON DELETE CASCADE,
    token_hash  VARCHAR(255)      NOT NULL UNIQUE,
    expires_at  DATETIME2         NOT NULL,
    revoked_at  DATETIME2         NULL,
    created_at  DATETIME2         NOT NULL DEFAULT GETDATE()
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
    created_at     DATETIME2         NOT NULL DEFAULT GETDATE()
);
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

-- ── Stored Procedure: Transfer ────────────────────────────
CREATE PROCEDURE sp_Transfer
    @from_wallet_id  UNIQUEIDENTIFIER,
    @to_wallet_id    UNIQUEIDENTIFIER,
    @amount          DECIMAL(18,2),
    @description     NVARCHAR(255),
    @reference_code  VARCHAR(30)
AS
BEGIN
    SET NOCOUNT ON;
    SET XACT_ABORT ON;

    DECLARE @from_bal_before DECIMAL(18,2);
    DECLARE @from_bal_after  DECIMAL(18,2);
    DECLARE @to_bal_before   DECIMAL(18,2);
    DECLARE @to_bal_after    DECIMAL(18,2);

    BEGIN TRANSACTION;

        SELECT @from_bal_before = balance
        FROM Wallets WITH (UPDLOCK, ROWLOCK)
        WHERE wallet_id = @from_wallet_id AND status = 'ACTIVE';

        IF @from_bal_before IS NULL
        BEGIN
            ROLLBACK;
            RAISERROR('Source wallet not found or frozen', 16, 1);
            RETURN;
        END

        IF @from_bal_before < @amount
        BEGIN
            ROLLBACK;
            RAISERROR('Insufficient balance', 16, 1);
            RETURN;
        END

        SELECT @to_bal_before = balance
        FROM Wallets WITH (UPDLOCK, ROWLOCK)
        WHERE wallet_id = @to_wallet_id AND status = 'ACTIVE';

        IF @to_bal_before IS NULL
        BEGIN
            ROLLBACK;
            RAISERROR('Destination wallet not found or frozen', 16, 1);
            RETURN;
        END

        SET @from_bal_after = @from_bal_before - @amount;
        SET @to_bal_after   = @to_bal_before   + @amount;

        UPDATE Wallets SET balance = @from_bal_after
        WHERE wallet_id = @from_wallet_id;

        UPDATE Wallets SET balance = @to_bal_after
        WHERE wallet_id = @to_wallet_id;

        INSERT INTO Transactions (
            reference_code, txn_type,
            from_wallet_id, to_wallet_id,
            amount,
            from_balance_before, from_balance_after,
            to_balance_before,   to_balance_after,
            status, description
        ) VALUES (
            @reference_code, 'TRANSFER',
            @from_wallet_id, @to_wallet_id,
            @amount,
            @from_bal_before, @from_bal_after,
            @to_bal_before,   @to_bal_after,
            'SUCCESS', @description
        );

    COMMIT;

    SELECT 'SUCCESS' AS result, @from_bal_after AS new_balance;
END;
GO