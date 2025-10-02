# Fly.io Deployment Guide

## Prerequisites

1. Install the Fly.io CLI:
   ```bash
   brew install flyctl
   ```

2. Sign up and log in:
   ```bash
   flyctl auth signup
   # or if you already have an account
   flyctl auth login
   ```

## Initial Setup

### 1. Create the Fly.io App

```bash
# Create the app (this reserves the name)
flyctl apps create flowlog-api

# Or let Fly.io generate a unique name
flyctl apps create
```

### 2. Create PostgreSQL Database

```bash
# Create a Postgres cluster
flyctl postgres create --name flowlog-db --region sjc

# Attach it to your app (this sets DATABASE_URL automatically)
flyctl postgres attach flowlog-db --app flowlog-api
```

### 3. Set Secrets (Environment Variables)

```bash
# Generate a secure secret key
export SECRET_KEY=$(openssl rand -hex 32)

# Set secrets in Fly.io
flyctl secrets set SECRET_KEY="$SECRET_KEY" --app flowlog-api
flyctl secrets set ACCESS_TOKEN_EXPIRE_MINUTES="11520" --app flowlog-api
flyctl secrets set ALGORITHM="HS256" --app flowlog-api
flyctl secrets set BACKEND_CORS_ORIGINS='["https://your-frontend-domain.com"]' --app flowlog-api
```

### 4. Configure GitHub Package Access

For Fly.io to pull your Docker image from GHCR:

```bash
# Create a GitHub Personal Access Token (PAT)
# Go to: GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic)
# Create a token with 'read:packages' scope

# Set the registry authentication in Fly.io
flyctl secrets set REGISTRY_USERNAME="smiileyface" --app flowlog-api
flyctl secrets set REGISTRY_PASSWORD="your_github_pat" --app flowlog-api
```

### 5. Deploy Manually (First Time)

```bash
# Deploy from GHCR
flyctl deploy --app flowlog-api --image ghcr.io/smiileyface/flowlog-api:main

# Or deploy and watch logs
flyctl deploy --app flowlog-api --image ghcr.io/smiileyface/flowlog-api:main && flyctl logs
```

## Automatic Deployments via GitHub Actions

Once you've set up the Fly.io API token (see below), every push to `main` will automatically:
1. Run tests
2. Build Docker image
3. Push to GHCR
4. Deploy to Fly.io

### Setup GitHub Actions Deploy Token

```bash
# Create a deploy token
flyctl auth token

# Add this token to GitHub:
# 1. Go to your repo → Settings → Secrets and variables → Actions
# 2. Click "New repository secret"
# 3. Name: FLY_API_TOKEN
# 4. Value: (paste the token from above)
# 5. Click "Add secret"
```

## Useful Commands

```bash
# View app status
flyctl status --app flowlog-api

# View logs (live)
flyctl logs --app flowlog-api

# SSH into the running app
flyctl ssh console --app flowlog-api

# Scale the app
flyctl scale count 2 --app flowlog-api  # Run 2 instances
flyctl scale vm shared-cpu-1x --memory 512 --app flowlog-api  # Bigger VM

# View secrets
flyctl secrets list --app flowlog-api

# Open app in browser
flyctl open --app flowlog-api

# View dashboard
flyctl dashboard --app flowlog-api

# Run a one-off command
flyctl ssh console --app flowlog-api -C "alembic upgrade head"

# Check Postgres
flyctl postgres connect --app flowlog-db
```

## Database Migrations

Migrations run automatically on deploy via the `release_command` in `fly.toml`.

To run migrations manually:
```bash
flyctl ssh console --app flowlog-api -C "alembic upgrade head"
```

## Monitoring

```bash
# Real-time metrics
flyctl dashboard --app flowlog-api

# Check health
flyctl checks list --app flowlog-api
```

## Troubleshooting

### View deployment logs
```bash
flyctl logs --app flowlog-api
```

### Check app configuration
```bash
flyctl config show --app flowlog-api
```

### Restart the app
```bash
flyctl apps restart flowlog-api
```

### Check database connection
```bash
flyctl ssh console --app flowlog-api -C "python -c 'from app.db.session import engine; print(engine.url)'"
```

## Costs

- **Free tier**: 3 shared-cpu-1x VMs with 256MB RAM each
- **Postgres**: Free for development (single node, 256MB RAM)
- For production: ~$2-5/month for small apps

## Regions

Available regions (change in `fly.toml`):
- `sjc` - San Jose, California
- `iad` - Ashburn, Virginia
- `lhr` - London
- `fra` - Frankfurt
- `syd` - Sydney
- More: https://fly.io/docs/reference/regions/

## Production Checklist

- [ ] Set proper CORS origins
- [ ] Configure proper SECRET_KEY
- [ ] Set DEBUG=False (already in fly.toml)
- [ ] Scale to multiple regions if needed
- [ ] Set up backups for PostgreSQL
- [ ] Configure custom domain (if needed)
- [ ] Enable monitoring/alerts
- [ ] Review security headers

## Custom Domain (Optional)

```bash
# Add a custom domain
flyctl certs create yourdomain.com --app flowlog-api

# Add DNS records as instructed by Fly.io
# Then verify
flyctl certs show yourdomain.com --app flowlog-api
```

## Scaling

```bash
# Auto-scale based on load (already configured in fly.toml)
# Adjust in fly.toml: min_machines_running and auto_start_machines

# Manual scaling
flyctl scale count 2  # Run 2 instances
flyctl scale vm shared-cpu-2x --memory 512  # Bigger VM
```

## Support

- Documentation: https://fly.io/docs/
- Community: https://community.fly.io/
- Status: https://status.flyio.net/
