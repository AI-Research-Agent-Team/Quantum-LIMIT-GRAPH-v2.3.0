# Quantum LIMIT-GRAPH Extended - Deployment Guide

Complete guide for deploying the extended Quantum LIMIT-GRAPH system with all components integrated with AgentBeats.

## 📋 Table of Contents

1. [Prerequisites](#prerequisites)
2. [Quick Start](#quick-start)
3. [Component-by-Component Setup](#component-setup)
4. [AgentBeats Integration](#agentbeats-integration)
5. [Production Deployment](#production-deployment)
6. [Monitoring & Maintenance](#monitoring)
7. [Troubleshooting](#troubleshooting)

## 🎯 Prerequisites

### Required Software
- Docker 20.10+
- Docker Compose 2.0+
- Python 3.11+
- Git
- 8GB+ RAM
- 50GB+ disk space

### Required Accounts
- GitHub account (for Actions and GHCR)
- AgentBeats account (register at https://agentbeats.dev)
- API keys:
  - OpenAI (or Google Gemini)
  - Optional: Anthropic Claude

### System Requirements

| Component | CPU | RAM | Disk |
|-----------|-----|-----|------|
| Green Agent | 2 cores | 4GB | 10GB |
| API Server | 2 cores | 2GB | 5GB |
| Dashboard | 1 core | 1GB | 2GB |
| PostgreSQL | 2 cores | 4GB | 20GB |
| Redis | 1 core | 2GB | 5GB |
| Workers (x2) | 4 cores | 8GB | 10GB |
| **Total** | **12 cores** | **21GB** | **52GB** |

## 🚀 Quick Start (Development)

### 1. Clone and Setup

```bash
# Clone repository
git clone https://github.com/YOUR_USERNAME/Quantum-LIMIT-GRAPH-v2.3.0.git
cd Quantum-LIMIT-GRAPH-v2.3.0

# Create environment file
cp .env.example .env

# Edit .env with your API keys
nano .env
```

### 2. Configure Environment

Edit `.env`:

```bash
# API Keys
OPENAI_API_KEY=sk-your-openai-key
GOOGLE_API_KEY=your-google-key

# Database
POSTGRES_USER=quantum
POSTGRES_PASSWORD=your_secure_password
POSTGRES_DB=quantum_limit

# Redis
REDIS_PASSWORD=your_redis_password

# API
API_KEY=your-api-key-for-protected-endpoints

# AgentBeats
AGENTBEATS_WEBHOOK=https://agentbeats.dev/api/hook/v2/YOUR_TOKEN
AGENT_CARD_URL=https://your-public-url:8000

# Optional
DEBUG=false
CORS_ORIGINS=*
```

### 3. Start All Services

```bash
# Build and start all containers
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f
```

### 4. Verify Services

```bash
# Green Agent
curl http://localhost:8000/.well-known/agent-card.json

# API
curl http://localhost:8080/health

# Dashboard
open http://localhost:8501

# Grafana
open http://localhost:3000
# Login: admin / admin (change password!)
```

## 🔧 Component-by-Component Setup

### A. Database Setup

```bash
# Initialize database
docker-compose exec postgres psql -U quantum -d quantum_limit

# Run migrations
docker-compose exec api alembic upgrade head

# Seed test data
docker-compose exec api python scripts/seed_database.py
```

### B. Green Agent Setup

```bash
# Test green agent locally
python server.py

# Or with Docker
docker-compose up green-agent

# Verify A2A endpoint
curl http://localhost:8000/.well-known/agent-card.json | jq .
```

### C. API Setup

```bash
# Test API locally
cd api && python main.py

# Or with Docker
docker-compose up api

# Test endpoints
curl http://localhost:8080/api/v1/leaderboard/
curl http://localhost:8080/api/v1/metrics/available
```

### D. Dashboard Setup

```bash
# Run dashboard locally
cd dashboard && streamlit run app.py

# Or with Docker
docker-compose up dashboard

# Access at http://localhost:8501
```

### E. Workers Setup

```bash
# Start Celery workers
docker-compose up -d worker beat flower

# Monitor workers
open http://localhost:5555  # Flower UI

# Test async task
python -c "
from orchestration.worker import example_task
result = example_task.delay('test')
print(f'Task ID: {result.id}')
"
```

## 🔗 AgentBeats Integration

### Step 1: Register Green Agent

1. Go to https://agentbeats.dev
2. Click "Register Agent"
3. Select "Green Agent" (Evaluator)
4. Fill in details:
   ```
   Display Name: Quantum LIMIT-GRAPH Benchmark
   Docker Image: ghcr.io/YOUR_USERNAME/quantum-limit-graph:latest
   Repository: https://github.com/YOUR_USERNAME/Quantum-LIMIT-GRAPH-v2.3.0
   ```
5. Copy the Agent ID (you'll need this)

### Step 2: Create Leaderboard Repository

```bash
# Use the leaderboard template
# Visit: https://github.com/RDI-Foundation/leaderboard-template
# Click "Use this template"

# Clone your new leaderboard repo
git clone https://github.com/YOUR_USERNAME/quantum-limit-leaderboard.git
cd quantum-limit-leaderboard

# Configure scenario.toml
cat > scenario.toml << 'EOF'
[green_agent]
id = "YOUR_GREEN_AGENT_ID"  # From AgentBeats
image = "ghcr.io/YOUR_USERNAME/quantum-limit-graph:latest"
env = { OPENAI_API_KEY = "${OPENAI_API_KEY}" }

[participants.purple_agent]
id = "YOUR_PURPLE_AGENT_ID"
image = "ghcr.io/YOUR_USERNAME/purple-agent:latest"

[config]
test_queries = [
    "What is quantum machine learning?",
    "¿Qué es el aprendizaje automático cuántico?",
    "什么是量子机器学习？"
]
EOF

# Commit and push
git add scenario.toml
git commit -m "Configure evaluation scenario"
git push
```

### Step 3: Connect Leaderboard to Agent

1. On AgentBeats, edit your green agent
2. Add leaderboard repository URL
3. Add this GraphQL query for leaderboard config:

```graphql
{
  assessment(id: "{{assessment_id}}") {
    results
    artifacts {
      name
      data
    }
  }
}
```

### Step 4: Setup Webhook

```bash
# In your leaderboard repo, go to Settings > Webhooks
# Add webhook:
Payload URL: https://agentbeats.dev/api/hook/v2/YOUR_TOKEN
Content type: application/json
Secret: (leave empty)
Events: Select "Workflow runs"
```

### Step 5: Run First Evaluation

```bash
# In leaderboard repo
git commit --allow-empty -m "Trigger evaluation"
git push

# Watch progress:
# 1. GitHub Actions tab
# 2. AgentBeats dashboard
# 3. Your leaderboard updates automatically
```

## 📊 Benchmark Execution

### Local Benchmark Run

```bash
# Run benchmarks against an agent
python benchmarks/runner.py \
  --agent-endpoint http://localhost:8001 \
  --agent-id test-agent-001 \
  --suites multilingual quantum hallucination \
  --output-dir ./results \
  --submit https://agentbeats.dev/api/hook/v2/YOUR_TOKEN
```

### Automated Nightly Benchmarks

GitHub Actions workflow (`.github/workflows/benchmark-nightly.yml`):

```yaml
name: Nightly Benchmarks

on:
  schedule:
    - cron: '0 2 * * *'  # 2 AM UTC daily
  workflow_dispatch:

jobs:
  benchmark:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Run benchmarks
        run: |
          docker-compose up -d
          python benchmarks/runner.py \
            --agent-endpoint http://green-agent:8000 \
            --agent-id nightly-baseline \
            --submit ${{ secrets.AGENTBEATS_WEBHOOK }}
      
      - name: Upload results
        uses: actions/upload-artifact@v3
        with:
          name: benchmark-results
          path: benchmark_results/
```

## 🏭 Production Deployment

### Option 1: Docker Compose Production

```bash
# Use production compose file
docker-compose -f docker-compose.prod.yml up -d

# With resource limits and healthchecks
docker-compose -f docker-compose.prod.yml \
  --env-file .env.production \
  up -d
```

### Option 2: Kubernetes Deployment

```bash
# Create namespace
kubectl create namespace quantum-limit

# Apply secrets
kubectl create secret generic quantum-secrets \
  --from-file=.env.production \
  -n quantum-limit

# Deploy all components
kubectl apply -f k8s/ -n quantum-limit

# Check status
kubectl get pods -n quantum-limit

# Access dashboard
kubectl port-forward svc/dashboard 8501:8501 -n quantum-limit
```

### Option 3: Cloud Deployment (AWS/GCP/Azure)

#### AWS ECS

```bash
# Build and push images
aws ecr create-repository --repository-name quantum-limit-graph
docker build -t quantum-limit-graph .
docker tag quantum-limit-graph:latest \
  AWS_ACCOUNT.dkr.ecr.REGION.amazonaws.com/quantum-limit-graph:latest
docker push AWS_ACCOUNT.dkr.ecr.REGION.amazonaws.com/quantum-limit-graph:latest

# Deploy with ECS
aws ecs create-service \
  --cluster quantum-cluster \
  --service-name quantum-limit \
  --task-definition quantum-limit-task \
  --desired-count 2
```

## 📈 Monitoring & Observability

### Prometheus Metrics

Access Prometheus at http://localhost:9090

Key metrics to monitor:
- `http_requests_total` - Total HTTP requests
- `evaluation_duration_seconds` - Evaluation latency
- `worker_tasks_total` - Worker task count
- `database_connections` - DB connection pool

### Grafana Dashboards

1. Access Grafana at http://localhost:3000
2. Login: admin / admin
3. Pre-configured dashboards:
   - **System Overview**: Resource utilization
   - **API Metrics**: Request rates, latency
   - **Worker Metrics**: Task queue, success rates
   - **Evaluation Metrics**: Benchmark performance

### Jaeger Tracing

Access Jaeger UI at http://localhost:16686

View distributed traces for:
- Complete evaluation flows
- API request chains
- Worker task execution
- Database queries

### Logging

```bash
# View all logs
docker-compose logs -f

# Specific service
docker-compose logs -f green-agent

# Filter by level
docker-compose logs -f | grep ERROR

# Export logs
docker-compose logs > logs/deployment-$(date +%Y%m%d).log
```

## 🔧 Maintenance

### Backup Database

```bash
# Automated backup
./scripts/backup.sh

# Manual backup
docker-compose exec postgres pg_dump -U quantum quantum_limit > backup.sql

# Restore
docker-compose exec -T postgres psql -U quantum quantum_limit < backup.sql
```

### Update Deployment

```bash
# Pull latest changes
git pull origin main

# Rebuild images
docker-compose build --no-cache

# Rolling update
docker-compose up -d --no-deps green-agent api

# Or update all
docker-compose up -d
```

### Scale Workers

```bash
# Scale to 4 workers
docker-compose up -d --scale worker=4

# Or in docker-compose.yml
deploy:
  replicas: 4
```

## 🐛 Troubleshooting

### Green Agent Won't Start

```bash
# Check logs
docker-compose logs green-agent

# Common issues:
# 1. Missing API keys
docker-compose exec green-agent env | grep API_KEY

# 2. Database not ready
docker-compose exec postgres pg_isready

# 3. Port conflict
lsof -i :8000
```

### Leaderboard Not Updating

```bash
# Check webhook delivery on GitHub
# Settings > Webhooks > Recent Deliveries

# Verify AgentBeats connection
curl -X POST https://agentbeats.dev/api/hook/v2/YOUR_TOKEN \
  -H "Content-Type: application/json" \
  -d '{"test": true}'

# Check API webhook handler
docker-compose logs api | grep webhook
```

### Dashboard Shows No Data

```bash
# Check API connectivity
docker-compose exec dashboard curl http://api:8080/health

# Check database
docker-compose exec postgres psql -U quantum -d quantum_limit \
  -c "SELECT COUNT(*) FROM evaluations;"

# Restart dashboard
docker-compose restart dashboard
```

## 📚 Additional Resources

- [AgentBeats Tutorial](https://docs.agentbeats.dev/tutorial/)
- [A2A Protocol Spec](https://a2a-protocol.org/latest/specification/)
- [API Documentation](http://localhost:8080/docs)
- [Architecture Diagram](./docs/architecture.md)

## ✅ Deployment Checklist

- [ ] All environment variables configured
- [ ] API keys added to secrets
- [ ] Database initialized and migrated
- [ ] All services healthy
- [ ] Green agent registered on AgentBeats
- [ ] Leaderboard repository created
- [ ] Webhook configured
- [ ] First evaluation runs successfully
- [ ] Monitoring dashboards accessible
- [ ] Backup script scheduled
- [ ] Documentation reviewed
- [ ] Team trained on operations

---

**You now have a complete, production-ready deployment of Quantum LIMIT-GRAPH integrated with AgentBeats! 🚀**
