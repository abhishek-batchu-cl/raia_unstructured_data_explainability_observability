#!/bin/bash

echo "=================================================================="
echo "  🚀 RAIA ENTERPRISE FULL-STACK DEPLOYMENT"
echo "=================================================================="
echo ""

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Step 1: Backend Setup
echo -e "${BLUE}Step 1: Setting up Backend (FastAPI)${NC}"
echo "--------------------------------------------------------------"

cd backend

if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

echo "Activating virtual environment..."
source venv/bin/activate

echo "Installing backend dependencies..."
pip install -q -r requirements.txt

echo -e "${GREEN}✅ Backend setup complete!${NC}"
echo ""

# Step 2: Frontend Setup
echo -e "${BLUE}Step 2: Setting up Frontend (React + TypeScript)${NC}"
echo "--------------------------------------------------------------"

cd ../

# Check if frontend exists with node_modules
if [ ! -d "frontend/node_modules" ]; then
    echo "Frontend not initialized. Creating with Vite..."

    # Create frontend with Vite
    npm create vite@latest frontend -- --template react-ts

    cd frontend

    echo "Installing dependencies..."
    npm install

    echo "Installing UI libraries..."
    npm install @mui/material @mui/icons-material @emotion/react @emotion/styled
    npm install recharts axios date-fns @tanstack/react-query react-router-dom

    echo -e "${GREEN}✅ Frontend setup complete!${NC}"
    cd ..
else
    echo "Frontend already initialized."
    cd frontend
    npm install
    cd ..
fi

echo ""

# Step 3: Start Services
echo -e "${BLUE}Step 3: Starting Services${NC}"
echo "--------------------------------------------------------------"

# Create run script
cat > run_full_stack.sh << 'RUNSCRIPT'
#!/bin/bash

echo "Starting RAIA Enterprise Application..."
echo ""

# Start backend in background
echo "🔧 Starting Backend API (Port 8000)..."
cd backend
source venv/bin/activate
uvicorn main:app --reload --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!
cd ..

echo "Backend PID: $BACKEND_PID"
echo ""

# Wait for backend to start
sleep 3

# Start frontend
echo "🎨 Starting Frontend Dashboard (Port 3000)..."
cd frontend
npm run dev &
FRONTEND_PID=$!
cd ..

echo "Frontend PID: $FRONTEND_PID"
echo ""

echo "=================================================================="
echo "  ✅ RAIA Enterprise Application Running!"
echo "=================================================================="
echo ""
echo "  📊 Frontend Dashboard: http://localhost:3000"
echo "  🔧 Backend API: http://localhost:8000"
echo "  📖 API Documentation: http://localhost:8000/api/docs"
echo ""
echo "  Press Ctrl+C to stop all services"
echo "=================================================================="
echo ""

# Handle Ctrl+C
trap "echo 'Stopping services...'; kill $BACKEND_PID $FRONTEND_PID; exit" INT

# Wait for processes
wait
RUNSCRIPT

chmod +x run_full_stack.sh

echo -e "${GREEN}✅ Deployment script created!${NC}"
echo ""

# Summary
echo "=================================================================="
echo "  🎉 SETUP COMPLETE!"
echo "=================================================================="
echo ""
echo "  📁 Project Structure:"
echo "     backend/          - FastAPI server (545 lines)"
echo "     frontend/         - React + TypeScript dashboard"
echo "     databases/        - SQLite data"
echo ""
echo "  🚀 To start the application:"
echo "     ./run_full_stack.sh"
echo ""
echo "  📊 Access Points:"
echo "     Frontend: http://localhost:3000"
echo "     Backend API: http://localhost:8000"
echo "     API Docs: http://localhost:8000/api/docs"
echo ""
echo "  📖 Documentation:"
echo "     CREATE_FULL_STACK_APP.md  - Complete guide"
echo "     DELIVERABLES_SUMMARY.md   - All features"
echo ""
echo "=================================================================="
