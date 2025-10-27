# 🚀 TRAFFIC SHARE - BOSHLASH UCHUN QO'LLANMA

**VPS IP:** 185.139.230.196  
**Ubuntu:** 24.04 LTS

---

## ⚡ TEZ BOSHLASH (5 QADAM)

### 📱 Agar siz FOYDALANUVCHI bo'lsangiz:

1. APK ni yuklab oling
2. O'rnating
3. Telegram ID ni kiriting
4. Kodni kiriting
5. Traffic ulashing va pul ishlang!

### 💻 Agar siz DEVELOPER bo'lsangiz:

Quyidagi qadamlarni bajaring ↓

---

## 🎯 DEPLOYMENT JARAYONI

## QADAM 1️⃣: VPS GA ULANISH

```bash
ssh ubuntu@185.139.230.196
# yoki
ssh root@185.139.230.196
```

---

## QADAM 2️⃣: POSTGRESQL VA REDIS O'RNATISH

### PostgreSQL

```bash
# O'rnatish
sudo apt update
sudo apt install postgresql postgresql-contrib -y

# Database yaratish
sudo -u postgres psql << EOF
CREATE DATABASE traffic_share;
CREATE USER traffic_user WITH PASSWORD 'QuvvatliParol_2024!';
GRANT ALL PRIVILEGES ON DATABASE traffic_share TO traffic_user;
ALTER DATABASE traffic_share OWNER TO traffic_user;
\c traffic_share
GRANT ALL ON SCHEMA public TO traffic_user;
EOF

# Test
psql -h localhost -U traffic_user -d traffic_share -c "SELECT 1;"
```

### Redis

```bash
# O'rnatish
sudo apt install redis-server -y

# Start va enable
sudo systemctl start redis-server
sudo systemctl enable redis-server

# Test
redis-cli ping
# Javob: PONG
```

**Batafsil:** `INSTALL_POSTGRESQL_REDIS.md`

---

## QADAM 3️⃣: LOYIHANI VPS GA KO'CHIRISH

### Variant A: Git (Tavsiya etiladi)

```bash
cd /opt
sudo git clone https://github.com/your-username/traffic-share.git traffic_share
sudo chown -R ubuntu:ubuntu traffic_share
```

### Variant B: SCP (Local kompyuterdan)

```bash
# Local terminalda
scp -r /workspace ubuntu@185.139.230.196:/tmp/traffic_share

# VPS da
sudo mv /tmp/traffic_share /opt/
sudo chown -R ubuntu:ubuntu /opt/traffic_share
```

### Variant C: Manual

```bash
# VPS da
sudo mkdir -p /opt/traffic_share
sudo chown -R ubuntu:ubuntu /opt/traffic_share

# Local dan fayllarni ko'chirish
# yoki git clone qilish
```

---

## QADAM 4️⃣: BACKEND DEPLOY (AVTOMATIK)

```bash
cd /opt/traffic_share

# 1. Script ni executable qilish
chmod +x BUILD_COMPLETE.sh

# 2. .env faylni sozlash
cp .env.example .env
nano .env
```

`.env` da to'ldiring:

```env
DATABASE_URL=postgresql://traffic_user:QuvvatliParol_2024!@localhost:5432/traffic_share
REDIS_URL=redis://localhost:6379/0
SECRET_KEY=your-very-long-secret-key-change-this-min-32-chars
TELEGRAM_BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz
TELEGRAM_ADMIN_IDS=123456789
CRYPTOMUS_API_KEY=your-api-key
CRYPTOMUS_MERCHANT_ID=your-merchant-id
```

```bash
# 3. Build va deploy
./BUILD_COMPLETE.sh
```

Bu script avtomatik:
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

## QADAM 5️⃣: FLUTTER APK BUILD (AVTOMATIK)

### Local Kompyuterda

```bash
cd /workspace/app

# 1. Script ni executable qilish
chmod +x build_apk.sh

# 2. Release APK build
./build_apk.sh release
```

Bu script avtomatik:
- ✅ Flutter va Java tekshiradi
- ✅ Clean build qiladi
- ✅ Dependencies fetch qiladi
- ✅ Code analyze qiladi
- ✅ APK build qiladi
- ✅ Signature verify qiladi
- ✅ APK info ko'rsatadi

### Natija

```
✅ APK build successful! 🎉

APK location:
  build/app/outputs/flutter-apk/app-release.apk

File size:
  ~25 MB
```

### APK ni Tarqatish

```bash
# VPS ga upload
scp build/app/outputs/flutter-apk/app-release.apk \
    ubuntu@185.139.230.196:/var/www/downloads/

# Nginx orqali download
# http://185.139.230.196/downloads/app-release.apk
```

