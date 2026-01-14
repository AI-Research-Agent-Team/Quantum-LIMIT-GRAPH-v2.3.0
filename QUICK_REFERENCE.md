# Quantum LIMIT-GRAPH - Quick Reference

## 🚀 Quick Start Commands

```bash
# Initial Setup
chmod +x setup.sh
./setup.sh

# Start All Services
docker-compose up -d

# Stop All Services
docker-compose down

# View Logs
docker-compose logs -f

# Restart Service
docker-compose restart [service-name]
```

## 🔗 Service URLs

| Service | URL | Credentials |
|---------|-----|-------------|
| Green Agent | http://localhost:8000 | - |
| API Docs | http://localhost:8080/docs | - |
| Dashboard | http://localhost:8501 | - |
| Grafana | http://localhost:3000 | admin / admin |
| Prometheus | http://localhost:9090 | - |
| Flower (Celery) | http://localhost:5555 | - |
| Jaeger | http://localhost:16686 | - |

## 📊 Common API Calls

```bash
# Get Leaderboard
curl http://localhost:8080/api/v1/leaderboard/

# Get Agent Ranking
curl http://localhost:8080/api/v1/leaderboard/agent/AGENT_ID

# Submit Evaluation (requires API key)
curl -X POST http://localhost:8080/api/v1/evaluations \
  -H "X-API-Key: your-api-key" \
  -H "Content-Type: application/json" \
  -d '{"agent_id": "test", "results": {...}}'

# Get Available Metrics
curl http://localhost:8080/api/v1/leaderboard/metrics/available

# Health Check
curl http://localhost:8080/health
```

## 🏃 Benchmark Commands

```bash
# Run All Benchmarks
python benchmarks/runner.py \
  --agent-endpoint http://localhost:8000 \
  --agent-id my-agent

# Run Specific Suite
python benchmarks/runner.py \
  --agent-endpoint http://localhost:8000 \
  --agent-id my-agent \
  --suites multilingual

# Run in Parallel
python benchmarks/runner.py \
  --agent-endpoint http://localhost:8000 \
  --agent-id my-agent \
  --parallel

# Submit to AgentBeats
python benchmarks/runner.py \
  --agent-endpoint http://localhost:8000 \
  --agent-id my-agent \
  --submit https://agentbeats.dev/api/hook/v2/TOKEN
```

## 🗄️ Database Commands

```bash
# Connect to PostgreSQL
docker-compose exec postgres psql -U quantum -d quantum_limit

# Run Migrations
docker-compose exec api alembic upgrade head

# Create Migration
docker-compose exec api alembic revision --autogenerate -m "description"

# Seed Database
docker-compose exec api python scripts/seed_database.py

# Backup Database
docker-compose exec postgres pg_dump -U quantum quantum_limit > backup.sql

# Restore Database
docker-compose exec -T postgres psql -U quantum quantum_limit < backup.sql
```

## 📈 Monitoring Commands

```bash
# View All Logs
docker-compose logs -f

# View Specific Service
docker-compose logs -f green-agent

# View Last 100 Lines
docker-compose logs --tail=100 api

# Export Logs
docker-compose logs > logs/export-$(date +%Y%m%d).log

# Check Resource Usage
docker stats

# View Celery Tasks
docker-compose exec flower celery -A orchestration.worker inspect active
```

## 🔄 Scaling Commands

```bash
# Scale Workers
docker-compose up -d --scale worker=4

# Scale Down
docker-compose up -d --scale worker=1

# Check Worker Count
docker-compose ps worker
```

## 🛠️ Maintenance Commands

```bash
# Update All Services
docker-compose pull
docker-compose up -d

# Rebuild Single Service
docker-compose build --no-cache green-agent
docker-compose up -d green-agent

# Remove Unused Resources
docker system prune -a

# View Disk Usage
docker system df

# Clean Up Volumes
docker-compose down -v
```

## 🐛 Debugging Commands

```bash
# Check Service Health
docker-compose exec green-agent curl http://localhost:8000/health

# Access Container Shell
docker-compose exec green-agent /bin/bash

# Check Environment Variables
docker-compose exec green-agent env

# View Container Processes
docker-compose exec green-agent ps aux

# Check Network Connectivity
docker-compose exec green-agent ping api
```

## 🧪 Testing Commands

