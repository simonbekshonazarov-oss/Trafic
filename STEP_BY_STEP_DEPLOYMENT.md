# 📋 QADAM-BA-QADAM DEPLOYMENT QO'LLANMASI

**VPS:** 185.139.230.196  
**OS:** Ubuntu 24.04

---

## 🎯 UMUMIY JARAYON

```
[1] VPS Tayyorlash (PostgreSQL, Redis)
    ↓
[2] Backend Deploy (FastAPI)
    ↓
[3] Flutter APK Build
    ↓
[4] Testing
    ↓
[5] Production Launch
```

---

## ✅ BOSHLASHDAN OLDIN

### Kerakli Ma'lumotlar

1. **VPS SSH Access**
   - IP: 185.139.230.196
   - User: ubuntu yoki root
   - Password yoki SSH key

2. **Telegram Bot**
   - Bot token (@BotFather dan)
   - Admin Telegram ID

3. **Cryptomus**
   - API key
   - Merchant ID

4. **Flutter**
   - Flutter SDK o'rnatilgan
   - Android Studio yoki Android SDK

---

## 📍 QADAM 1: VPS GA ULANISH

```bash
ssh ubuntu@185.139.230.196
```

Agar parol so'ralsa, VPS parolini kiriting.

---

## 📍 QADAM 2: TIZIMNI YANGILASH

```bash
sudo apt update
sudo apt upgrade -y
sudo apt install -y git curl wget nano htop
```

Kutish: 5-10 daqiqa

---

## 📍 QADAM 3: POSTGRESQL O'RNATISH

### 3.1. O'rnatish

```bash
sudo apt install -y postgresql postgresql-contrib
```

### 3.2. Service Tekshirish

```bash
sudo systemctl status postgresql
# Active (running) bo'lishi kerak
```

### 3.3. Database Yaratish

```bash
sudo -u postgres psql << 'EOF'
CREATE DATABASE traffic_share;
CREATE USER traffic_user WITH PASSWORD 'TrafficShare_DB_2024!';
GRANT ALL PRIVILEGES ON DATABASE traffic_share TO traffic_user;
ALTER DATABASE traffic_share OWNER TO traffic_user;
\c traffic_share
GRANT ALL ON SCHEMA public TO traffic_user;
EOF
```

### 3.4. Test

```bash
psql -h localhost -U traffic_user -d traffic_share -c "SELECT 1;"
```

Parol: `TrafficShare_DB_2024!`

Agar `?column? | 1` deb ko'rsatsa - SUCCESS! ✅

---

## 📍 QADAM 4: REDIS O'RNATISH

### 4.1. O'rnatish

```bash
sudo apt install -y redis-server
```

### 4.2. Service Start

```bash
sudo systemctl start redis-server
sudo systemctl enable redis-server
sudo systemctl status redis-server
```

### 4.3. Test

```bash
redis-cli ping
```

Javob: `PONG` - SUCCESS! ✅

---

## 📍 QADAM 5: PYTHON VA DEPENDENCIES

```bash
# Python 3.11
sudo apt install -y python3.11 python3.11-venv python3-pip

# Test
python3.11 --version
# Python 3.11.x
```

---

## 📍 QADAM 6: LOYIHANI KO'CHIRISH

### Variant A: Agar Git Repository Bor Bo'lsa

```bash
cd /opt
sudo git clone https://github.com/your-username/traffic-share.git traffic_share
sudo chown -R ubuntu:ubuntu traffic_share
cd traffic_share
```

### Variant B: Local dan SCP

**Local terminalda:**

```bash
# Butun loyihani ko'chirish
scp -r /workspace ubuntu@185.139.230.196:/tmp/traffic_share
```

**VPS da:**

```bash
sudo mv /tmp/traffic_share /opt/
sudo chown -R ubuntu:ubuntu /opt/traffic_share
cd /opt/traffic_share
```

### Variant C: Manual Upload

1. Loyihani zip qiling
2. FileZilla yoki WinSCP orqali upload qiling
3. VPS da unzip qiling

```bash
cd /opt
sudo unzip traffic_share.zip
sudo chown -R ubuntu:ubuntu traffic_share
```

---

## 📍 QADAM 7: BACKEND DEPLOY (AVTOMATIK)

```bash
cd /opt/traffic_share

# 1. Build scriptni executable qilish
chmod +x BUILD_COMPLETE.sh

# 2. .env sozlash
cp .env.example .env
nano .env
```

### .env Faylni To'ldirish

**MUHIM:** Quyidagi qiymatlarni o'zgartiring!

