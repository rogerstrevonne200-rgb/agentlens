#!/usr/bin/env bash
set -e

ROOT="$(cd "$(dirname "$0")" && pwd)"

cleanup() {
    echo ""
    echo "Shutting down..."
    kill $SERVER_PID $DASHBOARD_PID 2>/dev/null
    wait $SERVER_PID $DASHBOARD_PID 2>/dev/null
    exit 0
}
trap cleanup INT TERM

echo "Starting AgentLens..."
echo ""

# Start FastAPI server
cd "$ROOT/server"
python -m uvicorn main:app --host 0.0.0.0 --port 7842 --reload &
SERVER_PID=$!

# Start dashboard dev server
cd "$ROOT/dashboard"
npm run dev -- --port 5173 &
DASHBOARD_PID=$!

echo ""
echo "  API server:  http://localhost:7842"
echo "  Dashboard:   http://localhost:5173"
echo ""
echo "Press Ctrl+C to stop both."

wait
