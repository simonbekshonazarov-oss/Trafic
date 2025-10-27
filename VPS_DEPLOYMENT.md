# 🚀 VPS Deployment - Ubuntu 24.04

**VPS IP:** 185.139.230.196

## 1️⃣ VPS ga Ulanish

```bash
ssh root@185.139.230.196
# yoki
ssh ubuntu@185.139.230.196
```

## 2️⃣ Sistem Yangilash

```bash
sudo apt update && sudo apt upgrade -y
```

## 3️⃣ Python 3.11+ O'rnatish

```bash
sudo apt install python3.11 python3.11-venv python3-pip -y
python3.11 --version
```

## 4️⃣ PostgreSQL Sozlash

PostgreSQL allaqachon o'rnatilgan. Database yaratish:

```bash
sudo -u postgres psql

# PostgreSQL ichida:
CREATE DATABASE traffic_share;
CREATE USER traffic_user WITH PASSWORD 'quvvatli_parol_123';
GRANT ALL PRIVILEGES ON DATABASE traffic_share TO traffic_user;
\q
```

## 5️⃣ Redis Sozlash

Redis allaqachon o'rnatilgan. Tekshirish:

```bash
redis-cli ping
# PONG javobini berishi kerak
```

## 6️⃣ Loyihani VPS ga Ko'chirish

### Variant A: Git orqali (Tavsiya etiladi)

```bash
cd /opt
sudo git clone https://github.com/your-repo/traffic_share.git
sudo chown -R ubuntu:ubuntu traffic_share
cd traffic_share
```

### Variant B: SCP orqali

Local kompyuterdan:

```bash
scp -r /workspace ubuntu@185.139.230.196:/opt/traffic_share
```

## 7️⃣ Virtual Environment va Dependencies

```bash
cd /opt/traffic_share

# Virtual environment
python3.11 -m venv venv
source venv/bin/activate

# Dependencies o'rnatish
pip install --upgrade pip
pip install -r requirements.txt
```

## 8️⃣ Environment Sozlash

```bash
cp .env.example .env
nano .env
```

`.env` faylni to'ldiring:

```env
# Application
APP_NAME=Traffic Share
APP_VERSION=1.0.0
DEBUG=False

# Server
HOST=0.0.0.0
PORT=8000
WORKERS=4

# Security
SECRET_KEY=YOUR-VERY-LONG-SECRET-KEY-MIN-32-CHARACTERS-CHANGE-THIS
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
REFRESH_TOKEN_EXPIRE_DAYS=30

# Database (VPS local)
DATABASE_URL=postgresql://traffic_user:quvvatli_parol_123@localhost:5432/traffic_share
DB_POOL_SIZE=20
DB_MAX_OVERFLOW=10
DB_ECHO=False

# Redis (VPS local)
REDIS_URL=redis://localhost:6379/0
REDIS_KEY_PREFIX=traffic_share:

# Telegram Bot
TELEGRAM_BOT_TOKEN=YOUR_BOT_TOKEN_FROM_BOTFATHER
TELEGRAM_ADMIN_IDS=YOUR_TELEGRAM_ID
TELEGRAM_ADMIN_CHANNEL=

# Cryptomus Payment Gateway
CRYPTOMUS_API_KEY=your-cryptomus-api-key
CRYPTOMUS_MERCHANT_ID=your-merchant-id
CRYPTOMUS_API_URL=https://api.cryptomus.com/v1
CRYPTOMUS_WEBHOOK_SECRET=your-webhook-secret

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
LOG_FILE=/opt/traffic_share/logs/traffic_share.log
LOG_MAX_SIZE_MB=10
LOG_BACKUP_COUNT=5

# CORS (VPS IP)
CORS_ORIGINS=*

# Background Tasks
CLEANUP_TASK_INTERVAL=300
STATS_TASK_INTERVAL=3600
BACKUP_TASK_INTERVAL=86400
```

## 9️⃣ Database Initialization

```bash
source venv/bin/activate
python traffic_share/scripts/init_db.py

# Test data (ixtiyoriy)
python traffic_share/scripts/seed_data.py
```

## 🔟 Systemd Service Yaratish

### API Service

```bash
sudo nano /etc/systemd/system/traffic-share-api.service
```

```ini
[Unit]
Description=Traffic Share API
After=network.target postgresql.service redis.service

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/opt/traffic_share
Environment="PATH=/opt/traffic_share/venv/bin"
ExecStart=/opt/traffic_share/venv/bin/uvicorn traffic_share.server.main:app --host 0.0.0.0 --port 8000 --workers 4
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

### Telegram Bot Service

```bash
sudo nano /etc/systemd/system/traffic-share-bot.service
```

```ini
[Unit]
Description=Traffic Share Telegram Bot
After=network.target traffic-share-api.service

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/opt/traffic_share
Environment="PATH=/opt/traffic_share/venv/bin"
ExecStart=/opt/traffic_share/venv/bin/python -m traffic_share.bot.bot
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

### Background Tasks Service

