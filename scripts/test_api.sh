#!/bin/bash
# Test script to verify API functionality

set -e

echo "=== Testing API Health ==="
curl -s http://localhost:8001/ | head -5
echo ""

echo "=== Testing Login ==="
LOGIN_RESPONSE=$(curl -s -X POST http://localhost:8001/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "admin@rovet.io", "password": "admin123"}')
echo "$LOGIN_RESPONSE" | jq '.' 2>/dev/null || echo "$LOGIN_RESPONSE"
echo ""

# Extract token
TOKEN=$(echo "$LOGIN_RESPONSE" | grep -o '"access_token":"[^"]*' | cut -d'"' -f4)
if [ -z "$TOKEN" ]; then
    TOKEN=$(echo "$LOGIN_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin)['access_token'])" 2>/dev/null || echo "")
fi

if [ -z "$TOKEN" ]; then
    echo "ERROR: Could not extract token from login response"
    exit 1
fi

echo "=== Testing Get Users (with token) ==="
curl -s http://localhost:8001/api/v1/users/ \
  -H "Authorization: Bearer $TOKEN" | jq '.' 2>/dev/null || \
  curl -s http://localhost:8001/api/v1/users/ \
  -H "Authorization: Bearer $TOKEN"
echo ""

echo "=== Testing Get User by ID ==="
curl -s http://localhost:8001/api/v1/users/1 \
  -H "Authorization: Bearer $TOKEN" | jq '.' 2>/dev/null || \
  curl -s http://localhost:8001/api/v1/users/1 \
  -H "Authorization: Bearer $TOKEN"
echo ""

echo "=== Testing Public Key Endpoint ==="
curl -s http://localhost:8001/api/v1/auth/public-key | head -3
echo ""

echo "=== All tests completed ==="

