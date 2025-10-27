#!/bin/bash

###############################################################################
# TRAFFIC SHARE - COMPLETE BUILD SCRIPT
# VPS: 185.139.230.196
# Ubuntu 24.04
###############################################################################

set -e  # Exit on error

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Functions
print_header() {
    echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
    echo -e "${BLUE}  $1${NC}"
    echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

###############################################################################
# 1. SYSTEM CHECK
###############################################################################

print_header "1. SYSTEM CHECK"

# Check if running on Ubuntu
if [[ ! -f /etc/os-release ]] || ! grep -q "Ubuntu" /etc/os-release; then
    print_error "This script is designed for Ubuntu"
    exit 1
fi

print_success "Operating System: $(lsb_release -d | cut -f2)"

# Check Python version
if command -v python3.11 &> /dev/null; then
    PYTHON_CMD=python3.11
elif command -v python3 &> /dev/null; then
    PYTHON_CMD=python3
else
    print_error "Python 3 not found"
    exit 1
fi

print_success "Python: $($PYTHON_CMD --version)"

# Check PostgreSQL
if command -v psql &> /dev/null; then
    print_success "PostgreSQL: $(psql --version | awk '{print $3}')"
else
    print_warning "PostgreSQL not installed"
fi

# Check Redis
if command -v redis-cli &> /dev/null; then
    print_success "Redis: $(redis-cli --version | awk '{print $2}')"
else
    print_warning "Redis not installed"
fi

###############################################################################
# 2. DIRECTORY SETUP
###############################################################################

print_header "2. DIRECTORY SETUP"

PROJECT_DIR="/opt/traffic_share"

if [[ ! -d "$PROJECT_DIR" ]]; then
    print_warning "Project directory not found: $PROJECT_DIR"
    print_info "Please copy project to $PROJECT_DIR first"
    exit 1
fi

cd "$PROJECT_DIR"
print_success "Working directory: $PROJECT_DIR"

###############################################################################
# 3. VIRTUAL ENVIRONMENT
###############################################################################

print_header "3. VIRTUAL ENVIRONMENT"

if [[ ! -d "venv" ]]; then
    print_info "Creating virtual environment..."
    $PYTHON_CMD -m venv venv
    print_success "Virtual environment created"
else
    print_success "Virtual environment exists"
fi

# Activate virtual environment
source venv/bin/activate
print_success "Virtual environment activated"

###############################################################################
# 4. DEPENDENCIES
###############################################################################

print_header "4. DEPENDENCIES"

print_info "Upgrading pip..."
pip install --upgrade pip setuptools wheel -q

print_info "Installing dependencies..."
pip install -r requirements.txt -q

print_success "All dependencies installed"

###############################################################################
# 5. ENVIRONMENT CHECK
###############################################################################

print_header "5. ENVIRONMENT CHECK"

if [[ ! -f ".env" ]]; then
    print_warning ".env file not found"
    print_info "Copying from .env.example..."
    cp .env.example .env
    print_warning "Please edit .env file with your settings"
    print_warning "Required: DATABASE_URL, REDIS_URL, SECRET_KEY, TELEGRAM_BOT_TOKEN, CRYPTOMUS_API_KEY"
    exit 1
else
    print_success ".env file exists"
fi

# Check required variables
required_vars=("DATABASE_URL" "REDIS_URL" "SECRET_KEY")
missing_vars=()

for var in "${required_vars[@]}"; do
    if ! grep -q "^$var=" .env || grep -q "^$var=your-" .env; then
        missing_vars+=("$var")
    fi
done

if [[ ${#missing_vars[@]} -gt 0 ]]; then
    print_error "Missing or unconfigured variables in .env:"
    for var in "${missing_vars[@]}"; do
        echo "  - $var"
    done
    exit 1
fi

print_success "Environment variables configured"

###############################################################################
# 6. DATABASE CHECK
###############################################################################

print_header "6. DATABASE CHECK"

# Test PostgreSQL connection
print_info "Testing PostgreSQL connection..."
if $PYTHON_CMD -c "
from traffic_share.server.database import engine
try:
    conn = engine.connect()
    conn.close()
    print('OK')
except Exception as e:
    print(f'ERROR: {e}')
    exit(1)
" | grep -q "OK"; then
    print_success "PostgreSQL connection successful"
else
    print_error "PostgreSQL connection failed"
    print_info "Please check DATABASE_URL in .env"
    exit 1
fi

# Test Redis connection
print_info "Testing Redis connection..."
if $PYTHON_CMD -c "
import redis
from traffic_share.server.config import settings
url = settings.REDIS_URL
try:
    r = redis.from_url(url)
    r.ping()
    print('OK')
except Exception as e:
    print(f'ERROR: {e}')
    exit(1)
" | grep -q "OK"; then
    print_success "Redis connection successful"
else
    print_error "Redis connection failed"
    print_info "Please check REDIS_URL in .env"
    exit 1
fi

###############################################################################
# 7. DATABASE INITIALIZATION
###############################################################################

print_header "7. DATABASE INITIALIZATION"

print_info "Initializing database tables..."
$PYTHON_CMD traffic_share/scripts/init_db.py

if [[ $? -eq 0 ]]; then
    print_success "Database initialized successfully"
else
    print_error "Database initialization failed"
    exit 1
fi

###############################################################################
# 8. CREATE DIRECTORIES
###############################################################################

print_header "8. CREATE DIRECTORIES"

mkdir -p logs backups
print_success "Directories created: logs, backups"

###############################################################################
# 9. SYSTEMD SERVICES
###############################################################################

print_header "9. SYSTEMD SERVICES"

# API Service
print_info "Creating systemd service: traffic-share-api"
sudo tee /etc/systemd/system/traffic-share-api.service > /dev/null << EOF
[Unit]
Description=Traffic Share API
After=network.target postgresql.service redis.service

[Service]
Type=simple
User=$USER
WorkingDirectory=$PROJECT_DIR
Environment="PATH=$PROJECT_DIR/venv/bin"
ExecStart=$PROJECT_DIR/venv/bin/uvicorn traffic_share.server.main:app --host 0.0.0.0 --port 8000 --workers 4
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Bot Service
print_info "Creating systemd service: traffic-share-bot"
sudo tee /etc/systemd/system/traffic-share-bot.service > /dev/null << EOF
[Unit]
Description=Traffic Share Telegram Bot
After=network.target traffic-share-api.service

[Service]
Type=simple
User=$USER
WorkingDirectory=$PROJECT_DIR
Environment="PATH=$PROJECT_DIR/venv/bin"
ExecStart=$PROJECT_DIR/venv/bin/python -m traffic_share.bot.bot
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Tasks Service
print_info "Creating systemd service: traffic-share-tasks"
sudo tee /etc/systemd/system/traffic-share-tasks.service > /dev/null << EOF
[Unit]
Description=Traffic Share Background Tasks
After=network.target traffic-share-api.service

[Service]
Type=simple
User=$USER
WorkingDirectory=$PROJECT_DIR
Environment="PATH=$PROJECT_DIR/venv/bin"
ExecStart=$PROJECT_DIR/venv/bin/python -m traffic_share.server.tasks.cleanup_task
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Reload systemd
sudo systemctl daemon-reload
print_success "Systemd services created"

###############################################################################
# 10. START SERVICES
###############################################################################

print_header "10. START SERVICES"

# Enable and start services
for service in traffic-share-api traffic-share-bot traffic-share-tasks; do
    print_info "Enabling $service..."
    sudo systemctl enable $service
    
    print_info "Starting $service..."
    sudo systemctl start $service
    
    sleep 2
    
    if sudo systemctl is-active --quiet $service; then
        print_success "$service is running"
    else
        print_error "$service failed to start"
        sudo journalctl -u $service -n 20 --no-pager
    fi
done

###############################################################################
# 11. NGINX SETUP (Optional)
###############################################################################

print_header "11. NGINX SETUP"

if command -v nginx &> /dev/null; then
    print_info "Setting up Nginx reverse proxy..."
    
    sudo tee /etc/nginx/sites-available/traffic-share > /dev/null << 'EOF'
server {
    listen 80;
    server_name _;

    location /api {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /docs {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
    }

    location /openapi.json {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
    }

    location / {
        return 404;
    }
}
EOF
    
    # Enable site
    sudo ln -sf /etc/nginx/sites-available/traffic-share /etc/nginx/sites-enabled/
    
    # Test and reload
    sudo nginx -t && sudo systemctl reload nginx
    
    print_success "Nginx configured"
else
    print_warning "Nginx not installed - skipping"
fi

###############################################################################
# 12. FIREWALL
###############################################################################

print_header "12. FIREWALL"

if command -v ufw &> /dev/null; then
    print_info "Configuring UFW firewall..."
    sudo ufw allow 22/tcp comment 'SSH'
    sudo ufw allow 80/tcp comment 'HTTP'
    sudo ufw allow 443/tcp comment 'HTTPS'
    print_success "Firewall rules added"
else
    print_warning "UFW not installed - skipping"
fi

###############################################################################
# 13. HEALTH CHECK
###############################################################################

print_header "13. HEALTH CHECK"

print_info "Waiting for API to start..."
sleep 5

# Test API
if curl -s http://localhost:8000/api/system/health | grep -q "ok"; then
    print_success "API health check passed"
else
    print_warning "API health check failed (may need more time to start)"
fi

###############################################################################
# SUMMARY
###############################################################################

print_header "BUILD COMPLETE"

echo ""
echo -e "${GREEN}✅ Backend build successful!${NC}"
echo ""
echo "Services:"
echo "  - traffic-share-api     $(sudo systemctl is-active traffic-share-api)"
echo "  - traffic-share-bot     $(sudo systemctl is-active traffic-share-bot)"
echo "  - traffic-share-tasks   $(sudo systemctl is-active traffic-share-tasks)"
echo ""
echo "API Endpoints:"
echo "  - Health: http://$(hostname -I | awk '{print $1}')/api/system/health"
echo "  - Docs:   http://$(hostname -I | awk '{print $1}')/docs"
echo ""
echo "Logs:"
echo "  sudo journalctl -u traffic-share-api -f"
echo "  tail -f $PROJECT_DIR/logs/traffic_share.log"
echo ""
echo "Management:"
echo "  sudo systemctl status traffic-share-api"
echo "  sudo systemctl restart traffic-share-api"
echo "  sudo systemctl stop traffic-share-api"
echo ""

print_success "Done! 🎉"
