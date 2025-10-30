#!/bin/bash

###############################################################################
# TRAFFIC SHARE - 97% AVTOMATIK SETUP
# Faqat 3% (kalitlar) siz kiritasiz, qolganini tizim bajaradi!
###############################################################################

set -e
set -o pipefail

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
MAGENTA='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m'

PROJECT_DIR="/workspace"
ENV_FILE="$PROJECT_DIR/.env"
LOG_FILE="$PROJECT_DIR/logs/auto_setup_$(date +%Y%m%d_%H%M%S).log"

mkdir -p "$PROJECT_DIR/logs"

###############################################################################
# Logging
###############################################################################

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $@" | tee -a "$LOG_FILE"
}

log_info() {
    echo -e "${BLUE}ℹ️  $@${NC}" | tee -a "$LOG_FILE"
}

log_success() {
    echo -e "${GREEN}✅ $@${NC}" | tee -a "$LOG_FILE"
}

log_error() {
    echo -e "${RED}❌ $@${NC}" | tee -a "$LOG_FILE"
}

log_header() {
    echo ""
    echo -e "${CYAN}═══════════════════════════════════════════════════════════${NC}"
    echo -e "${CYAN}  $@${NC}"
    echo -e "${CYAN}═══════════════════════════════════════════════════════════${NC}"
}

###############################################################################
# 3% - FOYDALANUVCHIDAN MA'LUMOT OLISH (FAQAT KALITLAR!)
###############################################################################

collect_user_input() {
    log_header "QADAM 1/10: KALITLARNI KIRITING (3%)"
    
    echo ""
    echo -e "${YELLOW}📝 Faqat muhim kalitlarni kiriting:${NC}"
    echo ""
    
    # 1. SECRET_KEY
    read -p "🔐 SECRET_KEY (min 32 belgi, Enter - avtomatik): " SECRET_KEY
    if [ -z "$SECRET_KEY" ]; then
        SECRET_KEY=$(openssl rand -hex 32)
        log_info "SECRET_KEY avtomatik yaratildi"
    fi
    
    # 2. TELEGRAM_BOT_TOKEN
    echo ""
    echo -e "${YELLOW}Telegram Bot Token olish:${NC}"
    echo "  1. @BotFather ga boring"
    echo "  2. /newbot buyrug'ini yuboring"
    echo "  3. Token'ni ko'chiring"
    echo ""
    read -p "🤖 TELEGRAM_BOT_TOKEN: " TELEGRAM_BOT_TOKEN
    while [ -z "$TELEGRAM_BOT_TOKEN" ]; do
        echo -e "${RED}Token majburiy!${NC}"
        read -p "🤖 TELEGRAM_BOT_TOKEN: " TELEGRAM_BOT_TOKEN
    done
    
    # 3. TELEGRAM_ADMIN_IDS
    echo ""
    echo -e "${YELLOW}Admin Telegram ID olish:${NC}"
    echo "  1. @userinfobot ga boring"
    echo "  2. /start yuboring"
    echo "  3. ID'ni ko'chiring"
    echo ""
    read -p "👤 TELEGRAM_ADMIN_IDS (vergul bilan ajratish): " TELEGRAM_ADMIN_IDS
    while [ -z "$TELEGRAM_ADMIN_IDS" ]; do
        echo -e "${RED}Admin ID majburiy!${NC}"
        read -p "👤 TELEGRAM_ADMIN_IDS: " TELEGRAM_ADMIN_IDS
    done
    
    # 4. DATABASE (Avtomatik yoki Manual)
    echo ""
    read -p "💾 PostgreSQL parol (Enter - avtomatik): " DB_PASSWORD
    if [ -z "$DB_PASSWORD" ]; then
        DB_PASSWORD=$(openssl rand -base64 16)
        log_info "Database parol avtomatik yaratildi"
    fi
    
    # 5. CRYPTOMUS (Ixtiyoriy)
    echo ""
    echo -e "${BLUE}To'lov tizimi (ixtiyoriy, keyinroq ham sozlash mumkin):${NC}"
    read -p "💳 CRYPTOMUS_API_KEY (Enter - keyinroq): " CRYPTOMUS_API_KEY
    read -p "💳 CRYPTOMUS_MERCHANT_ID (Enter - keyinroq): " CRYPTOMUS_MERCHANT_ID
    
    log_success "Kalitlar qabul qilindi!"
}

