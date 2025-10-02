# Fly.io Quick Reference

## 🚀 Quick Start Commands

```bash
# Install Fly.io CLI (Mac)
brew install flyctl

# Login
flyctl auth login

# Run complete setup
./scripts/fly-setup.sh
```

## 📦 Deployment Commands

```bash
# Deploy from GHCR
flyctl deploy --image ghcr.io/smiileyface/flowlog-api:main

# Deploy specific tag
flyctl deploy --image ghcr.io/smiileyface/flowlog-api:v1.0.0

# Check deployment status
flyctl status
```

## 📊 Monitoring

```bash
# View logs (live)
flyctl logs

# View logs (follow mode)
flyctl logs -f

# Open app in browser
flyctl open

# View dashboard
flyctl dashboard
```

## 🗄️ Database Commands

```bash
# Connect to PostgreSQL
flyctl postgres connect -a flowlog-db

# View database list
flyctl postgres db list -a flowlog-db

# View connection info
flyctl postgres db show -a flowlog-db

# Run migrations
flyctl ssh console -C "cd /app && alembic upgrade head"
```

## 🔐 Secrets Management

```bash
# Set a secret
flyctl secrets set SECRET_KEY=your-secret-here

# List secrets (names only, not values)
flyctl secrets list

# Remove a secret
flyctl secrets unset SECRET_KEY

# Set multiple secrets at once
flyctl secrets set \
  SECRET_KEY=xxx \
  ANOTHER_SECRET=yyy
```

## ⚙️ Configuration

```bash
# View current config
flyctl config show

# Edit config
flyctl config save

# View environment variables
flyctl ssh console -C "env"
```

## 📈 Scaling

```bash
# Scale to 2 instances
flyctl scale count 2

# Scale to different VM size
flyctl scale vm shared-cpu-2x

# Scale memory
flyctl scale memory 512
```

## 🔄 Releases & Rollback

```bash
# List releases
flyctl releases

# Rollback to previous version
flyctl releases rollback

# View specific release
flyctl releases show <version>
```

## 🐛 Debugging

```bash
# SSH into container
flyctl ssh console

# Run a command in container
flyctl ssh console -C "python --version"

# View machine info
flyctl machines list

# Restart app
flyctl apps restart
```

## 🌍 Regions & Networking

```bash
# List available regions
flyctl regions list

# Add a region
flyctl regions add lax

# View IP addresses
flyctl ips list

# Allocate IPv4
flyctl ips allocate-v4
```

## 💰 Cost & Usage

```bash
# View app info (includes pricing tier)
flyctl info

# Monitor resource usage
flyctl status

# View volume usage
flyctl volumes list
```

## 🔧 Maintenance

```bash
# Stop app
flyctl apps stop

# Start app
flyctl apps start

# Destroy app (careful!)
flyctl apps destroy flowlog-api

# Create backup of database
flyctl postgres db backup -a flowlog-db
```

## 📱 App Management

```bash
# List all your apps
flyctl apps list

# View app details
flyctl info

# Rename app
flyctl apps rename flowlog-api new-name

# Open app URL
flyctl open /docs
```

## 🔍 Health Checks

```bash
# View health check status
flyctl checks list

# Test health endpoint locally
curl https://flowlog-api.fly.dev/health
```

## 📝 Useful Combinations

```bash
# Deploy and watch logs
flyctl deploy --image ghcr.io/smiileyface/flowlog-api:main && flyctl logs -f

# Quick health check
flyctl ssh console -C "curl localhost:8000/health"

# View recent errors
flyctl logs | grep ERROR

# Run migrations after deploy
flyctl ssh console -C "cd /app && alembic upgrade head"
```

## 🆘 Emergency Commands

```bash
# Force restart if stuck
flyctl machines restart --force

# View machine state
flyctl machines status

# Emergency rollback
flyctl releases rollback

# Check if app is responding
flyctl checks list
```

## 📚 Help

```bash
# General help
flyctl help

# Command-specific help
flyctl deploy --help

# Open documentation
open https://fly.io/docs
```

## 🔗 Important URLs

- Your App: https://flowlog-api.fly.dev
- API Docs: https://flowlog-api.fly.dev/docs
- Dashboard: https://fly.io/dashboard
- Status: https://status.fly.io

---

**Pro Tip:** Add `alias fly=flyctl` to your shell config for shorter commands!
