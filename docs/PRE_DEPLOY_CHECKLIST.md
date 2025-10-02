# Pre-Deployment Verification Checklist

## ✅ Critical Requirements

Before pushing, verify these are in place:

### 1. GitHub Secrets
- [ ] `FLY_API_TOKEN` is set in GitHub repository secrets
  - Go to: Settings → Secrets and variables → Actions → New repository secret
  - Get token: `flyctl auth token`

### 2. Fly.io Setup
- [ ] Fly.io app created: `flowlog-api`
- [ ] PostgreSQL database created and attached
- [ ] Database URL automatically set by Fly.io
- [ ] SECRET_KEY set in Fly.io secrets

### 3. Files Modified
- [x] `Dockerfile` - Python 3.12, explicit file copies, urllib healthcheck
- [x] `.github/workflows/docker-build.yml` - Build, tag, and deploy workflow
- [x] `fly.toml` - Fly.io configuration (no hardcoded image)

## 🔍 What Happens On Push

### Build Job:
1. ✅ Runs tests (via CI workflow separately)
2. ✅ Builds Docker image
3. ✅ Tags with:
   - `main` (branch name)
   - `sha-abc1234` (7-char commit hash)
4. ✅ Pushes to GHCR
5. ✅ Runs Trivy security scan
6. ✅ Uploads security results

### Deploy Job:
1. ✅ Waits for build to complete
2. ✅ Pulls image: `ghcr.io/smiileyface/flowlog-api:sha-abc1234`
3. ✅ Deploys to Fly.io
4. ✅ Fly.io runs: `alembic upgrade head`
5. ✅ Starts application

## 🐛 Common Issues & Solutions

### Issue: "Module not found: alembic"
**Solution:** ✅ Fixed - Alembic is in main dependencies and files are explicitly copied

### Issue: "Image not found"
**Solution:** ✅ Fixed - Using correct SHA tag format from build outputs

### Issue: "Resource not accessible by integration"
**Solution:** ✅ Fixed - Added `security-events: write` permission

### Issue: "Healthcheck fails"
**Solution:** ✅ Fixed - Using urllib (built-in) instead of requests

### Issue: "FLY_API_TOKEN not found"
**Solution:** Must add token to GitHub secrets manually

## 📋 Quick Deploy Commands

### Deploy Manually (bypass GitHub Actions)
```bash
# Build locally
docker build -t ghcr.io/smiileyface/flowlog-api:manual .

# Push to GHCR
docker push ghcr.io/smiileyface/flowlog-api:manual

# Deploy to Fly.io
flyctl deploy --image ghcr.io/smiileyface/flowlog-api:manual
```

### Rollback to Previous Version
```bash
# List releases
flyctl releases

# Rollback
flyctl releases rollback
```

### Check Logs After Deploy
```bash
flyctl logs
```

## ✨ Expected Flow

```
git commit -m "Your changes"
git push origin main
    ↓
GitHub Actions: CI workflow runs (tests)
    ↓
GitHub Actions: Docker Build workflow runs
    ↓
Build Docker image (runtime stage)
    ↓
Tag: main, sha-abc1234
    ↓
Push to ghcr.io/smiileyface/flowlog-api
    ↓
Trivy security scan
    ↓
Deploy to Fly.io using sha-abc1234 tag
    ↓
Fly.io: Run migrations (alembic upgrade head)
    ↓
Fly.io: Start app (uvicorn with 4 workers)
    ↓
Health check passes (/health endpoint)
    ↓
🎉 Live at: https://flowlog-api.fly.dev
```

## 🚨 Before First Deploy

Run the setup script if you haven't:
```bash
./scripts/fly-setup.sh
```

This creates:
- Fly.io app
- PostgreSQL database
- Secrets (SECRET_KEY)
- Initial deployment

## ✅ Ready to Deploy?

If all checkboxes above are checked, you're ready to push! 🚀

```bash
git add .
git commit -m "Fix Dockerfile and deployment configuration"
git push origin main
```

Then watch:
- GitHub Actions: https://github.com/smiileyface/flowlog-api/actions
- Fly.io Dashboard: https://fly.io/dashboard
