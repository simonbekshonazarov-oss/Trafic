#!/bin/bash

###############################################################################
# TRAFFIC SHARE - TO'LIQ TIZIM O'RNATISH SCRIPTI
# Barcha kerakli paketlar va toollarni avtomatik o'rnatadi
# 97% AVTOMATIK - Faqat kalitlar kiritish kerak!
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

# Configuration
INSTALL_LOG="/var/log/traffic_share_install.log"
PROJECT_DIR="/workspace"
FLUTTER_VERSION="3.16.0"
PYTHON_VERSION="3.12"
NODE_VERSION="20"

###############################################################################
# Logging
###############################################################################

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $@" | tee -a "$INSTALL_LOG"
}

log_info() {
    echo -e "${BLUE}ℹ️  $@${NC}" | tee -a "$INSTALL_LOG"
}

log_success() {
    echo -e "${GREEN}✅ $@${NC}" | tee -a "$INSTALL_LOG"
}

log_warning() {
    echo -e "${YELLOW}⚠️  $@${NC}" | tee -a "$INSTALL_LOG"
}

log_error() {
    echo -e "${RED}❌ $@${NC}" | tee -a "$INSTALL_LOG"
}

log_header() {
    echo ""
    echo -e "${CYAN}═══════════════════════════════════════════════════════════${NC}"
    echo -e "${CYAN}  $@${NC}"
    echo -e "${CYAN}═══════════════════════════════════════════════════════════${NC}"
    log "HEADER: $@"
}

###############################################################################
# System Info
###############################################################################

detect_os() {
    if [ -f /etc/os-release ]; then
        . /etc/os-release
        OS=$ID
        OS_VERSION=$VERSION_ID
    elif [ -f /etc/lsb-release ]; then
        . /etc/lsb-release
        OS=$DISTRIB_ID
        OS_VERSION=$DISTRIB_RELEASE
    else
        OS=$(uname -s)
        OS_VERSION=$(uname -r)
    fi
    
    log_info "OS: $OS $OS_VERSION"
}

###############################################################################
# 1. SYSTEM UPDATE
###############################################################################

update_system() {
    log_header "1. SYSTEM UPDATE"
    
    log_info "Sistema yangilanmoqda..."
    
    if [ "$OS" = "ubuntu" ] || [ "$OS" = "debian" ]; then
        sudo apt update -y >> "$INSTALL_LOG" 2>&1
        sudo apt upgrade -y >> "$INSTALL_LOG" 2>&1
        log_success "Sistema yangilandi"
    elif [ "$OS" = "centos" ] || [ "$OS" = "rhel" ]; then
        sudo yum update -y >> "$INSTALL_LOG" 2>&1
        log_success "Sistema yangilandi"
    else
        log_warning "Noma'lum OS, manual yangilash kerak"
    fi
}

###############################################################################
# 2. BASIC TOOLS
###############################################################################

install_basic_tools() {
    log_header "2. BASIC TOOLS"
    
    log_info "Asosiy toollar o'rnatilmoqda..."
    
    TOOLS=(
        "curl"
        "wget"
        "git"
        "build-essential"
        "software-properties-common"
        "apt-transport-https"
        "ca-certificates"
        "gnupg"
        "lsb-release"
        "unzip"
        "zip"
        "tar"
        "gzip"
        "nano"
        "vim"
        "htop"
        "net-tools"
    )
    
    for tool in "${TOOLS[@]}"; do
        if ! command -v $tool &> /dev/null; then
            log_info "O'rnatilmoqda: $tool"
            sudo apt install -y $tool >> "$INSTALL_LOG" 2>&1
            log_success "$tool o'rnatildi"
        else
            log_success "$tool allaqachon o'rnatilgan"
        fi
    done
}

###############################################################################
# 3. PYTHON
###############################################################################

install_python() {
    log_header "3. PYTHON $PYTHON_VERSION"
    
    if command -v python3 &> /dev/null; then
        CURRENT_VERSION=$(python3 --version | cut -d' ' -f2)
        log_info "Python hozirgi versiya: $CURRENT_VERSION"
    fi
    
    log_info "Python $PYTHON_VERSION o'rnatilmoqda..."
    
    # Add deadsnakes PPA
    sudo add-apt-repository ppa:deadsnakes/ppa -y >> "$INSTALL_LOG" 2>&1
    sudo apt update -y >> "$INSTALL_LOG" 2>&1
    
    # Install Python
    sudo apt install -y \
        python${PYTHON_VERSION} \
        python${PYTHON_VERSION}-dev \
        python${PYTHON_VERSION}-venv \
        python3-pip \
        >> "$INSTALL_LOG" 2>&1
    
    # Set as default
    sudo update-alternatives --install /usr/bin/python3 python3 /usr/bin/python${PYTHON_VERSION} 1
    
    log_success "Python $(python3 --version) o'rnatildi"
    
    # Upgrade pip
    log_info "pip yangilanmoqda..."
    python3 -m pip install --upgrade pip >> "$INSTALL_LOG" 2>&1
    log_success "pip yangilandi"
}

###############################################################################
# 4. POSTGRESQL
###############################################################################