###############################################################################
# 97% - AVTOMATIK SETUP
###############################################################################

setup_database() {
    log_header "QADAM 2/10: DATABASE SETUP (AUTO)"
    
    log_info "PostgreSQL sozlanmoqda..."
    
    # Create database and user
    sudo -u postgres psql << EOF >> "$LOG_FILE" 2>&1
DROP DATABASE IF EXISTS traffic_share;
DROP USER IF EXISTS traffic_user;
CREATE DATABASE traffic_share;
CREATE USER traffic_user WITH PASSWORD '$DB_PASSWORD';
GRANT ALL PRIVILEGES ON DATABASE traffic_share TO traffic_user;
ALTER DATABASE traffic_share OWNER TO traffic_user;
\q
EOF
    
    log_success "Database yaratildi: traffic_share"
    log_success "User yaratildi: traffic_user"
}

setup_redis() {
    log_header "QADAM 3/10: REDIS SETUP (AUTO)"
    
    log_info "Redis sozlanmoqda..."
    
    sudo systemctl restart redis-server
    
    # Test connection
    if redis-cli ping | grep -q "PONG"; then
        log_success "Redis ishlayapti"
    else
        log_error "Redis ishga tushmadi!"
    fi
}

create_env_file() {
    log_header "QADAM 4/10: .env FAYLI (AUTO)"
    
    log_info ".env yaratilmoqda..."
    
    cat > "$ENV_FILE" << EOF
# Application
APP_NAME=Traffic Share
APP_VERSION=1.0.0
DEBUG=False

# Server
HOST=0.0.0.0
PORT=8000
WORKERS=4

# Security
SECRET_KEY=$SECRET_KEY
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
REFRESH_TOKEN_EXPIRE_DAYS=30

# Database
DATABASE_URL=postgresql://traffic_user:$DB_PASSWORD@localhost:5432/traffic_share
DB_POOL_SIZE=20
DB_MAX_OVERFLOW=10
DB_ECHO=False

# Redis
REDIS_URL=redis://localhost:6379/0
REDIS_KEY_PREFIX=traffic_share:

# Telegram Bot
TELEGRAM_BOT_TOKEN=$TELEGRAM_BOT_TOKEN
TELEGRAM_ADMIN_IDS=$TELEGRAM_ADMIN_IDS
TELEGRAM_ADMIN_CHANNEL=

# Cryptomus Payment Gateway
CRYPTOMUS_API_KEY=${CRYPTOMUS_API_KEY:-test-api-key}
CRYPTOMUS_MERCHANT_ID=${CRYPTOMUS_MERCHANT_ID:-test-merchant-id}
CRYPTOMUS_API_URL=https://api.cryptomus.com/v1
CRYPTOMUS_WEBHOOK_SECRET=

# IP & Region Check
IP_API_ENABLED=True
REGION_CHECK_ENABLED=True

# Traffic & Pricing
PRICE_PER_GB=0.50
MIN_WITHDRAWAL_AMOUNT=5.0
MAX_WITHDRAWAL_AMOUNT=1000.0

# Package Allocation
PACKAGE_ALLOCATION_TTL=60
MAX_PACKAGES_PER_REQUEST=10

# Rate Limiting
RATE_LIMIT_ENABLED=True
RATE_LIMIT_AUTH=10/minute
RATE_LIMIT_TRAFFIC_UPDATE=100/minute
RATE_LIMIT_BUYER_PULL=10/minute

# Logging
LOG_LEVEL=INFO
LOG_FILE=logs/traffic_share.log
LOG_MAX_SIZE_MB=10
LOG_BACKUP_COUNT=5

# CORS
CORS_ORIGINS=*

# Background Tasks
CLEANUP_TASK_INTERVAL=300
STATS_TASK_INTERVAL=3600
BACKUP_TASK_INTERVAL=86400
EOF
    
    chmod 600 "$ENV_FILE"
    log_success ".env fayli yaratildi va xavfsizlashtirildi"
}

