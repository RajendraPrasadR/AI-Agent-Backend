#!/bin/bash
# AI Agent Backend - Task Assignment Example
# Demonstrates how to assign tasks and retrieve results using curl

set -e

BASE_URL="http://localhost:8000"

echo "========================================"
echo "AI Agent Backend - Task Assignment Example"
echo "========================================"

# Check if orchestrator service is running
echo "Checking if Orchestrator Service is running..."
if ! curl -f -s "${BASE_URL}/health" > /dev/null; then
    echo "ERROR: Orchestrator Service is not running!"
    echo "Please start the services first:"
    echo "  Windows: start_all.bat"
    echo "  Linux/macOS: ./start_all.sh"
    echo "  Docker: docker-compose up"
    exit 1
fi

echo "✓ Orchestrator Service is running"
echo ""

# Example 1: Health Check
echo "1. Health Check"
echo "==============="
echo "GET ${BASE_URL}/health"
curl -s "${BASE_URL}/health" | python3 -m json.tool
echo ""
echo ""

# Example 2: Test Task Assignment
echo "2. Test Task Assignment"
echo "======================="
echo "POST ${BASE_URL}/assign-task/"

TASK_RESPONSE=$(curl -s -X POST "${BASE_URL}/assign-task/" \
  -H "Content-Type: application/json" \
  -d '{
    "task_type": "test_task",
    "params": {
      "duration": 3,
      "success_rate": 0.9,
      "test_data": "example_data"
    }
  }')

echo "$TASK_RESPONSE" | python3 -m json.tool

# Extract task_id from response
TASK_ID=$(echo "$TASK_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin)['task_id'])")
echo ""
echo "Task assigned with ID: $TASK_ID"
echo ""

# Example 3: Check Task Result (immediate)
echo "3. Check Task Result (immediate)"
echo "==============================="
echo "GET ${BASE_URL}/result/${TASK_ID}"
curl -s "${BASE_URL}/result/${TASK_ID}" | python3 -m json.tool
echo ""
echo ""

# Example 4: Wait and Check Task Result
echo "4. Wait and Check Task Result"
echo "============================"
echo "Waiting for task to complete..."
sleep 5

echo "GET ${BASE_URL}/result/${TASK_ID}"
curl -s "${BASE_URL}/result/${TASK_ID}" | python3 -m json.tool
echo ""
echo ""

# Example 5: Batch Approval Task Assignment
echo "5. Batch Approval Task Assignment"
echo "================================="
echo "POST ${BASE_URL}/assign-task/"

BATCH_TASK_RESPONSE=$(curl -s -X POST "${BASE_URL}/assign-task/" \
  -H "Content-Type: application/json" \
  -d '{
    "task_type": "approve_batches",
    "params": {
      "batch_ids": ["BATCH001", "BATCH002", "BATCH003"],
      "max_batches": 5,
      "auto_approve": true
    }
  }')

echo "$BATCH_TASK_RESPONSE" | python3 -m json.tool

# Extract batch task_id from response
BATCH_TASK_ID=$(echo "$BATCH_TASK_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin)['task_id'])")
echo ""
echo "Batch approval task assigned with ID: $BATCH_TASK_ID"
echo ""

# Example 6: Monitor Batch Task Progress
echo "6. Monitor Batch Task Progress"
echo "============================="
echo "Note: Batch approval tasks may take several minutes to complete"
echo "GET ${BASE_URL}/result/${BATCH_TASK_ID}"

for i in {1..3}; do
    echo "Check #$i:"
    RESULT=$(curl -s "${BASE_URL}/result/${BATCH_TASK_ID}")
    echo "$RESULT" | python3 -m json.tool
    
    STATUS=$(echo "$RESULT" | python3 -c "import sys, json; print(json.load(sys.stdin)['status'])")
    if [ "$STATUS" = "completed" ] || [ "$STATUS" = "failed" ]; then
        break
    fi
    
    echo "Task still running, waiting 10 seconds..."
    sleep 10
    echo ""
done

echo ""
echo "========================================"
echo "Example completed!"
echo "========================================"
echo ""
echo "Additional API endpoints to try:"
echo "- GET ${BASE_URL}/ (service info)"
echo "- GET ${BASE_URL}/docs (interactive API documentation)"
echo "- GET ${BASE_URL}/redoc (alternative API documentation)"
echo ""
echo "For more examples, check the API documentation at:"
echo "${BASE_URL}/docs"
