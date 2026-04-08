#!/bin/bash

HF_URL=$1
PROJECT_DIR=$2

echo "Starting validation checks for $HF_URL on "$PROJECT_DIR"..."
echo ""

# 1. Check POST /reset returns 200
echo "[1/3] Checking if POST /reset returns 200..."
# using a minimal valid body based on pydantic models previously seen
HTTP_STATUS=$(curl -s -o /dev/null -w "%{http_code}" -X POST "${HF_URL}/reset" -H "Content-Type: application/json" -d '{"session_id": "val_session", "task_id": "skill_gap_identifier"}')

if [ "$HTTP_STATUS" -eq 200 ]; then
    echo "  -> SUCCESS (HTTP 200)"
else
    echo "  -> FAILED (HTTP $HTTP_STATUS)"
fi
echo ""

# 2. Check docker build succeeds
echo "[2/3] Checking if docker build succeeds locally..."
cd "$PROJECT_DIR" || exit 1
if docker build -t careernav-env-validate . ; then
    echo "  -> SUCCESS (Docker built successfully)"
else
    echo "  -> FAILED (Docker build error)"
fi
echo ""

# 3. Check openenv validate passes
echo "[3/3] Checking if openenv validate passes locally..."
# Assuming we are running from project root where .venv is located
if ../.venv/Scripts/openenv.exe validate . ; then
    echo "  -> SUCCESS (openenv validation passed)"
else
    echo "  -> FAILED (openenv validation failed)"
fi
echo ""

echo "All checks completed."