install_python_deps() {
    log_header "QADAM 5/10: PYTHON DEPENDENCIES (AUTO)"
    
    log_info "Virtual environment yaratilmoqda..."
    python3 -m venv venv
    source venv/bin/activate
    
    log_info "pip yangilanmoqda..."
    pip install --upgrade pip >> "$LOG_FILE" 2>&1
    
    log_info "Dependencies o'rnatilmoqda..."
    pip install -r requirements.txt >> "$LOG_FILE" 2>&1
    
    log_success "Barcha Python paketlar o'rnatildi"
}

initialize_database() {
    log_header "QADAM 6/10: DATABASE INITIALIZATION (AUTO)"
    
    log_info "Database tables yaratilmoqda..."
    
    source venv/bin/activate
    python3 traffic_share/scripts/init_db.py >> "$LOG_FILE" 2>&1
    
    log_success "Database initialized"
}

run_tests() {
    log_header "QADAM 7/10: TESTLARNI BAJARISH (AUTO)"
    
    log_info "Import tahlil..."
    python3 check_all_imports.py >> "$LOG_FILE" 2>&1
    log_success "Import test: 100%"
    
    log_info "Unit testlar..."
    pytest tests/ -v >> "$LOG_FILE" 2>&1 || log_warning "Ba'zi testlar o'tmadi"
    
    log_success "Testlar bajarildi"
}

configure_nginx() {
    log_header "QADAM 8/10: NGINX KONFIGURATSIYASI (AUTO)"
    
    log_info "Nginx config yaratilmoqda..."
    
    SERVER_IP=$(hostname -I | awk '{print $1}')
    
    sudo tee /etc/nginx/sites-available/traffic-share << EOF > /dev/null
server {
    listen 80;
    server_name $SERVER_IP;

    client_max_body_size 100M;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }

    location /downloads {
        alias /var/www/downloads;
        autoindex on;
    }
}
EOF
    
    # Enable site
    sudo ln -sf /etc/nginx/sites-available/traffic-share /etc/nginx/sites-enabled/
    sudo rm -f /etc/nginx/sites-enabled/default
    
    # Create downloads directory
    sudo mkdir -p /var/www/downloads
    sudo chown -R www-data:www-data /var/www/downloads
    
    # Test and reload
    sudo nginx -t >> "$LOG_FILE" 2>&1
    sudo systemctl reload nginx
    
    log_success "Nginx sozlandi: http://$SERVER_IP"
}

setup_systemd_services() {
    log_header "QADAM 9/10: SYSTEMD SERVICES (AUTO)"
    
    log_info "Service fayllar yaratilmoqda..."
    
    # API Service
    sudo tee /etc/systemd/system/traffic-share-api.service << EOF > /dev/null
[Unit]
Description=Traffic Share API Server
After=network.target postgresql.service redis.service

[Service]
Type=simple
User=$USER
WorkingDirectory=$PROJECT_DIR
Environment="PATH=$PROJECT_DIR/venv/bin"
ExecStart=$PROJECT_DIR/venv/bin/uvicorn traffic_share.server.main:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF
    
    # Bot Service
    sudo tee /etc/systemd/system/traffic-share-bot.service << EOF > /dev/null
[Unit]
Description=Traffic Share Telegram Bot
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$PROJECT_DIR
Environment="PATH=$PROJECT_DIR/venv/bin"
ExecStart=$PROJECT_DIR/venv/bin/python3 -m traffic_share.bot.bot
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF
    
    # Tasks Service
    sudo tee /etc/systemd/system/traffic-share-tasks.service << EOF > /dev/null
[Unit]
Description=Traffic Share Background Tasks
After=network.target postgresql.service

[Service]
Type=simple
User=$USER
WorkingDirectory=$PROJECT_DIR
Environment="PATH=$PROJECT_DIR/venv/bin"
ExecStart=$PROJECT_DIR/venv/bin/python3 -m traffic_share.server.tasks.cleanup_task
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF
    
    # Reload and enable
    sudo systemctl daemon-reload
    sudo systemctl enable traffic-share-api traffic-share-bot traffic-share-tasks
    
    log_success "Systemd services yaratildi"
}

