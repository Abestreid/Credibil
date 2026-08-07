#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
BACKUP_DIR="$PROJECT_DIR/backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
RETENTION_DAYS="${BACKUP_RETENTION_DAYS:-30}"

mkdir -p "$BACKUP_DIR"

echo "[$(date -Iseconds)] Starting PostgreSQL backup..."

DB_HOST="${DB_HOST:-localhost}"
DB_PORT="${DB_PORT:-5432}"
DB_NAME="${DB_NAME:-credibil}"
DB_USER="${DB_USER:-credibil}"

BACKUP_FILE="$BACKUP_DIR/${DB_NAME}_${TIMESTAMP}.sql.gz"

pg_dump -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" \
    --no-owner --no-privileges --clean --if-exists \
    | gzip > "$BACKUP_FILE"

FILESIZE=$(du -h "$BACKUP_FILE" | cut -f1)
echo "[$(date -Iseconds)] Backup complete: $BACKUP_FILE ($FILESIZE)"

echo "[$(date -Iseconds)] Cleaning backups older than $RETENTION_DAYS days..."
find "$BACKUP_DIR" -name "*.sql.gz" -mtime +"$RETENTION_DAYS" -delete
REMAINING=$(find "$BACKUP_DIR" -name "*.sql.gz" | wc -l)
echo "[$(date -Iseconds)] $REMAINING backups remaining"

if [ -n "${S3_BACKUP_BUCKET:-}" ]; then
    echo "[$(date -Iseconds)] Uploading to S3..."
    aws s3 cp "$BACKUP_FILE" "s3://$S3_BACKUP_BUCKET/backups/$(basename "$BACKUP_FILE")" \
        --storage-class STANDARD_IA
    echo "[$(date -Iseconds)] S3 upload complete"
fi

echo "[$(date -Iseconds)] Backup finished successfully"