```env
# Database
DATABASE_URL=postgresql://traffic_user:TrafficShare_DB_2024!@localhost:5432/traffic_share

# Redis
REDIS_URL=redis://localhost:6379/0

# Security (O'ZGARTIRING!)
SECRET_KEY=bu-juda-uzun-va-quvvatli-secret-key-min-32-characters-12345678

# Server
HOST=0.0.0.0
PORT=8000
WORKERS=4
DEBUG=False

# Telegram Bot (O'ZGARTIRING!)
TELEGRAM_BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz-YOUR-TOKEN
TELEGRAM_ADMIN_IDS=123456789
TELEGRAM_ADMIN_CHANNEL=

# Cryptomus (O'ZGARTIRING!)
CRYPTOMUS_API_KEY=your-cryptomus-api-key-here
CRYPTOMUS_MERCHANT_ID=your-merchant-id-here
CRYPTOMUS_API_URL=https://api.cryptomus.com/v1

# Other
PRICE_PER_GB=0.50
MIN_WITHDRAWAL_AMOUNT=5.0
LOG_LEVEL=INFO
CORS_ORIGINS=*
```

**Ctrl+O** (saqlash), **Enter**, **Ctrl+X** (chiqish)

### Build va Deploy

```bash
./BUILD_COMPLETE.sh
```

Bu script 10-15 daqiqada:
- ✅ Virtual environment yaratadi
- ✅ Dependencies o'rnatadi
- ✅ Database test qiladi
- ✅ Tables yaratadi
- ✅ Systemd services yaratadi
- ✅ Nginx sozlaydi
- ✅ Services ishga tushiradi
- ✅ Health check qiladi

### Natija

```
═══════════════════════════════════════════════════════════
BUILD COMPLETE
═══════════════════════════════════════════════════════════

✅ Backend build successful!

Services:
  - traffic-share-api     active
  - traffic-share-bot     active
  - traffic-share-tasks   active

API Endpoints:
  - Health: http://185.139.230.196/api/system/health
  - Docs:   http://185.139.230.196/docs
```

---

## 📍 QADAM 8: BACKEND TEST

### Browser da

```
http://185.139.230.196/docs
```

Swagger UI ochilishi kerak - barcha API endpointlar ko'rinadi ✅

### cURL orqali

```bash
# Health check
curl http://185.139.230.196/api/system/health

# Javob:
{"status":"ok","timestamp":"2025-10-27T...","version":"1.0.0"}

# Version
curl http://185.139.230.196/api/system/version
```

---

## 📍 QADAM 9: FLUTTER APK BUILD

**Local kompyuterda** (Windows/Mac/Linux):

### 9.1. Flutter Tekshirish

```bash
flutter doctor
```

Hamma ✅ yoki ! bo'lishi kerak.

### 9.2. Loyiha Ochish

```bash
cd /workspace/app
```

### 9.3. Dependencies

```bash
flutter pub get
```

### 9.4. API URL Tekshirish

`lib/utils/constants.dart` faylda:

```dart
static const String baseUrl = 'http://185.139.230.196/api';
```

✅ To'g'ri bo'lishi kerak!

### 9.5. Build (AVTOMATIK)

```bash
chmod +x build_apk.sh
./build_apk.sh release
```

Bu script 5-10 daqiqada APK yaratadi.

### Yoki Manual:

```bash
flutter clean
flutter pub get
flutter build apk --release
```

### 9.6. APK Location

```
build/app/outputs/flutter-apk/app-release.apk
```

File size: ~20-30 MB ✅

---

## 📍 QADAM 10: APK TEST QILISH

### Telefonga O'rnatish

#### Variant A: USB Cable

```bash
# Android device ni USB ga ulang
# USB debugging yoqing

# Install
flutter install
# yoki
adb install build/app/outputs/flutter-apk/app-release.apk
```

#### Variant B: File Transfer

1. APK ni telefonga ko'chiring (USB, Google Drive, etc.)
2. Telefonda APK ni toping
3. Install bosing
4. "Unknown sources" ga ruxsat bering

### Test Qilish

1. **Ilovani oching**
2. **Telegram ID kiriting**
3. **"Send Code" bosing**
4. **Telegram botdan kod oling** (5-10 soniya kutish)
5. **Kodni kiriting va verify bosing**
6. **Home screen ochiladi** ✅
7. **"Start Sharing" bosing**
8. **Traffic ko'rinadi** ✅
9. **Balance yangilanadi** ✅

---

## 📍 QADAM 11: PRODUCTION SETUP

### 11.1. Nginx (allaqachon sozlangan)

Test:

```bash
curl http://185.139.230.196/api/system/health
```

### 11.2. Firewall

```bash
sudo ufw status

# Agar inactive bo'lsa:
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
```

### 11.3. SSL (HTTPS) - Optional

Agar domain bor bo'lsa:

```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d yourdomain.com
```

### 11.4. Monitoring

