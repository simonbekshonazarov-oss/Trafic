#!/bin/bash

# Production Setup Script for Traffic Share
# This script sets up the production environment

set -e

echo "🚀 Setting up Traffic Share Production Environment..."

# Check if running as root
if [ "$EUID" -eq 0 ]; then
    echo "❌ Please do not run this script as root"
    exit 1
fi

# Update system packages
echo "📦 Updating system packages..."
sudo apt update && sudo apt upgrade -y

# Install required system packages
echo "🔧 Installing system dependencies..."
sudo apt install -y python3.11 python3.11-venv python3.11-dev postgresql postgresql-contrib redis-server nginx certbot python3-certbot-nginx git curl

# Create application user
echo "👤 Creating application user..."
sudo useradd -m -s /bin/bash traffic_share || echo "User already exists"
sudo usermod -aG sudo traffic_share

# Create application directory
echo "📁 Creating application directory..."
sudo mkdir -p /opt/traffic_share
sudo chown traffic_share:traffic_share /opt/traffic_share

# Clone repository (if not already present)
if [ ! -d "/opt/traffic_share/.git" ]; then
    echo "📥 Cloning repository..."
    sudo -u traffic_share git clone https://github.com/your-repo/traffic_share.git /opt/traffic_share
fi

# Set up Python virtual environment
echo "🐍 Setting up Python virtual environment..."
cd /opt/traffic_share
sudo -u traffic_share python3.11 -m venv venv
sudo -u traffic_share ./venv/bin/pip install --upgrade pip
sudo -u traffic_share ./venv/bin/pip install -r requirements.txt

# Set up PostgreSQL database
echo "🗄️ Setting up PostgreSQL database..."
sudo -u postgres psql -c "CREATE DATABASE traffic_share;"
sudo -u postgres psql -c "CREATE USER traffic_user WITH PASSWORD 'secure_password_here';"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE traffic_share TO traffic_user;"

# Set up Redis
echo "🔴 Configuring Redis..."
sudo systemctl enable redis-server
sudo systemctl start redis-server

# Create systemd service files
echo "⚙️ Creating systemd services..."

# Main application service
sudo tee /etc/systemd/system/traffic_share.service > /dev/null << 'SERVICE_EOF'
[Unit]
Description=Traffic Share API Server
After=network.target postgresql.service redis.service

[Service]
Type=simple
User=traffic_share
Group=traffic_share
WorkingDirectory=/opt/traffic_share
Environment=PATH=/opt/traffic_share/venv/bin
ExecStart=/opt/traffic_share/venv/bin/uvicorn traffic_share.server.main:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
SERVICE_EOF

# Bot service
sudo tee /etc/systemd/system/traffic_share_bot.service > /dev/null << 'BOT_SERVICE_EOF'
[Unit]
Description=Traffic Share Telegram Bot
After=network.target

[Service]
Type=simple
User=traffic_share
Group=traffic_share
WorkingDirectory=/opt/traffic_share
Environment=PATH=/opt/traffic_share/venv/bin
ExecStart=/opt/traffic_share/venv/bin/python -m traffic_share.bot.bot
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
BOT_SERVICE_EOF

# Bot API service
sudo tee /etc/systemd/system/traffic_share_bot_api.service > /dev/null << 'BOT_API_SERVICE_EOF'
[Unit]
Description=Traffic Share Bot API Server
After=network.target

[Service]
Type=simple
User=traffic_share
Group=traffic_share
WorkingDirectory=/opt/traffic_share
Environment=PATH=/opt/traffic_share/venv/bin
ExecStart=/opt/traffic_share/venv/bin/uvicorn traffic_share.bot.api_server:app --host 0.0.0.0 --port 8001
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
BOT_API_SERVICE_EOF

