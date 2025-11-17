#!/bin/bash
# Run all three agents in separate terminals/processes

# Data Scout Agent (port 8000)
cd "$(dirname "$0")"
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload &

# Compliance Agent (port 8001)
cd compliance-agent
uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload &

# Permit Liaison Agent (port 8002)
cd ../permit-liaison-agent
uvicorn app.main:app --host 0.0.0.0 --port 8002 --reload &

echo "All agents started:"
echo "  Data Scout: http://localhost:8000"
echo "  Compliance: http://localhost:8001"
echo "  Permit Liaison: http://localhost:8002"
echo ""
echo "Press Ctrl+C to stop all agents"

wait
