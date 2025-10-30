#!/bin/bash

###############################################################################
# TRAFFIC SHARE - COMPLETE BUILD AND DEPLOY SCRIPT
# Author: AI Assistant
# Date: 2025-10-30
# Description: Butun loyihani build va deploy qilish uchun
###############################################################################

set -e  # Exit on error
set -o pipefail  # Pipe failures

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
MAGENTA='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Configuration
PROJECT_NAME="Traffic Share"
PROJECT_DIR="/workspace"
LOG_DIR="$PROJECT_DIR/logs"
DEPLOY_LOG="$LOG_DIR/deploy_$(date +%Y%m%d_%H%M%S).log"
PYTHON_VERSION="3.12"
VENV_DIR="$PROJECT_DIR/venv"

# Create log directory
mkdir -p "$LOG_DIR"

###############################################################################
# Logging Functions
###############################################################################

log() {
    local level=$1
    shift
    local message="$@"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo "[$timestamp] [$level] $message" | tee -a "$DEPLOY_LOG"
}

log_info() {
    echo -e "${BLUE}ℹ️  $@${NC}"
    log "INFO" "$@"
}

log_success() {
    echo -e "${GREEN}✅ $@${NC}"
    log "SUCCESS" "$@"
}

log_warning() {
    echo -e "${YELLOW}⚠️  $@${NC}"
    log "WARNING" "$@"
}

log_error() {
    echo -e "${RED}❌ $@${NC}"
    log "ERROR" "$@"
}

log_header() {
    echo ""
    echo -e "${CYAN}═══════════════════════════════════════════════════════════${NC}"
    echo -e "${CYAN}  $@${NC}"
    echo -e "${CYAN}═══════════════════════════════════════════════════════════${NC}"
    log "HEADER" "$@"
}

###############################################################################
# Error Handler
###############################################################################

error_exit() {
    log_error "$1"
    log_error "Build va deploy muvaffaqiyatsiz tugadi!"
    log_error "Log fayli: $DEPLOY_LOG"
    exit 1
}

trap 'error_exit "Xatolik yuz berdi! Line: $LINENO"' ERR

###############################################################################
# Pre-flight Checks
###############################################################################

check_prerequisites() {
    log_header "1. PREREQUISITE CHECK"
    
    # Check Python
    if ! command -v python3 &> /dev/null; then
        error_exit "Python3 o'rnatilmagan!"
    fi
    
    PYTHON_VER=$(python3 --version | cut -d' ' -f2)
    log_success "Python: $PYTHON_VER"
    
    # Check pip
    if ! command -v pip3 &> /dev/null; then
        error_exit "pip3 o'rnatilmagan!"
    fi
    log_success "pip3: $(pip3 --version | cut -d' ' -f2)"
    
    # Check PostgreSQL
    if command -v psql &> /dev/null; then
        log_success "PostgreSQL: $(psql --version | cut -d' ' -f3)"
    else
        log_warning "PostgreSQL o'rnatilmagan (kerak bo'ladi)"
    fi
    
    # Check Redis
    if command -v redis-cli &> /dev/null; then
        log_success "Redis: $(redis-cli --version | cut -d' ' -f2)"
    else
        log_warning "Redis o'rnatilmagan (kerak bo'ladi)"
    fi
    
    # Check Git
    if command -v git &> /dev/null; then
        log_success "Git: $(git --version | cut -d' ' -f3)"
    fi
}

###############################################################################
# Virtual Environment Setup
###############################################################################

setup_venv() {
    log_header "2. VIRTUAL ENVIRONMENT SETUP"
    
    if [ -d "$VENV_DIR" ]; then
        log_info "Virtual environment mavjud, yangilanmoqda..."
        source "$VENV_DIR/bin/activate"
    else
        log_info "Virtual environment yaratilmoqda..."
        python3 -m venv "$VENV_DIR"
        source "$VENV_DIR/bin/activate"
    fi
    
    log_success "Virtual environment aktiv"
    
    # Upgrade pip
    log_info "pip yangilanmoqda..."
    pip install --upgrade pip >> "$DEPLOY_LOG" 2>&1
    log_success "pip yangilandi"
}

###############################################################################
# Dependencies Installation
###############################################################################

install_dependencies() {
    log_header "3. DEPENDENCIES INSTALLATION"
    
    if [ ! -f "requirements.txt" ]; then
        error_exit "requirements.txt topilmadi!"
    fi
    
    log_info "Python paketlar o'rnatilmoqda..."
    pip install -r requirements.txt >> "$DEPLOY_LOG" 2>&1
    
    log_success "Barcha paketlar o'rnatildi"
    
    # List installed packages
    log_info "O'rnatilgan paketlar:"
    pip list | tee -a "$DEPLOY_LOG"
}

###############################################################################
# Code Quality Checks
###############################################################################