# Set up Nginx
echo "🌐 Configuring Nginx..."
sudo tee /etc/nginx/sites-available/traffic_share > /dev/null << 'NGINX_EOF'
server {
    listen 80;
    server_name your-domain.com;

    # API server
    location /api/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Bot API server
    location /bot-api/ {
        proxy_pass http://127.0.0.1:8001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Admin dashboard
    location /admin/ {
        alias /opt/traffic_share/admin_dashboard/;
        index index.html;
        try_files $uri $uri/ =404;
    }

    # Static files
    location /static/ {
        alias /opt/traffic_share/static/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
NGINX_EOF

# Enable the site
sudo ln -sf /etc/nginx/sites-available/traffic_share /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t
sudo systemctl reload nginx

# Set up SSL with Let's Encrypt
echo "🔒 Setting up SSL certificate..."
read -p "Enter your domain name: " DOMAIN
sudo certbot --nginx -d $DOMAIN --non-interactive --agree-tos --email admin@$DOMAIN

# Create environment file
echo "📝 Creating production environment file..."
sudo -u traffic_share tee /opt/traffic_share/.env.production > /dev/null << 'ENV_EOF'
# Production Environment Configuration
DATABASE_URL=postgresql://traffic_user:secure_password_here@localhost:5432/traffic_share
REDIS_URL=redis://localhost:6379/0

# Security (CHANGE THESE IN PRODUCTION!)
SECRET_KEY=your-super-secret-key-change-this-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# Telegram Bot (ADD YOUR TOKENS)
TELEGRAM_BOT_TOKEN=your-telegram-bot-token
TELEGRAM_ADMIN_IDS=123456789,987654321

# Cryptomus Payment (ADD YOUR CREDENTIALS)
CRYPTOMUS_MERCHANT_ID=your-merchant-id
CRYPTOMUS_API_KEY=your-api-key
CRYPTOMUS_WEBHOOK_SECRET=your-webhook-secret

# Server Configuration
HOST=0.0.0.0
PORT=8000
DEBUG=False

# Rate Limiting
RATE_LIMIT_PER_MINUTE=60
BUYER_RATE_LIMIT_PER_MINUTE=10

# Traffic Pricing
PRICE_PER_GB_USD=0.50
MIN_WITHDRAWAL_USD=5.0
MAX_WITHDRAWAL_USD=1000.0

# Allowed Regions
ALLOWED_REGIONS=US,EU,CA,AU

# Bot Service
BOT_SERVICE_URL=http://localhost:8001
BOT_API_KEY=bot_secret_key
ENV_EOF

# Set up log rotation
echo "📋 Setting up log rotation..."
sudo tee /etc/logrotate.d/traffic_share > /dev/null << 'LOGROTATE_EOF'
/opt/traffic_share/logs/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    create 644 traffic_share traffic_share
    postrotate
        systemctl reload traffic_share
        systemctl reload traffic_share_bot
        systemctl reload traffic_share_bot_api
    endscript
}
LOGROTATE_EOF

# Create logs directory
sudo -u traffic_share mkdir -p /opt/traffic_share/logs

# Set up database migrations
echo "🗄️ Running database migrations..."
cd /opt/traffic_share
sudo -u traffic_share ./venv/bin/alembic upgrade head

# Start services
echo "🚀 Starting services..."
sudo systemctl daemon-reload
sudo systemctl enable traffic_share
sudo systemctl enable traffic_share_bot
sudo systemctl enable traffic_share_bot_api
sudo systemctl start traffic_share
sudo systemctl start traffic_share_bot
sudo systemctl start traffic_share_bot_api

# Set up monitoring
echo "📊 Setting up monitoring..."
sudo apt install -y htop iotop nethogs

# Create monitoring script
sudo -u traffic_share tee /opt/traffic_share/monitor.sh > /dev/null << 'MONITOR_EOF'
#!/bin/bash
echo "=== Traffic Share System Status ==="
echo "Date: $(date)"
echo ""
echo "=== Services Status ==="
systemctl status traffic_share --no-pager -l
echo ""
systemctl status traffic_share_bot --no-pager -l
echo ""
systemctl status traffic_share_bot_api --no-pager -l
echo ""
echo "=== Database Status ==="
sudo -u postgres psql -c "SELECT count(*) as user_count FROM users;" traffic_share
echo ""
echo "=== Redis Status ==="
redis-cli ping
echo ""
echo "=== Disk Usage ==="
df -h
echo ""
echo "=== Memory Usage ==="
free -h
echo ""
echo "=== Network Connections ==="
netstat -tulpn | grep -E ':(8000|8001|5432|6379)'
MONITOR_EOF

sudo chmod +x /opt/traffic_share/monitor.sh

# Create backup script
sudo -u traffic_share tee /opt/traffic_share/backup.sh > /dev/null << 'BACKUP_EOF'
#!/bin/bash
BACKUP_DIR="/opt/traffic_share/backups"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR

# Backup database
sudo -u postgres pg_dump traffic_share > $BACKUP_DIR/database_$DATE.sql

# Backup application files
tar -czf $BACKUP_DIR/app_$DATE.tar.gz /opt/traffic_share --exclude=venv --exclude=backups --exclude=logs

# Keep only last 7 days of backups
find $BACKUP_DIR -name "*.sql" -mtime +7 -delete
find $BACKUP_DIR -name "*.tar.gz" -mtime +7 -delete

echo "Backup completed: $DATE"
BACKUP_EOF

sudo chmod +x /opt/traffic_share/backup.sh

# Set up cron jobs
echo "⏰ Setting up cron jobs..."
sudo -u traffic_share crontab - << 'CRON_EOF'
# Backup database daily at 2 AM
0 2 * * * /opt/traffic_share/backup.sh

# Monitor system every 5 minutes
*/5 * * * * /opt/traffic_share/monitor.sh >> /opt/traffic_share/logs/monitor.log 2>&1
CRON_EOF

echo "✅ Production setup completed!"
echo ""
echo "🔧 Next steps:"
echo "1. Update /opt/traffic_share/.env.production with your actual credentials"
echo "2. Restart services: sudo systemctl restart traffic_share traffic_share_bot traffic_share_bot_api"
echo "3. Check logs: sudo journalctl -u traffic_share -f"
echo "4. Monitor system: /opt/traffic_share/monitor.sh"
echo ""
echo "🌐 Your application should be available at: https://$DOMAIN"
echo "📊 Admin dashboard: https://$DOMAIN/admin/"
echo "🔧 API documentation: https://$DOMAIN/docs"
