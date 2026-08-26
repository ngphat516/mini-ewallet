USE ebanking;
GO

-- Safe to run on a new schema and on older databases that predate session
-- rotation. Each change is guarded for partially upgraded environments.
IF COL_LENGTH('dbo.RefreshTokens', 'session_id') IS NULL
    ALTER TABLE RefreshTokens ADD session_id UNIQUEIDENTIFIER NULL;
GO
IF COL_LENGTH('dbo.RefreshTokens', 'family_id') IS NULL
    ALTER TABLE RefreshTokens ADD family_id UNIQUEIDENTIFIER NULL;
GO
IF COL_LENGTH('dbo.RefreshTokens', 'device_name') IS NULL
    ALTER TABLE RefreshTokens ADD device_name NVARCHAR(255) NOT NULL
        CONSTRAINT DF_RefreshTokens_Device DEFAULT 'Unknown device';
GO
IF COL_LENGTH('dbo.RefreshTokens', 'ip_address') IS NULL
    ALTER TABLE RefreshTokens ADD ip_address VARCHAR(45) NULL;
GO
IF COL_LENGTH('dbo.RefreshTokens', 'revoked_reason') IS NULL
    ALTER TABLE RefreshTokens ADD revoked_reason VARCHAR(20) NULL;
GO
IF COL_LENGTH('dbo.RefreshTokens', 'replaced_by_token_id') IS NULL
    ALTER TABLE RefreshTokens ADD replaced_by_token_id UNIQUEIDENTIFIER NULL;
GO
IF COL_LENGTH('dbo.RefreshTokens', 'last_used_at') IS NULL
    ALTER TABLE RefreshTokens ADD last_used_at DATETIME2 NOT NULL
        CONSTRAINT DF_RefreshTokens_LastUsed DEFAULT GETUTCDATE();
GO

UPDATE RefreshTokens
SET session_id = token_id, family_id = token_id
WHERE session_id IS NULL OR family_id IS NULL;
GO

ALTER TABLE RefreshTokens ALTER COLUMN session_id UNIQUEIDENTIFIER NOT NULL;
ALTER TABLE RefreshTokens ALTER COLUMN family_id UNIQUEIDENTIFIER NOT NULL;
GO

IF NOT EXISTS (
    SELECT 1 FROM sys.foreign_keys
    WHERE name = 'FK_RefreshTokens_ReplacedBy'
      AND parent_object_id = OBJECT_ID('dbo.RefreshTokens')
)
    ALTER TABLE RefreshTokens ADD CONSTRAINT FK_RefreshTokens_ReplacedBy
        FOREIGN KEY (replaced_by_token_id) REFERENCES RefreshTokens(token_id);
GO

IF NOT EXISTS (
    SELECT 1 FROM sys.indexes
    WHERE name = 'IX_RefreshTokens_Session'
      AND object_id = OBJECT_ID('dbo.RefreshTokens')
)
    CREATE INDEX IX_RefreshTokens_Session ON RefreshTokens(session_id);
GO

IF NOT EXISTS (
    SELECT 1 FROM sys.indexes
    WHERE name = 'IX_RefreshTokens_Family'
      AND object_id = OBJECT_ID('dbo.RefreshTokens')
)
    CREATE INDEX IX_RefreshTokens_Family ON RefreshTokens(family_id);
GO
