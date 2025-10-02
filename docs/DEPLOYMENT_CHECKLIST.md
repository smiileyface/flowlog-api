# Deployment Checklist

Use this checklist to ensure everything is set up correctly for Fly.io deployment.

## ✅ Pre-Deployment Checklist

### Local Development
- [ ] All tests passing (`make test`)
- [ ] Code linted and formatted (`make check`)
- [ ] Type checking passes (`make typecheck`)
- [ ] `.env` file configured (not committed!)
- [ ] `.env.example` up to date
- [ ] Database migrations work (`make migrate`)
- [ ] App runs locally (`make start p=dev`)

### GitHub Setup
- [ ] Repository pushed to GitHub
- [ ] GitHub Actions workflows present (`.github/workflows/`)
- [ ] CI workflow running successfully
- [ ] Docker image building and pushing to GHCR
- [ ] All secrets NOT committed to repository

### Fly.io CLI
- [ ] Fly.io CLI installed (`brew install flyctl`)
- [ ] Logged into Fly.io (`flyctl auth login`)
- [ ] Fly.io account verified

## 🚀 Initial Deployment Checklist

### Setup Process
- [ ] Run setup script: `./scripts/fly-setup.sh`
  - [ ] App created on Fly.io
  - [ ] PostgreSQL database created
  - [ ] Database attached to app
  - [ ] Secrets configured
  - [ ] First deployment successful

### Verify Deployment
- [ ] App accessible at: https://flowlog-api.fly.dev
- [ ] Health endpoint works: https://flowlog-api.fly.dev/health
- [ ] API docs accessible: https://flowlog-api.fly.dev/docs
- [ ] Database connected (check logs: `flyctl logs`)

### GitHub Integration
- [ ] Get Fly.io token: `flyctl auth token`
- [ ] Add token to GitHub:
  - [ ] Go to repo Settings → Secrets and variables → Actions
  - [ ] Add secret: `FLY_API_TOKEN`
  - [ ] Paste token value
- [ ] Test auto-deploy:
  - [ ] Make a small change
  - [ ] Push to main
  - [ ] Verify GitHub Action runs
  - [ ] Verify app updates on Fly.io

## 🔧 Configuration Checklist

### Environment Variables
- [ ] `SECRET_KEY` set (auto-generated in setup)
- [ ] `DATABASE_URL` set (auto-configured by Fly.io)
- [ ] `ENVIRONMENT` set to "production"
- [ ] `DEBUG` set to "False"
- [ ] `LOG_LEVEL` appropriate for production
- [ ] `BACKEND_CORS_ORIGINS` configured for your frontend

### Database
- [ ] Migrations applied: `flyctl ssh console -C "cd /app && alembic upgrade head"`
- [ ] Can connect: `flyctl postgres connect -a flowlog-db`
- [ ] Database has data (if applicable)

### Monitoring
- [ ] Health checks configured in `fly.toml`
- [ ] Can view logs: `flyctl logs`
- [ ] Can view status: `flyctl status`
- [ ] Dashboard accessible: `flyctl dashboard`

## 🔒 Security Checklist

### Secrets Management
- [ ] `.env` in `.gitignore`
- [ ] No secrets in code
- [ ] Strong `SECRET_KEY` generated
- [ ] Database password secure (managed by Fly.io)
- [ ] Fly.io secrets configured: `flyctl secrets list`

### Access Control
- [ ] GitHub repository access controlled
- [ ] Fly.io organization permissions set
- [ ] `FLY_API_TOKEN` secured in GitHub Secrets
- [ ] Database not publicly accessible

### Code Security
- [ ] Dependencies up to date
- [ ] Dependabot enabled
- [ ] CodeQL security scanning enabled
- [ ] Docker vulnerability scanning enabled (Trivy)

## 📊 Post-Deployment Checklist

### Testing in Production
- [ ] GET `/` returns welcome message
- [ ] GET `/health` returns healthy status
- [ ] GET `/docs` shows API documentation
- [ ] API endpoints responding correctly
- [ ] Database queries working
- [ ] Logs showing no errors

### Performance
- [ ] App starts within health check timeout
- [ ] Response times acceptable
- [ ] Database queries optimized
- [ ] No memory leaks (monitor logs)

### Monitoring Setup
- [ ] Regular log checks scheduled
- [ ] Error alerting configured (optional)
- [ ] Uptime monitoring (optional)
- [ ] Cost monitoring (Fly.io dashboard)

## 🔄 Ongoing Maintenance Checklist

### Regular Tasks
- [ ] Monitor logs weekly: `flyctl logs`
- [ ] Check app status: `flyctl status`
- [ ] Review GitHub Actions runs
- [ ] Update dependencies (Dependabot PRs)
- [ ] Review security alerts

### Before Each Deployment
- [ ] Tests passing locally
- [ ] Code reviewed
- [ ] Breaking changes documented
- [ ] Database migrations ready
- [ ] Rollback plan in place

### After Each Deployment
- [ ] Verify deployment success
- [ ] Check logs for errors
- [ ] Test critical endpoints
- [ ] Monitor for issues
- [ ] Update documentation if needed

## 🆘 Troubleshooting Checklist

### If Deployment Fails
- [ ] Check GitHub Actions logs
- [ ] Verify GHCR image exists
- [ ] Check Fly.io logs: `flyctl logs`
- [ ] Verify secrets are set: `flyctl secrets list`
- [ ] Check app status: `flyctl status`
- [ ] Try manual deploy: `flyctl deploy --image ghcr.io/smiileyface/flowlog-api:main`

### If App Not Responding
- [ ] Check health endpoint: `curl https://flowlog-api.fly.dev/health`
- [ ] View logs: `flyctl logs`
- [ ] Check machine status: `flyctl machines list`
- [ ] Restart app: `flyctl apps restart`
- [ ] Verify database connection
- [ ] Check resources (CPU/memory)

### If Database Issues
- [ ] Verify connection: `flyctl postgres connect -a flowlog-db`
- [ ] Check migrations: `flyctl ssh console -C "cd /app && alembic current"`
- [ ] Run migrations: `flyctl ssh console -C "cd /app && alembic upgrade head"`
- [ ] Check database logs: `flyctl logs -a flowlog-db`

## 📝 Documentation Checklist

- [ ] README.md updated with deployment info
- [ ] FLY_DEPLOYMENT.md reviewed
- [ ] DEPLOYMENT_SUMMARY.md reviewed
- [ ] FLY_COMMANDS.md bookmarked for reference
- [ ] Team members informed of deployment process

## 🎉 Success Criteria

Your deployment is successful when:
- ✅ App is accessible at https://flowlog-api.fly.dev
- ✅ All API endpoints working
- ✅ Database connected and functioning
- ✅ Automatic deployments from GitHub working
- ✅ Health checks passing
- ✅ No errors in logs
- ✅ Team can access and use the API

---

**Once all checkboxes are complete, you're ready for production! 🚀**
