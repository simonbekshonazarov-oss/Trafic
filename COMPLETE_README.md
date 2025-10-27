# 🚀 TRAFFIC SHARE - TO'LIQ LOYIHA DOKUMENTATSIYASI

**VPS:** 185.139.230.196  
**Version:** 1.0.0  
**Status:** ✅ Production Ready

---

## 📋 MUNDARIJA

1. [Loyiha Haqida](#-loyiha-haqida)
2. [Texnologiyalar](#-texnologiyalar)
3. [Arxitektura](#-arxitektura)
4. [VPS Sozlash](#-vps-sozlash)
5. [Backend Deploy](#-backend-deploy)
6. [Flutter APK Build](#-flutter-apk-build)
7. [API Hujjatlari](#-api-hujjatlari)
8. [Troubleshooting](#-troubleshooting)
9. [Xavfsizlik](#-xavfsizlik)
10. [Monitoring](#-monitoring)

---

## 🎯 LOYIHA HAQIDA

**Traffic Share** - foydalanuvchilar internet trafiklarini ulashib pul ishlashlari mumkin bo'lgan platforma.

### Asosiy Xususiyatlar

- ✅ Telegram orqali login
- ✅ Real-time traffic monitoring
- ✅ Avtomatik hisob-kitob va to'lov
- ✅ Cryptomus payment integration
- ✅ Admin dashboard
- ✅ Buyer API (traffic allocation)
- ✅ Background tasks
- ✅ Rate limiting & Security

### Komponentlar

1. **Backend API** - FastAPI (Python 3.11+)
2. **Flutter App** - Android APK
3. **Telegram Bot** - python-telegram-bot
4. **Database** - PostgreSQL 15+
5. **Cache** - Redis 7+
6. **Payment** - Cryptomus

---

## 🛠️ TEXNOLOGIYALAR

### Backend
```
- Python 3.11+
- FastAPI 0.104+
- SQLAlchemy 2.0+
- PostgreSQL 15+
- Redis 7+
- Pydantic 2.5+
- JWT (python-jose)
- Bcrypt
```

### Frontend
```
- Flutter 3.0+
- Dart 3.0+
- Provider (state management)
- HTTP client
- Material Design 3
```

### Infrastructure
```
- Ubuntu 24.04 LTS
- Nginx (reverse proxy)
- Systemd (process management)
- UFW (firewall)
```

---

## 🏗️ ARXITEKTURA

```
┌─────────────────────────────────────────────────────────┐
│                    FLUTTER APP (APK)                    │
│  - Login Screen                                         │
│  - Traffic Sharing                                      │
│  - Balance & Payments                                   │
│  - Statistics                                           │
└────────────────┬────────────────────────────────────────┘
                 │ HTTP/JSON
                 ▼
┌─────────────────────────────────────────────────────────┐
│                  NGINX (Reverse Proxy)                  │
│              185.139.230.196:80 → :8000                 │
└────────────────┬────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────┐
│                    FASTAPI BACKEND                      │
│  ┌──────────┬──────────┬──────────┬──────────┐         │
│  │   Auth   │  Traffic │ Payment  │  Admin   │         │
│  │  Routes  │  Routes  │ Routes   │  Routes  │         │
│  └─────┬────┴─────┬────┴─────┬────┴─────┬────┘         │
│        │          │          │          │               │
│  ┌─────▼──────────▼──────────▼──────────▼─────┐        │
│  │            SERVICES LAYER                   │        │
│  │  - Auth Service                             │        │
│  │  - Traffic Service                          │        │
│  │  - Payment Service (Cryptomus)              │        │
│  │  - Buyer Service                            │        │
│  │  - Notification Service                     │        │
│  └─────┬──────────────────────────────┬────────┘        │
│        │                              │                 │
│  ┌─────▼──────┐              ┌────────▼────────┐        │
│  │ PostgreSQL │              │     Redis       │        │
│  │  Database  │              │  Cache/Limiter  │        │
│  └────────────┘              └─────────────────┘        │
└─────────────────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────┐
│                   TELEGRAM BOT                          │
│  - Login code delivery                                  │
│  - Notifications                                        │
│  - Admin commands                                       │
└─────────────────────────────────────────────────────────┘
```

---

## 🔧 VPS SOZLASH

### 1. SSH Orqali Ulanish

```bash
ssh ubuntu@185.139.230.196
```

### 2. Tizimni Yangilash

```bash
sudo apt update && sudo apt upgrade -y
```

### 3. PostgreSQL O'rnatish

**To'liq qo'llanma:** `INSTALL_POSTGRESQL_REDIS.md`

```bash
# O'rnatish
sudo apt install postgresql postgresql-contrib -y

# Database yaratish
sudo -u postgres psql
CREATE DATABASE traffic_share;
CREATE USER traffic_user WITH PASSWORD 'QuvvatliParol_2024!';
GRANT ALL PRIVILEGES ON DATABASE traffic_share TO traffic_user;
\q

# Test
psql -h localhost -U traffic_user -d traffic_share
```

### 4. Redis O'rnatish

```bash
# O'rnatish
sudo apt install redis-server -y

# Start
sudo systemctl start redis-server
sudo systemctl enable redis-server

# Test
redis-cli ping
```

### 5. Python va Dependencies

```bash
# Python 3.11
sudo apt install python3.11 python3.11-venv python3-pip -y

# Boshqa dependencies
sudo apt install nginx git curl -y
```

---

## 🚀 BACKEND DEPLOY

### Avtomatik Deploy (Tavsiya etiladi)

```bash
# 1. Loyihani ko'chirish
cd /opt
sudo git clone <your-repo> traffic_share
sudo chown -R ubuntu:ubuntu traffic_share
cd traffic_share

# 2. Build script ishga tushirish
chmod +x BUILD_COMPLETE.sh
./BUILD_COMPLETE.sh
```

Build script avtomatik bajaradi:
- ✅ Virtual environment yaratish
- ✅ Dependencies o'rnatish
- ✅ .env tekshirish
- ✅ Database connection test
- ✅ Database initialization
- ✅ Systemd services yaratish
- ✅ Nginx sozlash
- ✅ Services ishga tushirish
- ✅ Health check

### Manual Deploy

#### 1. Loyihani Ko'chirish

```bash
# Git orqali
cd /opt
sudo git clone <repo-url> traffic_share

# Yoki SCP orqali (local dan)
scp -r /workspace ubuntu@185.139.230.196:/opt/traffic_share
```

#### 2. Virtual Environment

```bash
cd /opt/traffic_share
python3.11 -m venv venv
source venv/bin/activate
```

#### 3. Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

#### 4. Environment Sozlash

```bash
cp .env.example .env
nano .env
```

Minimal sozlamalar:

```env
DATABASE_URL=postgresql://traffic_user:QuvvatliParol_2024!@localhost:5432/traffic_share
REDIS_URL=redis://localhost:6379/0
SECRET_KEY=very-long-secret-key-change-this-immediately-32-chars-min
TELEGRAM_BOT_TOKEN=your-bot-token-from-botfather
TELEGRAM_ADMIN_IDS=your-telegram-id
CRYPTOMUS_API_KEY=your-cryptomus-api-key
CRYPTOMUS_MERCHANT_ID=your-merchant-id
```

#### 5. Database Initialization

```bash
python traffic_share/scripts/init_db.py
```

Success bo'lsa:
```
Database initialized successfully!
```

#### 6. Test Ishga Tushirish

```bash
# Manual test
uvicorn traffic_share.server.main:app --host 0.0.0.0 --port 8000

# Browser da:
# http://185.139.230.196:8000/docs
```

#### 7. Systemd Services

**API Service:**

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

**Bot Service:**

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

**Tasks Service:**

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

**Enable & Start:**

```bash
sudo systemctl daemon-reload
sudo systemctl enable traffic-share-api traffic-share-bot traffic-share-tasks
sudo systemctl start traffic-share-api traffic-share-bot traffic-share-tasks

# Status
sudo systemctl status traffic-share-api
```

#### 8. Nginx Sozlash

```bash
sudo nano /etc/nginx/sites-available/traffic-share
```

```nginx
server {
    listen 80;
    server_name 185.139.230.196;

    location /api {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }

    location /docs {
        proxy_pass http://127.0.0.1:8000;
    }

    location /openapi.json {
        proxy_pass http://127.0.0.1:8000;
    }
}
```

```bash
sudo ln -s /etc/nginx/sites-available/traffic-share /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

#### 9. Firewall

```bash
sudo ufw allow 22/tcp   # SSH
sudo ufw allow 80/tcp   # HTTP
sudo ufw allow 443/tcp  # HTTPS
sudo ufw enable
```

---

## 📱 FLUTTER APK BUILD

### Avtomatik Build

```bash
cd /workspace/app
chmod +x build_apk.sh

# Release APK
./build_apk.sh release

# Debug APK
./build_apk.sh debug

# Split APKs
./build_apk.sh split
```

### Manual Build

#### 1. Prerequisites

```bash
# Flutter o'rnatilganligini tekshiring
flutter doctor

# Dependencies
flutter pub get
```

#### 2. API URL Sozlash

`lib/utils/constants.dart`:

```dart
static const String baseUrl = 'http://185.139.230.196/api';
```

#### 3. Build

```bash
# Release APK
flutter build apk --release

# Split APKs (tavsiya etiladi)
flutter build apk --split-per-abi --release

# Output
# build/app/outputs/flutter-apk/app-release.apk
```

#### 4. Signing (Production uchun)

**Keystore yaratish:**

```bash
keytool -genkey -v -keystore ~/traffic-share-key.jks \
  -keyalg RSA -keysize 2048 -validity 10000 \
  -alias traffic-share
```

**android/key.properties:**

```properties
storePassword=your-password
keyPassword=your-password
keyAlias=traffic-share
storeFile=/path/to/traffic-share-key.jks
```

**android/app/build.gradle:**

```gradle
def keystoreProperties = new Properties()
def keystorePropertiesFile = rootProject.file('key.properties')
if (keystorePropertiesFile.exists()) {
    keystoreProperties.load(new FileInputStream(keystorePropertiesFile))
}

android {
    signingConfigs {
        release {
            keyAlias keystoreProperties['keyAlias']
            keyPassword keystoreProperties['keyPassword']
            storeFile keystoreProperties['storeFile'] ? file(keystoreProperties['storeFile']) : null
            storePassword keystoreProperties['storePassword']
        }
    }
    buildTypes {
        release {
            signingConfig signingConfigs.release
        }
    }
}
```

#### 5. Install

```bash
# USB orqali
flutter install

# Yoki adb
adb install build/app/outputs/flutter-apk/app-release.apk
```

---

## 📖 API HUJJATLARI

### Base URL

```
http://185.139.230.196/api
```

### Swagger Documentation

```
http://185.139.230.196/docs
```

### Asosiy Endpointlar

#### Authentication

```http
POST /api/auth/register
POST /api/auth/request_login_code
POST /api/auth/verify_code
POST /api/auth/refresh
```

#### User

```http
GET  /api/user/me
POST /api/user/update
POST /api/user/device/register
GET  /api/user/devices
```

#### Traffic

```http
POST /api/traffic/start
POST /api/traffic/update
POST /api/traffic/stop
GET  /api/traffic/history
GET  /api/traffic/summary
```

#### Payment

```http
GET  /api/balance
POST /api/withdraw/request
GET  /api/withdraw/status/{payment_id}
```

#### System

```http
GET /api/system/health
GET /api/system/version
```

### Request Example

```bash
# Login code so'rash
curl -X POST http://185.139.230.196/api/auth/request_login_code \
  -H "Content-Type: application/json" \
  -d '{"telegram_id": 123456789}'

# Code verification
curl -X POST http://185.139.230.196/api/auth/verify_code \
  -H "Content-Type: application/json" \
  -d '{"telegram_id": 123456789, "code": "123456"}'

# User profile (auth required)
curl -X GET http://185.139.230.196/api/user/me \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

## 🐛 TROUBLESHOOTING

### Backend Issues

#### Service ishlamayotgan

```bash
# Status tekshirish
sudo systemctl status traffic-share-api

# Logs
sudo journalctl -u traffic-share-api -n 50 --no-pager

# Restart
sudo systemctl restart traffic-share-api
```

#### Database connection error

```bash
# PostgreSQL ishlayaptimi?
sudo systemctl status postgresql

# Test connection
psql -h localhost -U traffic_user -d traffic_share

# .env tekshirish
cat /opt/traffic_share/.env | grep DATABASE_URL
```

#### Redis connection error

```bash
# Redis ishlayaptimi?
sudo systemctl status redis-server

# Test
redis-cli ping

# .env tekshirish
cat /opt/traffic_share/.env | grep REDIS_URL
```

### Flutter Issues

#### Build failed

```bash
# Clean
flutter clean

# Get dependencies
flutter pub get

# Rebuild
flutter build apk --release
```

#### Network error

`android/app/src/main/AndroidManifest.xml` da:

```xml
<application
    android:usesCleartextTraffic="true">
```

---

## 🔐 XAVFSIZLIK

### SSL/HTTPS (Production)

```bash
# Certbot o'rnatish
sudo apt install certbot python3-certbot-nginx

# SSL sertifikat (domain kerak)
sudo certbot --nginx -d yourdomain.com

# Auto-renewal
sudo certbot renew --dry-run
```

### Secret Keys

- ✅ SECRET_KEY kamida 32 character
- ✅ Database parol quvvatli bo'lishi kerak
- ✅ `.env` faylni git ga qo'shma
- ✅ Tokenlarni hash qilib saqlang

### Firewall

```bash
# Faqat kerakli portlar ochiq
sudo ufw status

# SSH port o'zgartirish (optional)
sudo nano /etc/ssh/sshd_config
# Port 2222
sudo systemctl restart sshd
sudo ufw allow 2222/tcp
```

---

## 📊 MONITORING

### Logs

```bash
# API logs
sudo journalctl -u traffic-share-api -f

# Application logs
tail -f /opt/traffic_share/logs/traffic_share.log

# Nginx logs
tail -f /var/log/nginx/access.log
tail -f /var/log/nginx/error.log
```

### System Metrics

```bash
# CPU, Memory
htop

# Disk usage
df -h

# Network
netstat -tulpn | grep LISTEN

# PostgreSQL
sudo -u postgres psql -c "SELECT count(*) FROM pg_stat_activity;"

# Redis
redis-cli info memory
```

### Health Checks

```bash
# API health
curl http://185.139.230.196/api/system/health

# Services status
sudo systemctl status traffic-share-api
sudo systemctl status traffic-share-bot
sudo systemctl status traffic-share-tasks
sudo systemctl status postgresql
sudo systemctl status redis-server
sudo systemctl status nginx
```

---

## 📋 MANAGEMENT COMMANDS

### Service Management

```bash
# Start
sudo systemctl start traffic-share-api

# Stop
sudo systemctl stop traffic-share-api

# Restart
sudo systemctl restart traffic-share-api

# Status
sudo systemctl status traffic-share-api

# Enable (auto-start)
sudo systemctl enable traffic-share-api

# Disable
sudo systemctl disable traffic-share-api
```

### Database Management

```bash
# Backup
sudo -u postgres pg_dump traffic_share > backup_$(date +%Y%m%d).sql

# Restore
sudo -u postgres psql traffic_share < backup.sql

# Connect
psql -h localhost -U traffic_user -d traffic_share
```

### Application Management

```bash
# Update code
cd /opt/traffic_share
git pull
source venv/bin/activate
pip install -r requirements.txt
sudo systemctl restart traffic-share-api

# View logs
tail -f logs/traffic_share.log

# Clear old sessions
python traffic_share/scripts/clear_sessions.py

# Export stats
python traffic_share/scripts/export_stats.py
```

---

## ✅ PRODUCTION CHECKLIST

### Backend

- [ ] PostgreSQL o'rnatildi va sozlandi
- [ ] Redis o'rnatildi
- [ ] .env to'liq sozlandi
- [ ] SECRET_KEY o'zgartirildi
- [ ] Database initialized
- [ ] Systemd services yaratildi
- [ ] Services ishlab turibdi
- [ ] Nginx sozlandi
- [ ] Firewall sozlandi
- [ ] SSL sertifikat (production)
- [ ] Backup strategy
- [ ] Monitoring setup
- [ ] Logs rotation
- [ ] Health check ishlayapti

### Frontend

- [ ] API URL sozlandi
- [ ] APK build qilindi
- [ ] Signing setup (release)
- [ ] Android permissions sozlandi
- [ ] Test qilindi
- [ ] Version updated
- [ ] Distribution ready

### Testing

- [ ] API endpoints test
- [ ] Authentication flow test
- [ ] Traffic session test
- [ ] Payment flow test (sandbox)
- [ ] Flutter app test
- [ ] Integration test
- [ ] Load test
- [ ] Security audit

---

## 📞 SUPPORT

### Documentation

- `COMPLETE_README.md` - Ushbu fayl
- `VPS_DEPLOYMENT.md` - VPS deployment
- `INSTALL_POSTGRESQL_REDIS.md` - Database setup
- `BUILD_INSTRUCTIONS.md` - Flutter build
- `PROJECT_README.md` - Backend details

### Scripts

- `BUILD_COMPLETE.sh` - Backend auto-deploy
- `build_apk.sh` - Flutter auto-build
- `run_server.sh` - Simple server start

### Links

- API Docs: http://185.139.230.196/docs
- Health: http://185.139.230.196/api/system/health

---

## 🎉 XULOSA

Loyiha to'liq tayyor va production ga deploy qilishga tayyor!

**Keyingi qadamlar:**

1. VPS ga backend deploy qiling (`BUILD_COMPLETE.sh`)
2. Flutter APK build qiling (`build_apk.sh`)
3. Test qiling
4. Foydalanuvchilarga taqsimlang

**Omad!** 🚀