install_postgresql() {
    log_header "4. POSTGRESQL"
    
    if command -v psql &> /dev/null; then
        log_success "PostgreSQL allaqachon o'rnatilgan"
        return
    fi
    
    log_info "PostgreSQL o'rnatilmoqda..."
    
    # Add PostgreSQL repo
    sudo sh -c 'echo "deb http://apt.postgresql.org/pub/repos/apt $(lsb_release -cs)-pgdg main" > /etc/apt/sources.list.d/pgdg.list'
    wget --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc | sudo apt-key add -
    
    sudo apt update -y >> "$INSTALL_LOG" 2>&1
    sudo apt install -y postgresql-15 postgresql-contrib-15 >> "$INSTALL_LOG" 2>&1
    
    # Start service
    sudo systemctl start postgresql
    sudo systemctl enable postgresql
    
    log_success "PostgreSQL $(psql --version | cut -d' ' -f3) o'rnatildi"
}

###############################################################################
# 5. REDIS
###############################################################################

install_redis() {
    log_header "5. REDIS"
    
    if command -v redis-cli &> /dev/null; then
        log_success "Redis allaqachon o'rnatilgan"
        return
    fi
    
    log_info "Redis o'rnatilmoqda..."
    
    sudo apt install -y redis-server >> "$INSTALL_LOG" 2>&1
    
    # Configure Redis
    sudo sed -i 's/supervised no/supervised systemd/g' /etc/redis/redis.conf
    
    # Start service
    sudo systemctl start redis-server
    sudo systemctl enable redis-server
    
    log_success "Redis $(redis-cli --version | cut -d' ' -f2) o'rnatildi"
}

###############################################################################
# 6. NODE.JS & NPM
###############################################################################

install_nodejs() {
    log_header "6. NODE.JS $NODE_VERSION"
    
    if command -v node &> /dev/null; then
        log_info "Node.js hozirgi versiya: $(node --version)"
    fi
    
    log_info "Node.js $NODE_VERSION o'rnatilmoqda..."
    
    # Add NodeSource repo
    curl -fsSL https://deb.nodesource.com/setup_${NODE_VERSION}.x | sudo -E bash - >> "$INSTALL_LOG" 2>&1
    
    sudo apt install -y nodejs >> "$INSTALL_LOG" 2>&1
    
    log_success "Node.js $(node --version) o'rnatildi"
    log_success "npm $(npm --version) o'rnatildi"
}

###############################################################################
# 7. DOCKER
###############################################################################

install_docker() {
    log_header "7. DOCKER"
    
    if command -v docker &> /dev/null; then
        log_success "Docker allaqachon o'rnatilgan"
        return
    fi
    
    log_info "Docker o'rnatilmoqda..."
    
    # Add Docker repo
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
    
    echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
    
    sudo apt update -y >> "$INSTALL_LOG" 2>&1
    sudo apt install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin >> "$INSTALL_LOG" 2>&1
    
    # Add user to docker group
    sudo usermod -aG docker $USER
    
    # Start service
    sudo systemctl start docker
    sudo systemctl enable docker
    
    log_success "Docker $(docker --version | cut -d' ' -f3 | tr -d ',') o'rnatildi"
}

###############################################################################
# 8. FLUTTER
###############################################################################

install_flutter() {
    log_header "8. FLUTTER $FLUTTER_VERSION"
    
    FLUTTER_DIR="$HOME/flutter"
    
    if [ -d "$FLUTTER_DIR" ]; then
        log_info "Flutter allaqachon mavjud, yangilanmoqda..."
        cd "$FLUTTER_DIR"
        git pull >> "$INSTALL_LOG" 2>&1
    else
        log_info "Flutter o'rnatilmoqda..."
        cd "$HOME"
        git clone https://github.com/flutter/flutter.git -b stable >> "$INSTALL_LOG" 2>&1
    fi
    
    # Add to PATH
    if ! grep -q "flutter/bin" "$HOME/.bashrc"; then
        echo 'export PATH="$PATH:$HOME/flutter/bin"' >> "$HOME/.bashrc"
        log_success "Flutter PATH ga qo'shildi"
    fi
    
    export PATH="$PATH:$HOME/flutter/bin"
    
    # Install Android dependencies
    log_info "Android dependencies o'rnatilmoqda..."
    sudo apt install -y \
        openjdk-11-jdk \
        android-sdk \
        >> "$INSTALL_LOG" 2>&1 || true
    
    # Run flutter doctor
    log_info "Flutter doctor ishga tushirilmoqda..."
    flutter doctor >> "$INSTALL_LOG" 2>&1 || true
    
    log_success "Flutter o'rnatildi"
    log_info "Flutter versiyani tekshirish: flutter --version"
}

###############################################################################
# 9. NGINX
###############################################################################