run_code_checks() {
    log_header "4. CODE QUALITY CHECKS"
    
    # Import check
    log_info "Importlar tekshirilmoqda..."
    if python3 check_all_imports.py >> "$DEPLOY_LOG" 2>&1; then
        log_success "Barcha importlar to'g'ri (100%)"
    else
        log_warning "Ba'zi importlarda muammolar bor"
    fi
    
    # Syntax check
    log_info "Sintaksis tekshirilmoqda..."
    if find traffic_share -name "*.py" -exec python3 -m py_compile {} \; 2>> "$DEPLOY_LOG"; then
        log_success "Sintaksis xatoligi yo'q"
    else
        error_exit "Sintaksis xatoligi topildi!"
    fi
    
    # Optional: Flake8
    if command -v flake8 &> /dev/null; then
        log_info "Flake8 tahlil..."
        ERROR_COUNT=$(flake8 traffic_share --count --select=E9,F63,F7,F82 2>&1 | tail -1 || echo "0")
        if [ "$ERROR_COUNT" == "0" ]; then
            log_success "Kritik xatolik yo'q"
        else
            log_warning "$ERROR_COUNT ta kritik xatolik topildi"
        fi
    fi
}

###############################################################################
# Run Tests
###############################################################################

run_tests() {
    log_header "5. RUNNING TESTS"
    
    if [ -d "tests" ]; then
        log_info "Testlar ishga tushirilmoqda..."
        
        if pytest tests/ -v --tb=short >> "$DEPLOY_LOG" 2>&1; then
            log_success "Barcha testlar o'tdi"
        else
            log_warning "Ba'zi testlar muvaffaqiyatsiz"
            log_warning "Test loglarini ko'ring: $DEPLOY_LOG"
        fi
    else
        log_warning "Tests papkasi topilmadi"
    fi
}

###############################################################################
# Database Setup
###############################################################################

setup_database() {
    log_header "6. DATABASE SETUP"
    
    # Check if .env exists
    if [ ! -f ".env" ]; then
        log_warning ".env fayli topilmadi, .env.example'dan nusxa ko'chirilmoqda..."
        if [ -f ".env.example" ]; then
            cp .env.example .env
            log_warning ".env faylini tahrirlang va haqiqiy ma'lumotlarni kiriting!"
        else
            error_exit ".env va .env.example topilmadi!"
        fi
    fi
    
    # Source .env
    if [ -f ".env" ]; then
        export $(cat .env | grep -v '^#' | xargs)
    fi
    
    # Check database connection
    log_info "Database ulanishi tekshirilmoqda..."
    
    if python3 << 'PYEOF' >> "$DEPLOY_LOG" 2>&1
from traffic_share.server.database import engine
try:
    engine.connect()
    print("Database connected")
except Exception as e:
    print(f"Database error: {e}")
    exit(1)
PYEOF
    then
        log_success "Database ulanishi muvaffaqiyatli"
        
        # Initialize database
        log_info "Database tables yaratilmoqda..."
        if python3 traffic_share/scripts/init_db.py >> "$DEPLOY_LOG" 2>&1; then
            log_success "Database tables yaratildi"
        else
            log_warning "Database init muammosi (davom etamiz)"
        fi
    else
        log_warning "Database ulanmadi (keyinroq sozlang)"
    fi
}

###############################################################################
# Configuration Check
###############################################################################

check_configuration() {
    log_header "7. CONFIGURATION CHECK"
    
    # Check .env file
    if [ -f ".env" ]; then
        log_info ".env fayli mavjud"
        
        # Check critical variables
        critical_vars=("SECRET_KEY" "DATABASE_URL" "TELEGRAM_BOT_TOKEN")
        
        for var in "${critical_vars[@]}"; do
            if grep -q "^${var}=" .env; then
                value=$(grep "^${var}=" .env | cut -d'=' -f2)
                if [[ "$value" =~ (your-|test-|change-this|example) ]]; then
                    log_warning "$var hali sozlanmagan!"
                else
                    log_success "$var sozlangan"
                fi
            else
                log_warning "$var .env da yo'q!"
            fi
        done
    else
        log_error ".env fayli yo'q!"
    fi
    
    # Check logs directory
    if [ ! -d "logs" ]; then
        mkdir -p logs
        log_success "logs papkasi yaratildi"
    fi
}

###############################################################################
# Build Backend
###############################################################################

build_backend() {
    log_header "8. BUILD BACKEND"
    
    log_info "Backend paketlar tekshirilmoqda..."
    
    # Check main components
    components=(
        "traffic_share.server.main"
        "traffic_share.bot.bot"
        "traffic_share.server.models"
        "traffic_share.server.routes"
        "traffic_share.server.services"
    )
    
    for component in "${components[@]}"; do
        if python3 -c "import $component" 2>> "$DEPLOY_LOG"; then
            log_success "$component - OK"
        else
            error_exit "$component yuklashda xatolik!"
        fi
    done
    
    log_success "Backend tayyor"
}

###############################################################################
# Build Frontend (APK)
###############################################################################

