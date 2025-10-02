# Deployment Setup Summary

## ✅ What's Been Configured

Your Flowlog API is now ready for deployment to Fly.io with full CI/CD automation!

## 📁 Files Created

### Configuration Files
- **`fly.toml`** - Fly.io app configuration
  - App name: `flowlog-api`
  - Region: `iad` (Ashburn, VA)
  - Auto-stop: enabled (saves costs)
  - Health checks configured
  - Secrets handling

### Documentation
- **`docs/FLY_DEPLOYMENT.md`** - Complete deployment guide
- **`docs/DEPLOYMENT_SUMMARY.md`** - This file

### Scripts
- **`scripts/fly-setup.sh`** - Automated initial setup script
  - Makes Fly.io setup one command
  - Handles app creation, database, and secrets

### GitHub Workflows Updated
- **`.github/workflows/docker-build.yml`**
  - Added automatic Fly.io deployment step
  - Triggers after successful GHCR push
  - Only deploys from `main` branch

## 🚀 Deployment Pipeline

Your complete CI/CD pipeline:

```
Developer pushes to main
        ↓
GitHub Actions triggered
        ↓
Run tests (lint, typecheck, pytest)
        ↓
Build Docker image
        ↓
Push to GHCR (ghcr.io/smiileyface/flowlog-api)
        ↓
Security scan (Trivy)
        ↓
Deploy to Fly.io (pulls from GHCR)
        ↓
Live at: flowlog-api.fly.dev
```

## 🔑 What You Need to Do

### 1. Initial Setup (One Time)

```bash
# Install Fly.io CLI
brew install flyctl

# Run the setup script
./scripts/fly-setup.sh
```

This will:
- Create your Fly.io app
- Set up PostgreSQL database
- Configure secrets
- Do the first deployment

### 2. Add Fly.io Token to GitHub (For Auto-Deploy)

```bash
# Get your Fly.io token
flyctl auth token

# Add to GitHub:
# 1. Go to: https://github.com/smiileyface/flowlog-api/settings/secrets/actions
# 2. Click "New repository secret"
# 3. Name: FLY_API_TOKEN
# 4. Value: Paste the token from above
# 5. Click "Add secret"
```

### 3. Push and Watch It Deploy!

```bash
git add .
git commit -m "Add Fly.io deployment"
git push origin main
```

Then watch:
- GitHub Actions: https://github.com/smiileyface/flowlog-api/actions
- Your app will be live at: https://flowlog-api.fly.dev

## 📊 Monitoring Your App

### View Logs
```bash
flyctl logs
```

### Check Status
```bash
flyctl status
```

### Open in Browser
```bash
flyctl open
```

### Access Dashboard
```bash
flyctl dashboard
```

### Database Connection
```bash
# Connect to PostgreSQL
flyctl postgres connect -a flowlog-db

# View connection string
flyctl postgres db list -a flowlog-db
```

## 💰 Cost Estimate

With Fly.io's free tier:
- **Free allowance**: 3 shared VMs + 3GB storage
- **Your setup**: 1 VM (shared-cpu-1x) + PostgreSQL (256MB)
- **Cost**: **FREE** for development/small projects

If you exceed free tier:
- ~$2-5/month for basic production usage
- Pay only for what you use

## 🔄 Making Changes

### Deploy Manually
```bash
flyctl deploy --image ghcr.io/smiileyface/flowlog-api:main
```

### Update Secrets
```bash
flyctl secrets set KEY=VALUE
```

### Scale Up
```bash
flyctl scale count 2  # Run 2 instances
flyctl scale vm shared-cpu-2x  # Upgrade VM
```

### Run Database Migrations
```bash
flyctl ssh console
cd /app
alembic upgrade head
```

## 🆘 Troubleshooting

### Deployment Failed?
```bash
# Check logs
flyctl logs

# Check app status
flyctl status

# Restart app
flyctl apps restart flowlog-api
```

### Database Issues?
```bash
# Check database status
flyctl postgres db list -a flowlog-db

# Connect to database
flyctl postgres connect -a flowlog-db
```

### Need to Rollback?
```bash
# List releases
flyctl releases

# Rollback to previous
flyctl releases rollback
```

## 🎉 Next Steps

1. ✅ Complete initial setup (`./scripts/fly-setup.sh`)
2. ✅ Add `FLY_API_TOKEN` to GitHub secrets
3. ✅ Push to main and watch it deploy
4. ✅ Visit your live API at `https://flowlog-api.fly.dev`
5. ✅ Check API docs at `https://flowlog-api.fly.dev/docs`

## 📚 Additional Resources

- [Fly.io Documentation](https://fly.io/docs/)
- [Fly.io PostgreSQL Guide](https://fly.io/docs/postgres/)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)

## 🔒 Security Notes

- Never commit `.env` or secrets to Git
- `FLY_API_TOKEN` is stored securely in GitHub Secrets
- Database credentials managed by Fly.io
- SECRET_KEY auto-generated during setup
- Docker images scanned for vulnerabilities

---

**You're all set! 🚀 Happy deploying!**