install_nginx() {
    log_header "9. NGINX"
    
    if command -v nginx &> /dev/null; then
        log_success "Nginx allaqachon o'rnatilgan"
        return
    fi
    
    log_info "Nginx o'rnatilmoqda..."
    
    sudo apt install -y nginx >> "$INSTALL_LOG" 2>&1
    
    # Start service
    sudo systemctl start nginx
    sudo systemctl enable nginx
    
    # Configure firewall
    sudo ufw allow 'Nginx Full' >> "$INSTALL_LOG" 2>&1 || true
    
    log_success "Nginx $(nginx -v 2>&1 | cut -d'/' -f2) o'rnatildi"
}

###############################################################################
# 10. SSL/CERTBOT
###############################################################################

install_certbot() {
    log_header "10. CERTBOT (SSL)"
    
    if command -v certbot &> /dev/null; then
        log_success "Certbot allaqachon o'rnatilgan"
        return
    fi
    
    log_info "Certbot o'rnatilmoqda..."
    
    sudo apt install -y certbot python3-certbot-nginx >> "$INSTALL_LOG" 2>&1
    
    log_success "Certbot o'rnatildi"
    log_info "SSL sertifikat olish: sudo certbot --nginx -d yourdomain.com"
}

###############################################################################
# 11. ADDITIONAL TOOLS
###############################################################################

install_additional_tools() {
    log_header "11. ADDITIONAL TOOLS"
    
    log_info "Qo'shimcha toollar o'rnatilmoqda..."
    
    # Monitoring tools
    sudo apt install -y \
        htop \
        iotop \
        iftop \
        ncdu \
        tree \
        jq \
        >> "$INSTALL_LOG" 2>&1
    
    # Security
    sudo apt install -y \
        ufw \
        fail2ban \
        >> "$INSTALL_LOG" 2>&1
    
    # Enable firewall
    sudo ufw --force enable >> "$INSTALL_LOG" 2>&1 || true
    sudo ufw allow 22 >> "$INSTALL_LOG" 2>&1 || true
    sudo ufw allow 80 >> "$INSTALL_LOG" 2>&1 || true
    sudo ufw allow 443 >> "$INSTALL_LOG" 2>&1 || true
    sudo ufw allow 8000 >> "$INSTALL_LOG" 2>&1 || true
    
    log_success "Qo'shimcha toollar o'rnatildi"
}

###############################################################################
# 12. VERIFY INSTALLATION
###############################################################################

verify_installation() {
    log_header "12. VERIFICATION"
    
    echo ""
    log_info "O'rnatilgan versiyalar:"
    echo ""
    
    echo "✅ Python: $(python3 --version 2>&1)"
    echo "✅ pip: $(pip3 --version 2>&1 | cut -d' ' -f1-2)"
    echo "✅ PostgreSQL: $(psql --version 2>&1 | cut -d' ' -f1-3)"
    echo "✅ Redis: $(redis-cli --version 2>&1 | cut -d' ' -f1-2)"
    echo "✅ Node.js: $(node --version 2>&1)"
    echo "✅ npm: $(npm --version 2>&1)"
    echo "✅ Docker: $(docker --version 2>&1 | cut -d',' -f1)"
    echo "✅ Nginx: $(nginx -v 2>&1)"
    echo "✅ Git: $(git --version 2>&1)"
    
    if [ -d "$HOME/flutter" ]; then
        export PATH="$PATH:$HOME/flutter/bin"
        echo "✅ Flutter: $(flutter --version 2>&1 | head -1)"
    fi
    
    echo ""
}

###############################################################################
# Main
###############################################################################

main() {
    clear
    
    echo ""
    echo -e "${MAGENTA}╔════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${MAGENTA}║                                                            ║${NC}"
    echo -e "${MAGENTA}║         TRAFFIC SHARE - TO'LIQ TIZIM O'RNATISH             ║${NC}"
    echo -e "${MAGENTA}║                  97% AVTOMATIK                             ║${NC}"
    echo -e "${MAGENTA}║                                                            ║${NC}"
    echo -e "${MAGENTA}╚════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    
    log_info "O'rnatish boshlandi: $(date)"
    log_info "Log fayli: $INSTALL_LOG"
    echo ""
    
    # Check root
    if [ "$EUID" -eq 0 ]; then
        log_error "Iltimos, root user sifatida ishlatmang!"
        log_info "Ishlatish: ./setup_full_system.sh"
        exit 1
    fi
    
    # Detect OS
    detect_os
    
    # Check internet
    if ! ping -c 1 google.com &> /dev/null; then
        log_error "Internet aloqasi yo'q!"
        exit 1
    fi
    
    # Run installation steps
    update_system
    install_basic_tools
    install_python
    install_postgresql
    install_redis
    install_nodejs
    install_docker
    install_flutter
    install_nginx
    install_certbot
    install_additional_tools
    verify_installation
    
    log_header "O'RNATISH TUGADI!"
    
    echo ""
    log_success "Barcha paketlar muvaffaqiyatli o'rnatildi! 🎉"
    echo ""
    log_info "Keyingi qadam: ./auto_setup.sh ni ishga tushiring"
    echo ""
    log_warning "PATH yangilash uchun terminal ni qayta oching yoki ishga tushiring:"
    echo "  source ~/.bashrc"
    echo ""
    
    log_info "To'liq log: $INSTALL_LOG"
}

main "$@"