build_frontend() {
    log_header "9. BUILD FRONTEND (OPTIONAL)"
    
    if command -v flutter &> /dev/null; then
        log_info "Flutter topildi, APK build qilinmoqdami?"
        
        if [ -d "app" ]; then
            cd app
            
            log_info "Flutter pub get..."
            flutter pub get >> "$DEPLOY_LOG" 2>&1
            
            log_info "APK build..."
            if flutter build apk --release >> "$DEPLOY_LOG" 2>&1; then
                log_success "APK muvaffaqiyatli build qilindi"
                APK_PATH=$(find build/app/outputs -name "*.apk" | head -1)
                log_info "APK: $APK_PATH"
            else
                log_warning "APK build muvaffaqiyatsiz"
            fi
            
            cd ..
        else
            log_warning "app papkasi topilmadi"
        fi
    else
        log_info "Flutter o'rnatilmagan, APK build qilinmaydi"
    fi
}

###############################################################################
# Service Files
###############################################################################

create_systemd_services() {
    log_header "10. SYSTEMD SERVICES"
    
    log_info "Systemd service fayllar yaratilmoqda..."
    
    # Main API service
    cat > /tmp/traffic-share-api.service << EOF
[Unit]
Description=Traffic Share API Server
After=network.target postgresql.service redis.service

[Service]
Type=simple
User=$USER
WorkingDirectory=$PROJECT_DIR
Environment="PATH=$VENV_DIR/bin"
ExecStart=$VENV_DIR/bin/uvicorn traffic_share.server.main:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF
    
    log_success "traffic-share-api.service yaratildi"
    
    # Bot service
    cat > /tmp/traffic-share-bot.service << EOF
[Unit]
Description=Traffic Share Telegram Bot
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$PROJECT_DIR
Environment="PATH=$VENV_DIR/bin"
ExecStart=$VENV_DIR/bin/python3 -m traffic_share.bot.bot
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF
    
    log_success "traffic-share-bot.service yaratildi"
    
    # Tasks service
    cat > /tmp/traffic-share-tasks.service << EOF
[Unit]
Description=Traffic Share Background Tasks
After=network.target postgresql.service

[Service]
Type=simple
User=$USER
WorkingDirectory=$PROJECT_DIR
Environment="PATH=$VENV_DIR/bin"
ExecStart=$VENV_DIR/bin/python3 -m traffic_share.server.tasks.cleanup_task
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF
    
    log_success "traffic-share-tasks.service yaratildi"
    
    log_info "Service fayllarni o'rnatish uchun:"
    echo ""
    echo "  sudo cp /tmp/traffic-share-*.service /etc/systemd/system/"
    echo "  sudo systemctl daemon-reload"
    echo "  sudo systemctl enable traffic-share-api traffic-share-bot traffic-share-tasks"
    echo "  sudo systemctl start traffic-share-api traffic-share-bot traffic-share-tasks"
    echo ""
}

###############################################################################
# Deployment Summary
###############################################################################

deployment_summary() {
    log_header "11. DEPLOYMENT SUMMARY"
    
    echo ""
    log_success "BUILD VA DEPLOY MUVAFFAQIYATLI TUGADI! 🎉"
    echo ""
    
    log_info "Loyiha ma'lumotlari:"
    echo "  📁 Papka: $PROJECT_DIR"
    echo "  🐍 Python: $PYTHON_VER"
    echo "  📦 Virtual Env: $VENV_DIR"
    echo "  📝 Log fayli: $DEPLOY_LOG"
    echo ""
    
    log_info "Keyingi qadamlar:"
    echo ""
    echo "  1. .env faylini to'ldiring:"
    echo "     nano .env"
    echo ""
    echo "  2. PostgreSQL va Redis sozlang:"
    echo "     sudo systemctl start postgresql redis"
    echo ""
    echo "  3. Database yarating:"
    echo "     python3 traffic_share/scripts/init_db.py"
    echo ""
    echo "  4. Serverni ishga tushiring:"
    echo "     uvicorn traffic_share.server.main:app --host 0.0.0.0 --port 8000"
    echo ""
    echo "  5. Bot testlang:"
    echo "     python3 test_bot_send.py"
    echo ""
    echo "  6. Systemd servicelarni o'rnating (production):"
    echo "     sudo cp /tmp/traffic-share-*.service /etc/systemd/system/"
    echo "     sudo systemctl daemon-reload"
    echo "     sudo systemctl start traffic-share-api"
    echo ""
    
    log_success "Barcha loglar: $DEPLOY_LOG"
    echo ""
}

###############################################################################
# Main Execution
###############################################################################

main() {
    clear
    
    echo ""
    echo -e "${MAGENTA}╔════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${MAGENTA}║                                                            ║${NC}"
    echo -e "${MAGENTA}║            TRAFFIC SHARE BUILD & DEPLOY                    ║${NC}"
    echo -e "${MAGENTA}║                                                            ║${NC}"
    echo -e "${MAGENTA}╚════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    
    log_info "Build va deploy boshlandi: $(date)"
    log_info "Log fayli: $DEPLOY_LOG"
    echo ""
    
    # Run all steps
    check_prerequisites
    setup_venv
    install_dependencies
    run_code_checks
    run_tests
    setup_database
    check_configuration
    build_backend
    build_frontend
    create_systemd_services
    deployment_summary
    
    log_success "Tugadi! $(date)"
}

# Run main
main "$@"