```bash
# Run All Tests
pytest tests/ -v

# Run Specific Test
pytest tests/unit/test_agent.py -v

# Run with Coverage
pytest tests/ --cov=. --cov-report=html

# Run Integration Tests
pytest tests/integration/ -v

# Run Load Tests
locust -f tests/load_tests/locustfile.py
```

## 🔑 Environment Variables

```bash
# Essential Variables
OPENAI_API_KEY=sk-...
GOOGLE_API_KEY=...
POSTGRES_PASSWORD=...
REDIS_PASSWORD=...
API_KEY=...
AGENTBEATS_WEBHOOK=https://agentbeats.dev/api/hook/v2/...

# Optional Variables
DEBUG=false
ENVIRONMENT=production
CORS_ORIGINS=*
MAX_WORKERS=4
```

## 📦 Docker Commands

```bash
# Build Images
docker-compose build

# Pull Latest Images
docker-compose pull

# Start Services
docker-compose up -d

# Stop Services
docker-compose stop

# Restart Services
docker-compose restart

# Remove Services
docker-compose down

# Remove with Volumes
docker-compose down -v

# View Running Containers
docker-compose ps

# View All Containers
docker ps -a
```

## 🎯 AgentBeats Integration

```bash
# Register Green Agent
# Visit: https://agentbeats.dev
# Click: Register Agent > Green Agent

# Create Leaderboard Repo
# Use template: https://github.com/RDI-Foundation/leaderboard-template

# Configure Webhook
# Settings > Webhooks > Add webhook
# Payload URL: https://agentbeats.dev/api/hook/v2/TOKEN
# Content type: application/json

# Trigger Evaluation
git commit --allow-empty -m "Trigger evaluation"
git push
```

## 🚨 Emergency Commands

```bash
# Stop Everything Immediately
docker-compose down

# Kill All Containers
docker kill $(docker ps -q)

# Remove All Containers
docker rm $(docker ps -a -q)

# Remove All Images
docker rmi $(docker images -q)

# Nuclear Option (Clean Everything)
docker system prune -a --volumes
```

## 📝 Useful Aliases

Add to your `.bashrc` or `.zshrc`:

```bash
alias dcup='docker-compose up -d'
alias dcdown='docker-compose down'
alias dclogs='docker-compose logs -f'
alias dcps='docker-compose ps'
alias dcrestart='docker-compose restart'
alias dcbuild='docker-compose build --no-cache'

# Quantum LIMIT-GRAPH specific
alias ql-start='docker-compose up -d'
alias ql-stop='docker-compose down'
alias ql-logs='docker-compose logs -f'
alias ql-status='docker-compose ps'
alias ql-bench='python benchmarks/runner.py'
```

## 🔍 Troubleshooting

### Service Won't Start
```bash
# Check logs
docker-compose logs [service-name]

# Check port conflicts
lsof -i :8000  # Green Agent
lsof -i :8080  # API
lsof -i :8501  # Dashboard

# Restart service
docker-compose restart [service-name]
```

### Database Connection Error
```bash
# Check if PostgreSQL is running
docker-compose ps postgres

# Check database health
docker-compose exec postgres pg_isready -U quantum

# Restart database
docker-compose restart postgres
```

### Redis Connection Error
```bash
# Check if Redis is running
docker-compose ps redis

# Test connection
docker-compose exec redis redis-cli ping

# Restart Redis
docker-compose restart redis
```

### API Returns 500
```bash
# Check API logs
docker-compose logs -f api

# Check database connection
docker-compose exec api curl http://postgres:5432

# Restart API
docker-compose restart api
```

## 💡 Pro Tips

1. **Always check logs first**: `docker-compose logs -f [service]`
2. **Use health checks**: All services have `/health` endpoints
3. **Monitor resources**: Use `docker stats` to watch usage
4. **Backup regularly**: Run `./scripts/backup.sh` daily
5. **Test locally first**: Before pushing to production
6. **Use environment files**: Never commit secrets
7. **Scale gradually**: Add workers one at a time
8. **Watch metrics**: Use Grafana dashboards

## 📚 More Information

- Full Documentation: `DEPLOYMENT_GUIDE.md`
- Architecture: `ARCHITECTURE.md`
- Extension Summary: `EXTENSION_SUMMARY.md`
- API Docs: http://localhost:8080/docs
- AgentBeats Tutorial: https://docs.agentbeats.dev/tutorial/

---

**Keep this reference handy for quick commands and troubleshooting!** 🚀