```bash
# htop o'rnatish
sudo apt install htop

# Ishlatish
htop
```

---

## 📍 QADAM 12: BACKUP SOZLASH

### 12.1. Database Backup Script

```bash
nano ~/backup_db.sh
```

```bash
#!/bin/bash
BACKUP_DIR=~/backups
mkdir -p $BACKUP_DIR
DATE=$(date +%Y%m%d_%H%M%S)
sudo -u postgres pg_dump traffic_share | gzip > $BACKUP_DIR/db_backup_$DATE.sql.gz
echo "Backup created: $BACKUP_DIR/db_backup_$DATE.sql.gz"
```

```bash
chmod +x ~/backup_db.sh
```

### 12.2. Cron Job (Kunlik Backup)

```bash
crontab -e
```

Qo'shing:

```cron
# Har kuni soat 2:00 da backup
0 2 * * * /home/ubuntu/backup_db.sh
```

---

## 📍 QADAM 13: TELEGRAM BOT SOZLASH

### 13.1. Bot Yaratish

1. Telegram da **@BotFather** ni oching
2. `/newbot` yuboring
3. **Bot nomi:** Traffic Share Bot
4. **Username:** @trafficshare_bot (yoki boshqa)
5. **Token oling:** `1234567890:ABCdef...`

### 13.2. Admin ID Aniqlash

1. **@userinfobot** ni oching
2. `/start` bosing
3. **ID ni ko'ring:** mesalan `123456789`

### 13.3. .env Yangilash

```bash
nano /opt/traffic_share/.env
```

```env
TELEGRAM_BOT_TOKEN=1234567890:ABCdef... (real token)
TELEGRAM_ADMIN_IDS=123456789 (real ID)
```

### 13.4. Bot Restart

```bash
sudo systemctl restart traffic-share-bot
sudo systemctl status traffic-share-bot
```

### 13.5. Test

Telegram da botingizga:
```
/start
```

Javob kelishi kerak! ✅

---

## 📍 QADAM 14: CRYPTOMUS SOZLASH

### 14.1. Account Yaratish

1. https://cryptomus.com ga kiring
2. Sign Up
3. Email verify qiling

### 14.2. Merchant Yaratish

1. Dashboard → Merchants
2. Create Merchant
3. Merchant name: Traffic Share
4. Currency: USD

### 14.3. API Keys

1. Settings → API
2. Generate API Key
3. API key va Merchant ID ni ko'ring

### 14.4. .env Yangilash

```bash
nano /opt/traffic_share/.env
```

```env
CRYPTOMUS_API_KEY=your-real-api-key
CRYPTOMUS_MERCHANT_ID=your-real-merchant-id
```

### 14.5. Webhook Setup

Cryptomus dashboard da:

```
Webhook URL: http://185.139.230.196/api/webhook/cryptomus
```

### 14.6. Restart

```bash
sudo systemctl restart traffic-share-api
```

---

## 📍 QADAM 15: YAKUNIY TEST

### 15.1. API Health

```bash
curl http://185.139.230.196/api/system/health
```

Kutilayotgan javob:
```json
{
  "status": "ok",
  "timestamp": "2025-10-27T...",
  "version": "1.0.0"
}
```

### 15.2. API Documentation

Browser:
```
http://185.139.230.196/docs
```

Swagger UI ochilishi kerak ✅

### 15.3. Services

```bash
sudo systemctl status traffic-share-api
sudo systemctl status traffic-share-bot
sudo systemctl status traffic-share-tasks
```

Barchasi **active (running)** bo'lishi kerak ✅

### 15.4. Database

```bash
psql -h localhost -U traffic_user -d traffic_share << EOF
SELECT COUNT(*) FROM users;
SELECT COUNT(*) FROM traffic_sessions;
EOF
```

Tables mavjud bo'lishi kerak ✅

### 15.5. Flutter App

1. APK ni telefonga o'rnating
2. Ilovani oching
3. Login qiling
4. Traffic sharing start qiling
5. Statistikani ko'ring

Hammasi ishlasa - SUCCESS! ✅

---

## 📍 QADAM 16: APK TARQATISH

### 16.1. VPS ga Upload

```bash
# Local dan
scp build/app/outputs/flutter-apk/app-release.apk \
    ubuntu@185.139.230.196:/var/www/html/
```

### 16.2. Nginx Download Sozlash

```bash
# VPS da
sudo mkdir -p /var/www/downloads
sudo cp /var/www/html/app-release.apk /var/www/downloads/traffic-share.apk
sudo chown -R www-data:www-data /var/www/downloads
```

Nginx config:

```bash
sudo nano /etc/nginx/sites-available/traffic-share
```

Qo'shing:

