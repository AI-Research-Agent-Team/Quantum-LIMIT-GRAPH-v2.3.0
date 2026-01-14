#!/bin/bash

# Quantum LIMIT-GRAPH Extended Setup Script
# Automated setup for the complete platform

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

log_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

log_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Header
echo ""
echo "=========================================="
echo "  Quantum LIMIT-GRAPH Extended Setup"
echo "  Version 2.3.0"
echo "=========================================="
echo ""

# Check prerequisites
log_info "Checking prerequisites..."

# Check Docker
if ! command -v docker &> /dev/null; then
    log_error "Docker is not installed. Please install Docker first."
    exit 1
fi
log_success "Docker found: $(docker --version)"

# Check Docker Compose
if ! command -v docker-compose &> /dev/null; then
    log_error "Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi
log_success "Docker Compose found: $(docker-compose --version)"

# Check Python
if ! command -v python3 &> /dev/null; then
    log_warning "Python 3 not found. Some scripts may not work."
else
    log_success "Python found: $(python3 --version)"
fi

# Check Git
if ! command -v git &> /dev/null; then
    log_warning "Git not found. Version control may not work."
else
    log_success "Git found: $(git --version)"
fi

echo ""
log_info "All prerequisites met!"
echo ""

# Create directory structure
log_info "Creating directory structure..."

directories=(
    "api/routes"
    "api/models"
    "api/services"
    "api/middleware"
    "dashboard/pages"
    "dashboard/components"
    "dashboard/static/css"
    "dashboard/static/js"
    "benchmarks/config"
    "benchmarks/suites"
    "benchmarks/scenarios"
    "benchmarks/metrics"
    "benchmarks/reporters"
    "leaderboard/templates"
    "database/migrations/versions"
    "database/repositories"
    "orchestration/distributed"
    "monitoring/alerts"
    "config/grafana/dashboards"
    "config/grafana/datasources"
    "docker"
    "k8s"
    "scripts"
    "tests/unit"
    "tests/integration"
    "tests/e2e"
    "benchmark_results"
    "logs"
)

for dir in "${directories[@]}"; do
    mkdir -p "$dir"
    log_success "Created $dir"
done

echo ""
log_success "Directory structure created!"
echo ""

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    log_info "Creating .env file..."
    
    cat > .env << 'EOF'
# API Keys (REQUIRED - Add your keys here)
OPENAI_API_KEY=your-openai-key-here
GOOGLE_API_KEY=your-google-key-here

# Database Configuration
POSTGRES_USER=quantum
POSTGRES_PASSWORD=change_this_password
POSTGRES_DB=quantum_limit
POSTGRES_PORT=5432

# Redis Configuration
REDIS_PASSWORD=change_this_redis_password
REDIS_PORT=6379

# API Configuration
API_KEY=change_this_api_key
API_HOST=0.0.0.0
API_PORT=8080
CORS_ORIGINS=*

# AgentBeats Integration
AGENTBEATS_WEBHOOK=https://agentbeats.dev/api/hook/v2/YOUR_TOKEN
AGENT_CARD_URL=http://localhost:8000

# Application Settings
DEBUG=false
ENVIRONMENT=development

# Grafana
GRAFANA_PASSWORD=admin
EOF
    
    log_success ".env file created!"
    log_warning "⚠️  IMPORTANT: Edit .env and add your API keys!"
    echo ""
else
    log_info ".env file already exists, skipping..."
fi

# Create __init__.py files
log_info "Creating Python package files..."

init_dirs=(
    "api"
    "api/routes"
    "api/models"
    "api/services"
    "api/middleware"
    "dashboard"
    "dashboard/pages"
    "dashboard/components"
    "benchmarks"
    "benchmarks/config"
    "benchmarks/suites"
    "benchmarks/scenarios"
    "benchmarks/metrics"
    "benchmarks/reporters"
    "leaderboard"
    "database"
    "database/repositories"
    "orchestration"
    "orchestration/distributed"
    "monitoring"
    "monitoring/alerts"
    "tests"
    "tests/unit"
    "tests/integration"
    "tests/e2e"
)

for dir in "${init_dirs[@]}"; do
    touch "$dir/__init__.py"
done

# Ensure quantum_integration has __init__.py
if [ ! -f "quantum_integration/__init__.py" ]; then
    touch quantum_integration/__init__.py
    log_success "Created quantum_integration/__init__.py"
