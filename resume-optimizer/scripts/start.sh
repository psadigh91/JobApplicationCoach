#!/bin/bash

echo "🚀 Starting Resume Optimizer..."
echo "==============================="

# Start backend
echo "Starting backend..."
cd backend
source venv/bin/activate
python main.py &
BACKEND_PID=$!
echo "✅ Backend running on http://localhost:8000 (PID: $BACKEND_PID)"

cd ..

# Start frontend
echo "Starting frontend..."
cd frontend
npm run dev &
FRONTEND_PID=$!
echo "✅ Frontend running on http://localhost:5173 (PID: $FRONTEND_PID)"

cd ..

# Save PIDs
echo $BACKEND_PID > .backend.pid
echo $FRONTEND_PID > .frontend.pid

echo ""
echo "✅ Application started!"
echo ""
echo "📝 Access the app at: http://localhost:5173"
echo "📝 API docs at: http://localhost:8000/docs"
echo ""
echo "To stop: ./scripts/stop.sh"
