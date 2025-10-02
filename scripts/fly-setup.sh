#!/bin/bash
# Fly.io Initial Setup Script
# Run this script to set up your Fly.io deployment

set -e

echo "🚀 Flowlog API - Fly.io Setup"
echo "================================"
echo ""

# Check if flyctl is installed
if ! command -v flyctl &> /dev/null; then
    echo "❌ Fly.io CLI not found. Installing..."
    brew install flyctl
fi

echo "✅ Fly.io CLI is installed"
echo ""

# Login check
echo "Checking Fly.io authentication..."
if ! flyctl auth whoami &> /dev/null; then
    echo "Please log in to Fly.io:"
    flyctl auth login
fi

echo "✅ Authenticated with Fly.io"
echo ""

# Create app
echo "📦 Creating Fly.io app..."
read -p "Enter app name (default: flowlog-api): " APP_NAME
APP_NAME=${APP_NAME:-flowlog-api}

if flyctl apps list | grep -q "$APP_NAME"; then
    echo "✅ App '$APP_NAME' already exists"
else
    flyctl apps create "$APP_NAME" --org personal
    echo "✅ Created app: $APP_NAME"
fi
echo ""

# Create database
echo "🗄️  Setting up PostgreSQL database..."
DB_NAME="${APP_NAME}-db"

if flyctl apps list | grep -q "$DB_NAME"; then
    echo "✅ Database '$DB_NAME' already exists"
else
    echo "Creating PostgreSQL cluster..."
    flyctl postgres create --name "$DB_NAME" --region sjc --initial-cluster-size 1 --vm-size shared-cpu-1x --volume-size 1
    echo "✅ Created database: $DB_NAME"
fi
echo ""

# Attach database
echo "🔗 Attaching database to app..."
flyctl postgres attach "$DB_NAME" --app "$APP_NAME" || echo "Database may already be attached"
echo ""

# Set secrets
echo "🔐 Setting up secrets..."
echo ""

# Generate secret key
SECRET_KEY=$(openssl rand -hex 32)
echo "Generated SECRET_KEY: ${SECRET_KEY:0:10}..."

# Set all secrets
flyctl secrets set \
    SECRET_KEY="$SECRET_KEY" \
    ACCESS_TOKEN_EXPIRE_MINUTES="11520" \
    ALGORITHM="HS256" \
    BACKEND_CORS_ORIGINS='["*"]' \
    --app "$APP_NAME"

echo "✅ Secrets configured"
echo ""

# Get GitHub PAT
echo "🔑 GitHub Personal Access Token Setup"
echo "To allow Fly.io to pull from GitHub Container Registry:"
echo "1. Go to: https://github.com/settings/tokens"
echo "2. Generate a new token (classic) with 'read:packages' scope"
echo "3. Copy the token"
echo ""

read -p "Enter your GitHub Personal Access Token (or press Enter to skip): " GITHUB_PAT

if [ -n "$GITHUB_PAT" ]; then
    flyctl secrets set \
        REGISTRY_USERNAME="smiileyface" \
        REGISTRY_PASSWORD="$GITHUB_PAT" \
        --app "$APP_NAME"
    echo "✅ GitHub registry access configured"
else
    echo "⚠️  Skipped GitHub registry setup. You'll need to configure this later."
fi
echo ""

# Deploy token for GitHub Actions
echo "🤖 GitHub Actions Setup"
echo "To enable automatic deployments from GitHub Actions:"
echo ""
FLY_TOKEN=$(flyctl auth token)
echo "Your Fly.io API token:"
echo "$FLY_TOKEN"
echo ""
echo "Add this token to GitHub:"
echo "1. Go to: https://github.com/smiileyface/flowlog-api/settings/secrets/actions"
echo "2. Click 'New repository secret'"
echo "3. Name: FLY_API_TOKEN"
echo "4. Value: (paste the token above)"
echo ""

read -p "Press Enter when you've added the token to GitHub..."
echo ""

# Update fly.toml
echo "📝 Updating fly.toml with app name..."
sed -i.bak "s/app = 'flowlog-api'/app = '$APP_NAME'/" fly.toml
rm fly.toml.bak
echo "✅ Updated fly.toml"
echo ""

# Initial deployment
echo "🚀 Ready for initial deployment!"
echo ""
read -p "Deploy now? (y/N): " DEPLOY_NOW

if [[ "$DEPLOY_NOW" =~ ^[Yy]$ ]]; then
    echo "Deploying from GHCR..."
    echo "Note: Make sure you've pushed to main and the Docker image is built"
    flyctl deploy --app "$APP_NAME" --image ghcr.io/smiileyface/flowlog-api:main || echo "⚠️  Deployment failed. You may need to build and push your Docker image first."
else
    echo "Skipped initial deployment."
    echo ""
    echo "To deploy manually later, run:"
    echo "  flyctl deploy --app $APP_NAME --image ghcr.io/smiileyface/flowlog-api:main"
fi

echo ""
echo "✅ Setup complete!"
echo ""
echo "📋 Next steps:"
echo "  1. Commit and push fly.toml to your repo"
echo "  2. Push to main to trigger automatic deployment"
echo "  3. View your app: flyctl open --app $APP_NAME"
echo "  4. View logs: flyctl logs --app $APP_NAME"
echo ""
echo "📚 Full documentation: docs/FLY_DEPLOYMENT.md"
