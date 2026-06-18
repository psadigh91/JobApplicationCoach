#!/bin/bash

echo "🚀 Resume Optimizer - Setup Script"
echo "=================================="

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.9 or higher."
    exit 1
fi

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js 18 or higher."
    exit 1
fi

echo ""
echo "📦 Setting up backend..."
cd backend

# Create virtual environment
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "✅ Created Python virtual environment"
fi

# Activate virtual environment
source venv/bin/activate

# Install Python dependencies
pip install --upgrade pip
pip install -r requirements.txt
echo "✅ Installed Python dependencies"

cd ..

echo ""
echo "📦 Setting up frontend..."
cd frontend

# Install Node dependencies
npm install
echo "✅ Installed Node dependencies"

cd ..

echo ""
echo "🗄️  Initializing database..."
cd backend
source venv/bin/activate
python -c "from core.database import init_db; init_db()"
echo "✅ Database initialized"

cd ..

echo ""
echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Copy .env.example to .env and add your ANTHROPIC_API_KEY"
echo "2. Run ./scripts/start.sh to start the application"