---

## ✅ TEST QILISH

### Backend Test

```bash
# Health check
curl http://185.139.230.196/api/system/health

# Javob:
# {"status":"ok","timestamp":"...","version":"1.0.0"}

# API documentation (browser)
# http://185.139.230.196/docs
```

### Services Test

```bash
# VPS da
sudo systemctl status traffic-share-api
sudo systemctl status traffic-share-bot
sudo systemctl status traffic-share-tasks

# Logs
sudo journalctl -u traffic-share-api -n 20
```

### Database Test

```bash
# Connection
psql -h localhost -U traffic_user -d traffic_share

# Tables
\dt

# Users count
SELECT COUNT(*) FROM users;

\q
```

### Flutter App Test

1. APK ni telefonga o'rnating
2. Ilovani oching
3. Telegram ID kiriting
4. Telegram botdan kod oling
5. Kodni kiriting
6. Start sharing bosing
7. Statistikani ko'ring

---

## 🔧 KONFIGURATSIYA

### Telegram Bot Setup

1. Telegram da @BotFather ni oching
2. `/newbot` komandasi
3. Bot nomi: Traffic Share Bot
4. Username: @trafficshare_bot
5. Token oling va `.env` ga qo'ying

### Admin ID Aniqlash

1. Telegram da @userinfobot ni oching
2. `/start` bosing
3. ID ni ko'ring
4. `.env` ga qo'ying: `TELEGRAM_ADMIN_IDS=123456789`

### Cryptomus Setup

1. https://cryptomus.com ga kiring
2. Ro'yxatdan o'ting
3. Merchant yarating
4. API settings dan key oling
5. `.env` ga qo'ying

---

## 📊 MONITORING

### Logs Ko'rish

```bash
# Real-time API logs
sudo journalctl -u traffic-share-api -f

# Application logs
tail -f /opt/traffic_share/logs/traffic_share.log

# Nginx logs
tail -f /var/log/nginx/access.log
```

### Metrics

```bash
# System info
htop

# Disk
df -h

# Network
netstat -tulpn | grep :8000

# PostgreSQL
sudo -u postgres psql -c "SELECT count(*) FROM pg_stat_activity;"

# Redis
redis-cli info
```

### Health Checks

API health endpoint:
```bash
curl http://185.139.230.196/api/system/health
```

Javob:
```json
{
  "status": "ok",
  "timestamp": "2025-10-27T...",
  "version": "1.0.0"
}
```

---

## 🚨 TROUBLESHOOTING

### Backend ishlamayapti

```bash
# Service status
sudo systemctl status traffic-share-api

# Logs
sudo journalctl -u traffic-share-api -n 50

# Restart
sudo systemctl restart traffic-share-api

# Test manually
cd /opt/traffic_share
source venv/bin/activate
uvicorn traffic_share.server.main:app --host 0.0.0.0 --port 8000
```

### Database error

```bash
# PostgreSQL ishlab turibdimi?
sudo systemctl status postgresql

# Connection test
psql -h localhost -U traffic_user -d traffic_share

# .env tekshirish
cat .env | grep DATABASE_URL
```

### APK build failed

```bash
# Clean va rebuild
cd /workspace/app
flutter clean
flutter pub get
flutter build apk --release
```

### Network permissions

`android/app/src/main/AndroidManifest.xml`:

```xml
<uses-permission android:name="android.permission.INTERNET" />
<uses-permission android:name="android.permission.ACCESS_NETWORK_STATE" />

<application
    android:usesCleartextTraffic="true">
```

---

## 🔐 XAVFSIZLIK

### Production Checklist

- [ ] `.env` SECRET_KEY o'zgartirildi
- [ ] Database parol quvvatli
- [ ] Firewall sozlandi
- [ ] SSH port o'zgartirildi (optional)
- [ ] SSL sertifikat o'rnatildi
- [ ] Admin Telegram ID to'g'ri
- [ ] Cryptomus production mode
- [ ] Logs rotation sozlandi
- [ ] Backup strategy
- [ ] Monitoring setup

### SSL/HTTPS Setup

```bash
# Domain bilan (recommended)
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d yourdomain.com

# Auto renewal
sudo certbot renew --dry-run
```

---

## 📋 BUYRUQLAR RO'YXATI

### Service Commands

```bash
# Start
sudo systemctl start traffic-share-api

# Stop  
sudo systemctl stop traffic-share-api

# Restart
sudo systemctl restart traffic-share-api

# Status
sudo systemctl status traffic-share-api

# Logs
sudo journalctl -u traffic-share-api -f
```

### Application Commands

