#!/usr/bin/env bash
# =============================================================================
# check-secrets.sh — Pre-commit hook: block commits containing hardcoded secrets
#
# Install as a pre-commit hook:
#   cp scripts/check-secrets.sh .git/hooks/pre-commit
#   chmod +x .git/hooks/pre-commit
#
# Or use with pre-commit framework (https://pre-commit.com) by adding to
# .pre-commit-config.yaml:
#   - repo: local
#     hooks:
#       - id: check-secrets
#         name: Check for hardcoded secrets
#         entry: scripts/check-secrets.sh
#         language: script
#         pass_filenames: false
# =============================================================================

set -euo pipefail

RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

FAILED=0

# Files staged for commit (or all tracked files when run standalone)
if git rev-parse --verify HEAD > /dev/null 2>&1; then
    STAGED=$(git diff --cached --name-only --diff-filter=ACM)
else
    STAGED=$(git ls-files)
fi

if [ -z "$STAGED" ]; then
    exit 0
fi

# ---------------------------------------------------------------------------
# Pattern checks
# ---------------------------------------------------------------------------

check_pattern() {
    local description="$1"
    local pattern="$2"
    # Exclude: this script itself, .env.example files, test fixtures, lock files
    local matches
    matches=$(echo "$STAGED" | xargs grep -l -E "$pattern" 2>/dev/null \
        | grep -v -E '(check-secrets\.sh|\.env\.example|requirements.*\.txt|package-lock\.json|yarn\.lock|\.md$)' \
        || true)
    if [ -n "$matches" ]; then
        echo -e "${RED}[SECRETS] Possible ${description} found in:${NC}"
        echo "$matches" | while read -r f; do
            echo -e "  ${YELLOW}$f${NC}"
            grep -n -E "$pattern" "$f" | grep -v -E '^\s*#' | head -5 || true
        done
        FAILED=1
    fi
}

# Hardcoded JWT secrets
check_pattern "hardcoded JWT secret" \
    '(jwt_secret|JWT_SECRET|secret_key|SECRET_KEY)\s*[:=]\s*["\x27][^$\{][^"\x27]{8,}'

# Raw password assignments (not referencing env vars)
check_pattern "hardcoded password" \
    '(password|passwd|POSTGRES_PASSWORD)\s*[:=]\s*["\x27][^$\{][^"\x27]{3,}'

# API keys
check_pattern "hardcoded API key" \
    '(api_key|API_KEY|apikey|APIKEY)\s*[:=]\s*["\x27][A-Za-z0-9_\-]{16,}'

# Common dummy secrets that should not be committed
check_pattern "placeholder secret that must be replaced" \
    '(local-dev-secret-change-in-production|your-generated-secret-here|your-super-secret|change-me-now)'

# ---------------------------------------------------------------------------

if [ "$FAILED" -eq 1 ]; then
    echo ""
    echo -e "${RED}Commit blocked: potential secrets detected.${NC}"
    echo "  - Move secrets to environment variables or a .env file (never committed)."
    echo "  - Use \${VARIABLE_NAME} syntax in config files."
    echo "  - If this is a false positive, review the match above carefully."
    exit 1
fi

echo "check-secrets: no hardcoded secrets detected."
exit 0