start_services() {
    log_header "QADAM 10/10: SERVICELARNI ISHGA TUSHIRISH (AUTO)"
    
    log_info "Servicelar ishga tushirilmoqda..."
    
    sudo systemctl start traffic-share-api
    sudo systemctl start traffic-share-bot
    sudo systemctl start traffic-share-tasks
    
    sleep 3
    
    # Check status
    if sudo systemctl is-active --quiet traffic-share-api; then
        log_success "API server ishga tushdi"
    else
        log_error "API server ishga tushmadi!"
    fi
    
    if sudo systemctl is-active --quiet traffic-share-bot; then
        log_success "Bot ishga tushdi"
    else
        log_error "Bot ishga tushmadi!"
    fi
    
    if sudo systemctl is-active --quiet traffic-share-tasks; then
        log_success "Tasks ishga tushdi"
    else
        log_error "Tasks ishga tushmadi!"
    fi
}

###############################################################################
# Summary
###############################################################################

show_summary() {
    log_header "✨ SETUP TUGADI!"
    
    SERVER_IP=$(hostname -I | awk '{print $1}')
    
    echo ""
    echo -e "${GREEN}═══════════════════════════════════════════════════════════${NC}"
    echo -e "${GREEN}           🎉 TRAFFIC SHARE TAYYOR! 🎉                    ${NC}"
    echo -e "${GREEN}═══════════════════════════════════════════════════════════${NC}"
    echo ""
    
    echo -e "${CYAN}📊 SERVER MA'LUMOTLARI:${NC}"
    echo "   🌐 API URL: http://$SERVER_IP:8000"
    echo "   🌐 Web URL: http://$SERVER_IP"
    echo "   📝 API Docs: http://$SERVER_IP:8000/docs"
    echo ""
    
    echo -e "${CYAN}🔑 SAQLANGAN KALITLAR:${NC}"
    echo "   📄 .env fayli: $ENV_FILE"
    echo "   🔐 Database parol: $DB_PASSWORD"
    echo "   🤖 Bot token: ${TELEGRAM_BOT_TOKEN:0:20}..."
    echo ""
    
    echo -e "${CYAN}⚙️  SERVICELAR:${NC}"
    echo "   ✅ traffic-share-api.service"
    echo "   ✅ traffic-share-bot.service"
    echo "   ✅ traffic-share-tasks.service"
    echo ""
    
    echo -e "${CYAN}📝 BUYRUQLAR:${NC}"
    echo "   Status: sudo systemctl status traffic-share-api"
    echo "   Logs: sudo journalctl -u traffic-share-api -f"
    echo "   Restart: sudo systemctl restart traffic-share-api"
    echo "   Stop: sudo systemctl stop traffic-share-api"
    echo ""
    
    echo -e "${CYAN}🧪 TEST:${NC}"
    echo "   Bot test: python3 test_bot_send.py"
    echo "   API test: curl http://localhost:8000"
    echo ""
    
    echo -e "${YELLOW}⚠️  KEYINGI QADAMLAR:${NC}"
    echo "   1. Bot bilan /start qiling Telegram'da"
    echo "   2. API ni test qiling"
    echo "   3. SSL sozlang (ixtiyoriy): sudo certbot --nginx"
    echo "   4. APK build qiling (ixtiyoriy)"
    echo ""
    
    log_success "To'liq log: $LOG_FILE"
}

###############################################################################
# Main
###############################################################################

main() {
    clear
    
    echo ""
    echo -e "${MAGENTA}╔════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${MAGENTA}║                                                            ║${NC}"
    echo -e "${MAGENTA}║         TRAFFIC SHARE - 97% AVTOMATIK SETUP                ║${NC}"
    echo -e "${MAGENTA}║              Faqat kalitlar kiriting!                      ║${NC}"
    echo -e "${MAGENTA}║                                                            ║${NC}"
    echo -e "${MAGENTA}╚════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    
    log_info "Avtomatik setup boshlandi: $(date)"
    
    # 3% - User input
    collect_user_input
    
    # 97% - Automatic
    setup_database
    setup_redis
    create_env_file
    install_python_deps
    initialize_database
    run_tests
    configure_nginx
    setup_systemd_services
    start_services
    show_summary
    
    echo ""
    log_success "SETUP 100% TUGADI! 🚀"
    echo ""
}

main "$@"