```bash
# Update code
cd /opt/traffic_share
git pull
source venv/bin/activate
pip install -r requirements.txt
sudo systemctl restart traffic-share-api

# Database backup
python traffic_share/scripts/backup_task.py

# Clear old data
python traffic_share/scripts/clear_sessions.py

# Export stats
python traffic_share/scripts/export_stats.py

# Rotate buyer token
python traffic_share/scripts/rotate_tokens.py <buyer_id>
```

---

## 📚 BARCHA FAYLLAR RO'YXATI

### Backend Python (53 fayl)
```
traffic_share/
├── core/ (4)
├── server/ (9)
│   ├── services/ (7)
│   ├── routes/ (7)
│   └── tasks/ (4)
├── bot/ (6)
├── scripts/ (5)
└── migrations/ (2)
```

### Frontend Dart (18 fayl)
```
app/lib/
├── api/ (4)
├── models/ (2)
├── providers/ (3)
├── screens/ (3)
├── widgets/ (3)
├── utils/ (2)
└── main.dart (1)
```

### Dokumentatsiya (12 fayl)
```
├── COMPLETE_README.md          (TO'LIQ qo'llanma)
├── START_HERE.md               (Boshlash)
├── INSTALL_POSTGRESQL_REDIS.md (Database)
├── VPS_DEPLOYMENT.md           (VPS deploy)
├── BUILD_INSTRUCTIONS.md       (APK build)
├── PRODUCTION_READY.md         (Production)
├── SETUP_GUIDE.md              (Setup)
├── QUICK_START.md              (Tez boshlash)
├── PROJECT_README.md           (Backend)
├── FINAL_SUMMARY.md            (Xulosa)
├── FINAL_COMPLETE.txt          (Hisobot)
└── app/README.md               (Flutter app)
```

### Scripts (2 + 5 utility)
```
├── BUILD_COMPLETE.sh           (Backend deploy)
├── build_apk.sh                (APK build)
├── run_server.sh               (Simple start)
└── traffic_share/scripts/      (5 utility scripts)
```

---

## 🎯 UMUMIY JARAYON

```
1. VPS Tayyorlash
   ├─ SSH ulanish
   ├─ PostgreSQL o'rnatish
   └─ Redis o'rnatish
   
2. Backend Deploy
   ├─ Loyihani ko'chirish
   ├─ .env sozlash
   ├─ BUILD_COMPLETE.sh ishga tushirish
   └─ Test qilish
   
3. Flutter APK Build
   ├─ Dependencies o'rnatish
   ├─ build_apk.sh ishga tushirish
   └─ APK olish
   
4. Testing
   ├─ Backend API test
   ├─ Flutter app test
   └─ Integration test
   
5. Launch
   ├─ SSL sozlash (optional)
   ├─ Domain sozlash (optional)
   ├─ Monitoring setup
   └─ Users ga APK tarqatish
```

---

## 🆘 YORDAM

### Qo'llanmalar

| Fayl | Maqsad |
|------|---------|
| `START_HERE.md` | Bu fayl - boshlash uchun |
| `COMPLETE_README.md` | To'liq texnik qo'llanma |
| `INSTALL_POSTGRESQL_REDIS.md` | Database o'rnatish |
| `VPS_DEPLOYMENT.md` | VPS sozlash |
| `BUILD_INSTRUCTIONS.md` | APK build |

### API Documentation

Browser da oching:
```
http://185.139.230.196/docs
```

### Scripts

```bash
# Backend deploy
./BUILD_COMPLETE.sh

# APK build
./build_apk.sh release
```

---

## ✅ YAKUNIY TEKSHIRUV

Deploy qilgandan keyin:

```bash
# 1. Health check
curl http://185.139.230.196/api/system/health

# 2. Services
sudo systemctl status traffic-share-api

# 3. Database
psql -h localhost -U traffic_user -d traffic_share -c "SELECT COUNT(*) FROM users;"

# 4. Redis
redis-cli ping

# 5. Logs
tail -f /opt/traffic_share/logs/traffic_share.log
```

Hammasi OK bo'lsa:

✅ Backend ishlayapti: http://185.139.230.196
✅ API docs: http://185.139.230.196/docs
✅ APK tayyor: build/app/outputs/flutter-apk/app-release.apk

---

## 🎉 TABRIKLAYMIZ!

Loyihangiz tayyor va ishlamoqda!

**Keyingi qadamlar:**
1. Foydalanuvchilarga APK tarqating
2. Telegram botni sozlang
3. Cryptomus to'lovlarni test qiling
4. Monitoring sozlang
5. Marketing boshlang!

**Omad!** 🚀

---

**Savollar?** Dokumentatsiyani o'qing yoki loglarni tekshiring.
