#!/bin/bash
# Comprehensive test script for the API

set -e

OUTPUT_FILE="/tmp/api_test_results.txt"

echo "=== API Test Results ===" > $OUTPUT_FILE
echo "Timestamp: $(date)" >> $OUTPUT_FILE
echo "" >> $OUTPUT_FILE

echo "1. Testing Health Endpoint..." | tee -a $OUTPUT_FILE
curl -s http://localhost:8001/ >> $OUTPUT_FILE 2>&1
echo "" >> $OUTPUT_FILE

echo "2. Seeding Database..." | tee -a $OUTPUT_FILE
python -m app.scripts.seed_db >> $OUTPUT_FILE 2>&1
echo "Database seeded successfully" >> $OUTPUT_FILE
echo "" >> $OUTPUT_FILE

echo "3. Testing Login..." | tee -a $OUTPUT_FILE
LOGIN_RESPONSE=$(curl -s -X POST http://localhost:8001/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "admin@rovet.io", "password": "admin123"}')
echo "$LOGIN_RESPONSE" >> $OUTPUT_FILE
echo "" >> $OUTPUT_FILE

# Try to extract token using Python
TOKEN=$(python3 -c "import sys, json; data=json.load(sys.stdin); print(data.get('access_token', ''))" <<< "$LOGIN_RESPONSE" 2>/dev/null || echo "")

if [ -z "$TOKEN" ]; then
    echo "ERROR: Could not extract token" >> $OUTPUT_FILE
    cat $OUTPUT_FILE
    exit 1
fi

echo "4. Testing Get Users Endpoint..." | tee -a $OUTPUT_FILE
curl -s http://localhost:8001/api/v1/users/ \
  -H "Authorization: Bearer $TOKEN" >> $OUTPUT_FILE 2>&1
echo "" >> $OUTPUT_FILE

echo "5. Testing Get User by ID..." | tee -a $OUTPUT_FILE
curl -s http://localhost:8001/api/v1/users/1 \
  -H "Authorization: Bearer $TOKEN" >> $OUTPUT_FILE 2>&1
echo "" >> $OUTPUT_FILE

echo "6. Testing Public Key Endpoint..." | tee -a $OUTPUT_FILE
curl -s http://localhost:8001/api/v1/auth/public-key | head -3 >> $OUTPUT_FILE 2>&1
echo "" >> $OUTPUT_FILE

echo "7. Running Pytest..." | tee -a $OUTPUT_FILE
pytest app/tests/ -v --tb=short >> $OUTPUT_FILE 2>&1 || echo "Some tests may have failed" >> $OUTPUT_FILE
echo "" >> $OUTPUT_FILE

echo "=== Test Results Complete ===" >> $OUTPUT_FILE
cat $OUTPUT_FILE

