#!/usr/bin/env bash
set -euo pipefail

sqlcmd=/opt/mssql-tools18/bin/sqlcmd

for _ in $(seq 1 60); do
  if "$sqlcmd" -S sqlserver -U sa -C -d master -Q "SELECT 1" >/dev/null 2>&1; then
    break
  fi
  sleep 2
done

if ! "$sqlcmd" -S sqlserver -U sa -C -d master -Q "SELECT 1" >/dev/null 2>&1; then
  echo "SQL Server did not become ready in time." >&2
  exit 1
fi

"$sqlcmd" -S sqlserver -U sa -C -d master -b -Q "IF DB_ID(N'ebanking') IS NULL CREATE DATABASE ebanking;"

for _ in $(seq 1 60); do
  if "$sqlcmd" -S sqlserver -U sa -C -d ebanking -Q "SELECT 1" >/dev/null 2>&1; then
    break
  fi
  sleep 2
done

if ! "$sqlcmd" -S sqlserver -U sa -C -d ebanking -Q "SELECT 1" >/dev/null 2>&1; then
  echo "The ebanking database did not become ready in time." >&2
  exit 1
fi

has_schema=$("$sqlcmd" -S sqlserver -U sa -C -d ebanking -h -1 -W -Q "SET NOCOUNT ON; SELECT CASE WHEN OBJECT_ID(N'dbo.Users', N'U') IS NULL THEN 0 ELSE 1 END;" | tr -d '[:space:]')
if [ "$has_schema" = "0" ]; then
  "$sqlcmd" -S sqlserver -U sa -C -b -d ebanking -i /init/01_schema.sql
  echo "Initialized ebanking schema."
else
  echo "ebanking schema already exists; skipping initialization."
fi

# Existing databases receive each versioned migration once; fresh databases
# record the migrations already present in the initial schema.
"$sqlcmd" -S sqlserver -U sa -C -b -d ebanking -Q "
IF OBJECT_ID(N'dbo.SchemaMigrations', N'U') IS NULL
BEGIN
    CREATE TABLE dbo.SchemaMigrations (
        migration_name VARCHAR(255) NOT NULL PRIMARY KEY,
        applied_at DATETIME2 NOT NULL DEFAULT GETUTCDATE()
    );
END
"

for migration in /migrations/*.sql; do
  migration_name=$(basename "$migration")
  applied=$("$sqlcmd" -S sqlserver -U sa -C -d ebanking -h -1 -W -Q \
    "SET NOCOUNT ON; SELECT COUNT(*) FROM dbo.SchemaMigrations WHERE migration_name = N'$migration_name';" \
    | tr -d '[:space:]')

  if [ "$applied" = "0" ]; then
    "$sqlcmd" -S sqlserver -U sa -C -b -d ebanking -i "$migration"
    "$sqlcmd" -S sqlserver -U sa -C -b -d ebanking -Q \
      "INSERT INTO dbo.SchemaMigrations (migration_name) VALUES (N'$migration_name');"
    echo "Applied migration $migration_name."
  else
    echo "Migration $migration_name already applied."
  fi
done