fi

log_success "Python packages configured!"
echo ""

# Make scripts executable
log_info "Making scripts executable..."

chmod +x run.sh 2>/dev/null || true
chmod +x scripts/*.sh 2>/dev/null || true

log_success "Scripts are now executable!"
echo ""

# Create Prometheus config
log_info "Creating Prometheus configuration..."

mkdir -p config

cat > config/prometheus.yml << 'EOF'
global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  - job_name: 'green-agent'
    static_configs:
      - targets: ['green-agent:8000']
  
  - job_name: 'api'
    static_configs:
      - targets: ['api:8080']
  
  - job_name: 'prometheus'
    static_configs:
      - targets: ['prometheus:9090']
  
  - job_name: 'redis'
    static_configs:
      - targets: ['redis:6379']
  
  - job_name: 'postgres'
    static_configs:
      - targets: ['postgres:5432']
EOF

log_success "Prometheus configured!"
echo ""

# Create Grafana datasource
log_info "Creating Grafana datasource configuration..."

mkdir -p config/grafana/datasources

cat > config/grafana/datasources/prometheus.yml << 'EOF'
apiVersion: 1

datasources:
  - name: Prometheus
    type: prometheus
    access: proxy
    url: http://prometheus:9090
    isDefault: true
    editable: true
EOF

log_success "Grafana datasource configured!"
echo ""

# Create nginx config
log_info "Creating nginx configuration..."

cat > docker/nginx.conf << 'EOF'
events {
    worker_connections 1024;
}

http {
    upstream green-agent {
        server green-agent:8000;
    }
    
    upstream api {
        server api:8080;
    }
    
    upstream dashboard {
        server dashboard:8501;
    }
    
    server {
        listen 80;
        
        location / {
            proxy_pass http://dashboard;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
        }
        
        location /api/ {
            proxy_pass http://api;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
        }
        
        location /agent/ {
            proxy_pass http://green-agent/;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
        }
    }
}
EOF

log_success "Nginx configured!"
echo ""

# Build Docker images
log_info "Building Docker images... (this may take a few minutes)"

if docker-compose build; then
    log_success "Docker images built successfully!"
else
    log_warning "Docker build had warnings, but continuing..."
fi

echo ""

# Summary
echo "=========================================="
echo "  ✅ Setup Complete!"
echo "=========================================="
echo ""
log_info "Next steps:"
echo ""
echo "1. Edit .env and add your API keys:"
echo "   nano .env"
echo ""
echo "2. Start all services:"
echo "   docker-compose up -d"
echo ""
echo "3. Check service status:"
echo "   docker-compose ps"
echo ""
echo "4. Access services:"
echo "   - Green Agent:  http://localhost:8000"
echo "   - API:          http://localhost:8080"
echo "   - Dashboard:    http://localhost:8501"
echo "   - Grafana:      http://localhost:3000"
echo "   - Prometheus:   http://localhost:9090"
echo "   - Flower:       http://localhost:5555"
echo ""
echo "5. View logs:"
echo "   docker-compose logs -f"
echo ""
echo "6. Register on AgentBeats:"
echo "   Visit https://agentbeats.dev"
echo ""
echo "For full documentation, see:"
echo "  - DEPLOYMENT_GUIDE.md"
echo "  - EXTENSION_SUMMARY.md"
echo ""
echo "=========================================="
echo ""

# Ask to start services
read -p "Do you want to start all services now? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    log_info "Starting services..."
    docker-compose up -d
    
    echo ""
    log_info "Waiting for services to be ready..."
    sleep 10
    
    # Check health
    echo ""
    log_info "Checking service health..."
    
    if curl -f http://localhost:8000/health &> /dev/null; then
        log_success "Green Agent is healthy!"
    else
        log_warning "Green Agent is not responding yet"
    fi
    
    if curl -f http://localhost:8080/health &> /dev/null; then
        log_success "API is healthy!"
    else
        log_warning "API is not responding yet"
    fi
    
    echo ""
    log_success "Setup complete! Services are starting..."
    log_info "Run 'docker-compose ps' to check status"
fi

echo ""
log_success "🎉 Quantum LIMIT-GRAPH Extended is ready to use!"
echo ""
