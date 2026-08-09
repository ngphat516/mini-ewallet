USE ebanking;
GO
ALTER TABLE RefreshTokens ADD
    session_id UNIQUEIDENTIFIER NULL, family_id UNIQUEIDENTIFIER NULL,
    device_name NVARCHAR(255) NOT NULL CONSTRAINT DF_RefreshTokens_Device DEFAULT 'Unknown device',
    ip_address VARCHAR(45) NULL, revoked_reason VARCHAR(20) NULL,
    replaced_by_token_id UNIQUEIDENTIFIER NULL,
    last_used_at DATETIME2 NOT NULL CONSTRAINT DF_RefreshTokens_LastUsed DEFAULT GETUTCDATE();
GO
UPDATE RefreshTokens SET session_id = token_id, family_id = token_id WHERE session_id IS NULL;
ALTER TABLE RefreshTokens ALTER COLUMN session_id UNIQUEIDENTIFIER NOT NULL;
ALTER TABLE RefreshTokens ALTER COLUMN family_id UNIQUEIDENTIFIER NOT NULL;
ALTER TABLE RefreshTokens ADD CONSTRAINT FK_RefreshTokens_ReplacedBy FOREIGN KEY (replaced_by_token_id) REFERENCES RefreshTokens(token_id);
CREATE INDEX IX_RefreshTokens_Session ON RefreshTokens(session_id);
CREATE INDEX IX_RefreshTokens_Family ON RefreshTokens(family_id);
GO