```bash
sudo nano /etc/systemd/system/traffic-share-tasks.service
```

```ini
[Unit]
Description=Traffic Share Background Tasks
After=network.target traffic-share-api.service

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/opt/traffic_share
Environment="PATH=/opt/traffic_share/venv/bin"
ExecStart=/opt/traffic_share/venv/bin/python -m traffic_share.server.tasks.cleanup_task
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

## 1️⃣1️⃣ Servicelarni Ishga Tushirish

```bash
# Reload systemd
sudo systemctl daemon-reload

# Enable services
sudo systemctl enable traffic-share-api
sudo systemctl enable traffic-share-bot
sudo systemctl enable traffic-share-tasks

# Start services
sudo systemctl start traffic-share-api
sudo systemctl start traffic-share-bot
sudo systemctl start traffic-share-tasks

# Check status
sudo systemctl status traffic-share-api
sudo systemctl status traffic-share-bot
sudo systemctl status traffic-share-tasks
```

## 1️⃣2️⃣ Nginx Reverse Proxy O'rnatish

```bash
sudo apt install nginx -y
```

```bash
sudo nano /etc/nginx/sites-available/traffic-share
```

```nginx
server {
    listen 80;
    server_name 185.139.230.196;

    # API
    location /api {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # API Docs
    location /docs {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    # Health check
    location /health {
        proxy_pass http://127.0.0.1:8000/api/system/health;
    }
}
```

```bash
# Enable site
sudo ln -s /etc/nginx/sites-available/traffic-share /etc/nginx/sites-enabled/

# Test nginx config
sudo nginx -t

# Restart nginx
sudo systemctl restart nginx
sudo systemctl enable nginx
```

## 1️⃣3️⃣ Firewall Sozlash

```bash
# UFW firewall
sudo ufw allow 22/tcp      # SSH
sudo ufw allow 80/tcp      # HTTP
sudo ufw allow 443/tcp     # HTTPS (keyinchalik)
sudo ufw enable

# Check status
sudo ufw status
```

## 1️⃣4️⃣ SSL Sertifikat (HTTPS)

### Let's Encrypt bilan

```bash
# Certbot o'rnatish
sudo apt install certbot python3-certbot-nginx -y

# Domain bilan (agar bor bo'lsa)
sudo certbot --nginx -d yourdomain.com

# Yoki IP bilan (self-signed)
sudo openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout /etc/ssl/private/nginx-selfsigned.key \
  -out /etc/ssl/certs/nginx-selfsigned.crt
```

## 1️⃣5️⃣ Test Qilish

```bash
# Health check
curl http://185.139.230.196/health

# API docs (browser)
# http://185.139.230.196/docs

# Logs
sudo journalctl -u traffic-share-api -f
sudo journalctl -u traffic-share-bot -f
```

## 1️⃣6️⃣ Monitoring va Logs

```bash
# API logs
sudo tail -f /opt/traffic_share/logs/traffic_share.log

# System logs
sudo journalctl -u traffic-share-api -n 100
sudo journalctl -u traffic-share-bot -n 100

# Service status
sudo systemctl status traffic-share-api
sudo systemctl status traffic-share-bot
sudo systemctl status traffic-share-tasks
```

## 1️⃣7️⃣ Backup Setup

```bash
# Cron job for daily backup
crontab -e

# Add this line (daily at 2 AM)
0 2 * * * /opt/traffic_share/venv/bin/python /opt/traffic_share/traffic_share/scripts/backup_task.py
```

## 🔧 Troubleshooting

### Service ishlamayotgan bo'lsa:

```bash
# Restart
sudo systemctl restart traffic-share-api

# Logs
sudo journalctl -u traffic-share-api -n 50 --no-pager
```

### Database connection error:

```bash
# Check PostgreSQL
sudo systemctl status postgresql

# Check database
sudo -u postgres psql -c "\l"
```

### Redis connection error:

```bash
# Check Redis
sudo systemctl status redis
redis-cli ping
```

## 📱 APK uchun API URL

Flutter ilovada API URL:

```dart
const String API_BASE_URL = "http://185.139.230.196/api";
// yoki domain bilan
const String API_BASE_URL = "https://yourdomain.com/api";
```

## ✅ Deploy Checklist

- [x] VPS ga ulanish
- [x] Python, PostgreSQL, Redis tekshirish
- [x] Loyihani ko'chirish
- [x] Virtual environment yaratish
- [x] Dependencies o'rnatish
- [x] .env sozlash
- [x] Database initialization
- [x] Systemd services yaratish
- [x] Servicelarni ishga tushirish
- [x] Nginx sozlash
- [x] Firewall sozlash
- [x] SSL sertifikat (HTTPS)
- [x] Test qilish
- [x] Backup sozlash
- [x] Monitoring setup

## 🎉 Tayyor!

API ishlayapti:
- **API:** http://185.139.230.196/api
- **Docs:** http://185.139.230.196/docs
- **Health:** http://185.139.230.196/health

Flutter ilovada API URL ni sozlang va APK build qiling!
