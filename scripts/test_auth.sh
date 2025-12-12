echo
echo
echo "Authentication flow OK: token valid and protected endpoint returned 200."
#!/usr/bin/env bash
set -euo pipefail

# Robust JWT flow test script for deployment verification
# Usage:
#   BASE_URL=https://your-domain ./scripts/test_auth.sh
# Optional env vars: USERNAME, EMAIL, PASSWORD, REGISTER_VIA_API (true/false)

BASE_URL=${BASE_URL:-http://localhost:8000}
USERNAME=${USERNAME:-apitest}
EMAIL=${EMAIL:-apitest@example.com}
PASSWORD=${PASSWORD:-TestPass123}
REGISTER_VIA_API=${REGISTER_VIA_API:-true}

echo "[test_auth] Base URL: $BASE_URL"

if [ "$REGISTER_VIA_API" = "true" ]; then
  echo "[test_auth] Registering user $USERNAME via API (idempotent) ..."
  REG_RES=$(curl -s -w "\n%{http_code}" -X POST "$BASE_URL/api/users/register/" \
    -H "Content-Type: application/json" \
    -d "{\"username\":\"$USERNAME\",\"email\":\"$EMAIL\",\"password\":\"$PASSWORD\"}")

  HTTP_CODE=$(echo "$REG_RES" | tail -n1)
  BODY=$(echo "$REG_RES" | sed '$d')
  echo "[test_auth] Register response code: $HTTP_CODE"
  echo "$BODY"
  # continue even if user exists
fi

echo "[test_auth] Obtaining JWT token..."
TOK=$(curl -s -X POST "$BASE_URL/api/token/" \
  -H "Content-Type: application/json" \
  -d "{\"username\":\"$USERNAME\",\"password\":\"$PASSWORD\"}")

if command -v jq >/dev/null 2>&1; then
  echo "$TOK" | jq || true
else
  echo "$TOK"
fi

ACCESS=$(echo "$TOK" | python3 -c "import sys, json; d=json.load(sys.stdin); print(d.get('access',''))")

if [ -z "$ACCESS" ]; then
  echo "[test_auth] Failed to get access token. Full response:" >&2
  echo "$TOK" >&2
  exit 1
fi

echo "[test_auth] Calling protected endpoint /api/users/me/ with access token..."
PROT=$(curl -s -w "\n%{http_code}" -X GET "$BASE_URL/api/users/me/" \
  -H "Authorization: Bearer $ACCESS" \
  -H "Accept: application/json")
HTTP_CODE=$(echo "$PROT" | tail -n1)
BODY=$(echo "$PROT" | sed '$d')

echo "[test_auth] Protected endpoint response code: $HTTP_CODE"
echo "$BODY"

if [ "$HTTP_CODE" -ne 200 ]; then
  echo "[test_auth] Protected endpoint did not return 200. Authentication may be failing." >&2
  exit 2
fi

echo "[test_auth] Authentication flow OK: token valid and protected endpoint returned 200."
exit 0
