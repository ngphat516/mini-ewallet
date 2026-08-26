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