```nginx
location /downloads {
    alias /var/www/downloads;
    autoindex on;
}
```

```bash
sudo nginx -t
sudo systemctl reload nginx
```

### 16.3. Download Link

```
http://185.139.230.196/downloads/traffic-share.apk
```

Foydalanuvchilarga bu linkni bering! 📱

---

## 📍 QADAM 17: MONITORING SOZLASH

### 17.1. Logs Monitoring

```bash
# Real-time logs
sudo journalctl -u traffic-share-api -f

# Application logs
tail -f /opt/traffic_share/logs/traffic_share.log
```

### 17.2. System Monitoring

```bash
# Install htop
sudo apt install htop

# Monitor
htop
```

### 17.3. Metrics Endpoint

```bash
curl http://localhost:8000/api/admin/metrics
```

---

## 🎉 DEPLOYMENT COMPLETE!

### ✅ Nima Qildik?

1. ✅ VPS tayyorlandi (PostgreSQL, Redis)
2. ✅ Backend deploy qilindi (FastAPI)
3. ✅ Systemd services yaratildi
4. ✅ Nginx sozlandi
5. ✅ Firewall sozlandi
6. ✅ Telegram bot sozlandi
7. ✅ Cryptomus integratsiya qilindi
8. ✅ Flutter APK build qilindi
9. ✅ Test qilindi
10. ✅ APK tarqatish sozlandi

### 🚀 Ishga Tushdi!

**API:** http://185.139.230.196/api  
**Docs:** http://185.139.230.196/docs  
**APK:** http://185.139.230.196/downloads/traffic-share.apk

---

## 📊 DAILY OPERATIONS

### Har Kuni Tekshirish

```bash
# Services status
sudo systemctl status traffic-share-api

# Logs
tail -n 100 /opt/traffic_share/logs/traffic_share.log

# Database size
sudo -u postgres psql -c "SELECT pg_size_pretty(pg_database_size('traffic_share'));"

# Disk space
df -h
```

### Muammolar Yuzaga Kelsa

```bash
# Restart services
sudo systemctl restart traffic-share-api
sudo systemctl restart traffic-share-bot

# Logs tekshirish
sudo journalctl -u traffic-share-api -n 100 --no-pager

# Manual start (debugging)
cd /opt/traffic_share
source venv/bin/activate
uvicorn traffic_share.server.main:app --host 0.0.0.0 --port 8000
```

---

## 🔄 UPDATE QILISH

Yangi versiya deploy qilish:

```bash
cd /opt/traffic_share

# Pull changes
git pull

# Update dependencies
source venv/bin/activate
pip install -r requirements.txt

# Database migrations (agar bor bo'lsa)
# alembic upgrade head

# Restart
sudo systemctl restart traffic-share-api
sudo systemctl restart traffic-share-bot
```

---

## 📞 SUPPORT

### Dokumentatsiya

- **START_HERE.md** - Bu fayl
- **COMPLETE_README.md** - To'liq qo'llanma
- **INSTALL_POSTGRESQL_REDIS.md** - Database setup
- **VPS_DEPLOYMENT.md** - Deployment details
- **app/BUILD_INSTRUCTIONS.md** - APK build

### Links

- API Docs: http://185.139.230.196/docs
- Health: http://185.139.230.196/api/system/health

### Commands

```bash
# Services
sudo systemctl status traffic-share-api
sudo systemctl restart traffic-share-api

# Logs
sudo journalctl -u traffic-share-api -f
tail -f /opt/traffic_share/logs/traffic_share.log

# Database
psql -h localhost -U traffic_user -d traffic_share
```

---

## ✅ CHECKLIST

Deploy tugagandan keyin:

- [ ] PostgreSQL o'rnatildi va ishlayapti
- [ ] Redis o'rnatildi va ishlayapti
- [ ] Loyiha /opt/traffic_share ga ko'chirildi
- [ ] .env to'liq sozlandi
- [ ] BUILD_COMPLETE.sh muvaffaqiyatli ishladi
- [ ] Services active holatda
- [ ] Health check SUCCESS
- [ ] API docs ochiladi (http://185.139.230.196/docs)
- [ ] Telegram bot javob beradi
- [ ] APK build qilindi
- [ ] APK telefonda ishlaydi
- [ ] Login flow ishlaydi
- [ ] Traffic sharing ishlaydi
- [ ] Statistika ko'rinadi
- [ ] Balance yangilanadi

---

## 🎉 TABRIKLAYMIZ!

Loyihangiz production da ishlamoqda!

**Next Steps:**
1. ✅ Monitoring setup
2. ✅ SSL/HTTPS (domain bilan)
3. ✅ Regular backups
4. ✅ Marketing & user acquisition
5. ✅ Feature improvements

**Omad!** 🚀
