#!/bin/bash

# Test script for Spatial Canvas API

echo "Testing Spatial Canvas API setup..."

# Check if docker-compose is running
if docker-compose ps | grep -q "spatial-canvas-backend"; then
    echo "✅ Docker containers are running"
else
    echo "⚠️  Starting Docker containers..."
    docker-compose up -d
    sleep 10
fi

# Test health endpoint
echo "\nTesting health endpoint..."
curl -s http://localhost:8000/health | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    if data.get('status') == 'healthy':
        print('✅ Health check passed')
    else:
        print('❌ Health check failed:', data)
except:
    print('❌ Could not reach API')
"

# Test API documentation
echo "\nTesting API documentation..."
curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/docs
if [ $? -eq 0 ]; then
    echo "✅ API documentation available at http://localhost:8000/docs"
else
    echo "❌ API documentation not available"
fi

# Test anchors endpoint (should return empty list)
echo "\nTesting anchors endpoint..."
curl -s "http://localhost:8000/api/v1/anchors?latitude=40.7128&longitude=-74.0060&radius_km=0.1" | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    if 'anchors' in data:
        print(f'✅ Anchors endpoint working. Found {data["count"]} anchors')
    else:
        print('❌ Unexpected response:', data)
except Exception as e:
    print('❌ Error:', e)
"

echo "\n✅ Setup complete!"
echo "API URL: http://localhost:8000"
echo "Docs: http://localhost:8000/docs"
echo "\nTo stop the services: docker-compose down"
