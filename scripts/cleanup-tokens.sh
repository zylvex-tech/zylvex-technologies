#!/bin/bash
# Purge expired and revoked refresh tokens older than 7 days
# Run as a daily cron job:
# 0 2 * * * /opt/zylvex/scripts/cleanup-tokens.sh

set -e

DATABASE_URL="${DATABASE_URL:-postgresql://auth_user:auth_pass@localhost:5432/auth_db}"

psql "$DATABASE_URL" -c "
DELETE FROM refresh_tokens
WHERE revoked = TRUE
   OR expires_at < NOW() - INTERVAL '7 days';
"

echo "Token cleanup completed at $(date)"
