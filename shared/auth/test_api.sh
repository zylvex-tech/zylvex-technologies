#!/bin/bash

# Test script for authentication API
BASE_URL="http://localhost:8001"

echo "Testing Authentication API at $BASE_URL"
echo "========================================"

# Test health endpoint
echo "\n1. Testing health endpoint..."
curl -s "$BASE_URL/health" | jq .

# Test registration
echo "\n2. Testing user registration..."
REGISTER_RESPONSE=$(curl -s -X POST "$BASE_URL/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "testuser@example.com",
    "password": "testpassword123",
    "full_name": "Test User"
  }')

echo "Registration response:"
echo $REGISTER_RESPONSE | jq .

# Extract user ID from response
USER_ID=$(echo $REGISTER_RESPONSE | jq -r '.id' 2>/dev/null)

# Test login
echo "\n3. Testing login..."
LOGIN_RESPONSE=$(curl -s -X POST "$BASE_URL/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "testuser@example.com",
    "password": "testpassword123"
  }')

echo "Login response:"
echo $LOGIN_RESPONSE | jq .

# Extract tokens
ACCESS_TOKEN=$(echo $LOGIN_RESPONSE | jq -r '.access_token' 2>/dev/null)
REFRESH_TOKEN=$(echo $LOGIN_RESPONSE | jq -r '.refresh_token' 2>/dev/null)

if [ "$ACCESS_TOKEN" != "null" ] && [ -n "$ACCESS_TOKEN" ]; then
    # Test getting current user
    echo "\n4. Testing get current user..."
    curl -s -X GET "$BASE_URL/auth/me" \
      -H "Authorization: Bearer $ACCESS_TOKEN" | jq .
    
    # Test refresh token
    echo "\n5. Testing token refresh..."
    curl -s -X POST "$BASE_URL/auth/refresh" \
      -H "Content-Type: application/json" \
      -d "{\"refresh_token\": \"$REFRESH_TOKEN\"}" | jq .
    
    # Test logout
    echo "\n6. Testing logout..."
    curl -s -X POST "$BASE_URL/auth/logout" \
      -H "Content-Type: application/json" \
      -d "{\"refresh_token\": \"$REFRESH_TOKEN\"}" | jq .
else
    echo "\nFailed to get access token from login response"
fi

echo "\n========================================"
echo "Test completed"
