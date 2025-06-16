#!/bin/bash

# Backup script for Kairos BCP PostgreSQL database
# Runs daily backups and maintains retention policy

set -e

# Configuration
DB_HOST=${DB_HOST:-postgres}
DB_PORT=${DB_PORT:-5432}
DB_NAME=${DB_NAME:-kairos_bcp}
DB_USER=${DB_USER:-kairos_user}
BACKUP_DIR=${BACKUP_DIR:-/backups}
RETENTION_DAYS=${RETENTION_DAYS:-30}

# Create backup directory if it doesn't exist
mkdir -p $BACKUP_DIR

# Generate timestamp
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_FILE="$BACKUP_DIR/kairos_bcp_backup_$TIMESTAMP.sql"

echo "Starting backup at $(date)"
echo "Database: $DB_NAME"
echo "Host: $DB_HOST:$DB_PORT"
echo "Backup file: $BACKUP_FILE"

# Create database backup
pg_dump -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME \
    --verbose \
    --format=custom \
    --compress=9 \
    --file="$BACKUP_FILE.dump"

# Also create SQL dump for easier inspection
pg_dump -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME \
    --verbose \
    --format=plain \
    --file="$BACKUP_FILE"

# Compress SQL file
gzip "$BACKUP_FILE"

echo "Backup completed: $BACKUP_FILE.gz and $BACKUP_FILE.dump"

# Calculate backup size
BACKUP_SIZE=$(du -h "$BACKUP_FILE.gz" | cut -f1)
DUMP_SIZE=$(du -h "$BACKUP_FILE.dump" | cut -f1)

echo "SQL backup size: $BACKUP_SIZE"
echo "Custom dump size: $DUMP_SIZE"

# Clean up old backups
echo "Cleaning up backups older than $RETENTION_DAYS days..."
find $BACKUP_DIR -name "kairos_bcp_backup_*.sql.gz" -type f -mtime +$RETENTION_DAYS -delete
find $BACKUP_DIR -name "kairos_bcp_backup_*.sql.dump" -type f -mtime +$RETENTION_DAYS -delete

# List remaining backups
echo "Remaining backups:"
ls -lh $BACKUP_DIR/kairos_bcp_backup_*

echo "Backup script completed at $(date)"

# Optional: Upload to cloud storage
if [ ! -z "$AWS_S3_BUCKET" ]; then
    echo "Uploading backup to S3..."
    aws s3 cp "$BACKUP_FILE.gz" "s3://$AWS_S3_BUCKET/backups/"
    aws s3 cp "$BACKUP_FILE.dump" "s3://$AWS_S3_BUCKET/backups/"
    echo "Upload completed"
fi

# Optional: Send notification
if [ ! -z "$WEBHOOK_URL" ]; then
    curl -X POST -H 'Content-type: application/json' \
        --data "{\"text\":\"Kairos BCP backup completed: $BACKUP_FILE.gz ($BACKUP_SIZE)\"}" \
        "$WEBHOOK_URL"
fi