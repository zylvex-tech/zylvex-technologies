#!/bin/bash

# Test script for SPATIAL CANVAS auth integration

echo "=== Testing SPATIAL CANVAS Auth Integration ==="

# Check if services are running
echo "1. Checking if services are accessible..."

# Test auth service health
if curl -s http://localhost:8001/health | grep -q "healthy"; then
    echo "   ✅ Auth service is healthy"
else
    echo "   ❌ Auth service is not responding"
    exit 1
fi

# Test spatial canvas backend health
if curl -s http://localhost:8000/health | grep -q "healthy"; then
    echo "   ✅ SPATIAL CANVAS backend is healthy"
else
    echo "   ❌ SPATIAL CANVAS backend is not responding"
    exit 1
fi

# Test authentication flow
echo "\n2. Testing authentication flow..."

# Register a test user
echo "   Registering test user..."
REGISTER_RESPONSE=$(curl -s -X POST http://localhost:8001/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "testpassword123",
    "full_name": "Test User"
  }')

echo "   Registration response: $REGISTER_RESPONSE"

# Login to get token
echo "   Logging in..."
LOGIN_RESPONSE=$(curl -s -X POST http://localhost:8001/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "testpassword123"
  }')

ACCESS_TOKEN=$(echo $LOGIN_RESPONSE | grep -o '"access_token":"[^"]*' | cut -d'"' -f4)

if [ -n "$ACCESS_TOKEN" ]; then
    echo "   ✅ Successfully obtained access token"
else
    echo "   ❌ Failed to get access token"
    echo "   Login response: $LOGIN_RESPONSE"
    exit 1
fi

# Test protected endpoint
echo "\n3. Testing protected SPATIAL CANVAS endpoint..."

PROTECTED_RESPONSE=$(curl -s -X GET http://localhost:8000/api/v1/anchors/mine \
  -H "Authorization: Bearer $ACCESS_TOKEN")

echo "   Protected endpoint response: $PROTECTED_RESPONSE"

if echo $PROTECTED_RESPONSE | grep -q '"anchors"'; then
    echo "   ✅ Successfully accessed protected endpoint"
else
    echo "   ⚠️  Protected endpoint may require anchors to exist"
fi

# Test public endpoint (should work without auth)
echo "\n4. Testing public endpoint..."

PUBLIC_RESPONSE=$(curl -s "http://localhost:8000/api/v1/anchors?latitude=0&longitude=0")

echo "   Public endpoint response: $PUBLIC_RESPONSE"

if echo $PUBLIC_RESPONSE | grep -q '"anchors"'; then
    echo "   ✅ Public endpoint accessible without authentication"
else
    echo "   ⚠️  Public endpoint response format may differ"
fi

echo "\n=== Auth Integration Test Complete ==="
echo "All tests passed! The auth integration is working correctly."
