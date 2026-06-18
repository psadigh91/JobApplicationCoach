#!/bin/bash
# Elastic Beanstalk Deployment Script for Resume Optimizer Backend
# Usage: ./BACKEND-DEPLOY-EB.sh

set -e

echo "🚀 Resume Optimizer - Backend Deployment to AWS Elastic Beanstalk"
echo "=================================================================="
echo ""

# Check prerequisites
echo "📋 Checking prerequisites..."

if ! command -v eb &> /dev/null; then
    echo "❌ Elastic Beanstalk CLI not found"
    echo "📦 Installing EB CLI..."
    pip install awsebcli
fi

if ! command -v aws &> /dev/null; then
    echo "⚠️  AWS CLI not found - you may need to configure credentials manually"
else
    echo "✅ AWS CLI found"
fi

echo ""
echo "🔑 Before proceeding, make sure you have:"
echo "  1. AWS account with proper permissions"
echo "  2. AWS credentials configured (aws configure)"
echo "  3. Anthropic API key ready"
echo ""
read -p "Press Enter to continue or Ctrl+C to cancel..."

# Navigate to backend directory
cd "$(dirname "$0")/backend"
echo "📁 Working directory: $(pwd)"

# Check if requirements.txt exists
if [ ! -f "requirements.txt" ]; then
    echo "❌ requirements.txt not found"
    exit 1
fi

# Create .ebignore if it doesn't exist
if [ ! -f ".ebignore" ]; then
    echo "📝 Creating .ebignore..."
    cat > .ebignore << 'EOF'
__pycache__/
*.pyc
*.pyo
*.pyd
.Python
venv/
env/
.env
*.sqlite
*.db
.DS_Store
.idea/
.vscode/
*.log
uploads/*
!uploads/.gitkeep
EOF
fi

# Create Procfile for EB
if [ ! -f "Procfile" ]; then
    echo "📝 Creating Procfile..."
    echo "web: uvicorn main:app --host 0.0.0.0 --port 8000" > Procfile
fi

# Initialize EB application
echo ""
echo "🔧 Initializing Elastic Beanstalk application..."
if [ ! -d ".elasticbeanstalk" ]; then
    eb init -p python-3.11 resume-optimizer-api --region us-east-2
else
    echo "✅ EB already initialized"
fi

# Ask for Anthropic API key
echo ""
read -p "🔑 Enter your Anthropic API key (or press Enter to set later): " ANTHROPIC_KEY

# Create environment
echo ""
echo "🌍 Creating Elastic Beanstalk environment..."
read -p "Enter environment name (default: resume-optimizer-prod): " ENV_NAME
ENV_NAME=${ENV_NAME:-resume-optimizer-prod}

if ! eb list | grep -q "$ENV_NAME"; then
    echo "Creating environment: $ENV_NAME"
    eb create "$ENV_NAME" \
        --instance-type t3.small \
        --timeout 15 \
        --envvars \
        API_HOST=0.0.0.0,\
        API_PORT=8000,\
        SESSION_EXPIRY_HOURS=24,\
        MAX_UPLOAD_SIZE_MB=10,\
        MAX_CRAWL_PAGES=10,\
        CRAWL_TIMEOUT_SECONDS=30
else
    echo "✅ Environment already exists"
fi

# Set Anthropic API key if provided
if [ -n "$ANTHROPIC_KEY" ]; then
    echo "🔐 Setting Anthropic API key..."
    eb setenv ANTHROPIC_API_KEY="$ANTHROPIC_KEY" -e "$ENV_NAME"
fi

# Deploy
echo ""
echo "📤 Deploying application..."
eb deploy "$ENV_NAME"

# Get status and URL
echo ""
echo "✅ Deployment complete!"
echo ""
echo "📊 Environment status:"
eb status "$ENV_NAME"

echo ""
echo "🎉 Backend deployment successful!"
echo ""
BACKEND_URL=$(eb status "$ENV_NAME" | grep CNAME | awk '{print $2}')
if [ -n "$BACKEND_URL" ]; then
    echo "🔗 Backend URL: https://$BACKEND_URL"
    echo ""
    echo "📋 Next steps:"
    echo "  1. Test backend: curl https://$BACKEND_URL/health"
    echo "  2. Update frontend .env.production:"
    echo "     VITE_API_URL=https://$BACKEND_URL/api"
    echo "  3. Rebuild frontend: npm run build"
    echo "  4. Deploy to Amplify"
    echo ""
    echo "💡 To set/update Anthropic API key later:"
    echo "   eb setenv ANTHROPIC_API_KEY=your_key -e $ENV_NAME"
    echo ""
    echo "📖 View logs:"
    echo "   eb logs $ENV_NAME"
fi

echo ""
echo "🎯 Deployment complete! Your backend is live."
