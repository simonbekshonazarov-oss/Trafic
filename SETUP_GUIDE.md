# Traffic Share - O'rnatish va Ishga Tushirish Qo'llanmasi

## 📋 Loyiha Haqida

Traffic Share platformasining to'liq backend tizimi muvaffaqiyatli qurildi. Bu qo'llanma sizga tizimni o'rnatish va ishga tushirishda yordam beradi.

## ✅ Yaratilgan Komponentlar

### Backend (60+ API endpoints)
- Authentication & Authorization
- User Management
- Traffic Session Tracking
- Payment Processing (Cryptomus)
- Buyer Package Allocation
- Admin Panel
- Background Tasks

### Database (14 tables)
- PostgreSQL schema
- Migrations support
- Indexes & optimizations

### Telegram Bot
- User commands
- Admin commands  
- Notification system

## 🔧 Tizim Talablari

- Python 3.11 yoki yuqori
- PostgreSQL 15+
- Redis 7+
- Telegram Bot Token
- Cryptomus API credentials (to'lovlar uchun)

## 📦 O'rnatish Bosqichlari

### 1. Virtual Environment Yaratish

```bash
cd /workspace
python -m venv venv
source venv/bin/activate  # Linux/Mac
# yoki
venv\Scripts\activate  # Windows
```

### 2. Dependencies O'rnatish

```bash
pip install -r requirements.txt
```

### 3. PostgreSQL Database Yaratish

```bash
# PostgreSQL ga ulanish
sudo -u postgres psql

# Database va user yaratish
CREATE DATABASE traffic_share;
CREATE USER traffic_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE traffic_share TO traffic_user;
\q
```

### 4. Redis O'rnatish (Ubuntu)

```bash
sudo apt update
sudo apt install redis-server
sudo systemctl start redis
sudo systemctl enable redis
```

### 5. Environment Configuration

```bash
cp .env.example .env
```

`.env` faylni tahrirlang:

```env
# Database
DATABASE_URL=postgresql://traffic_user:your_password@localhost:5432/traffic_share

# Redis
REDIS_URL=redis://localhost:6379/0

# Security
SECRET_KEY=your-very-long-secret-key-minimum-32-characters

# Telegram Bot
TELEGRAM_BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz
TELEGRAM_ADMIN_IDS=123456789,987654321

# Cryptomus
CRYPTOMUS_API_KEY=your-api-key
CRYPTOMUS_MERCHANT_ID=your-merchant-id
```

### 6. Database Initsializatsiya

```bash
python traffic_share/scripts/init_db.py
```

### 7. Test Ma'lumotlar (ixtiyoriy)

```bash
python traffic_share/scripts/seed_data.py
```

**Muhim:** Bu script buyer token yaratadi. Tokenni saqlang!

### 8. Server Ishga Tushirish

```bash
./run_server.sh
```

Yoki qo'lda:

```bash
uvicorn traffic_share.server.main:app --host 0.0.0.0 --port 8000 --reload
```

### 9. Telegram Bot Ishga Tushirish

Yangi terminal oynasida:

```bash
source venv/bin/activate
python -m traffic_share.bot.bot
```

### 10. Background Tasks (ixtiyoriy)

Yangi terminal oynasida:

```bash
source venv/bin/activate
python -m traffic_share.server.tasks.cleanup_task
```

## 🐳 Docker bilan Ishga Tushirish

Eng oson usul:

```bash
# .env faylni sozlang
cp .env.example .env
# .env ni tahrirlang

# Docker compose bilan ishga tushirish
docker-compose up -d

# Loglarni ko'rish
docker-compose logs -f api

# To'xtatish
docker-compose down
```

## 🧪 Test Qilish

### 1. Health Check

```bash
curl http://localhost:8000/api/system/health
```

Javob:
```json
{
  "status": "ok",
  "timestamp": "2025-10-27T...",
  "version": "1.0.0"
}
```

### 2. API Documentation

Brauzerda oching:
```
http://localhost:8000/docs
```

Swagger UI orqali barcha endpointlarni test qilishingiz mumkin.

### 3. Register & Login Test

```bash
# 1. Register
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "telegram_id": 123456789,
    "username": "testuser"
  }'

# 2. Request login code
curl -X POST http://localhost:8000/api/auth/request_login_code \
  -H "Content-Type: application/json" \
  -d '{"telegram_id": 123456789}'

# 3. Verify code (telegram botdan kelgan kod)
curl -X POST http://localhost:8000/api/auth/verify_code \
  -H "Content-Type: application/json" \
  -d '{
    "telegram_id": 123456789,
    "code": "123456"
  }'
```

## 📱 Telegram Bot Setup

### 1. Bot Yaratish

1. Telegram da @BotFather ni oching
2. `/newbot` komandasi yuboring
3. Bot nomini kiriting
4. Username kiriting (masalan: @trafficshare_bot)
5. Token oling va `.env` ga qo'ying

### 2. Admin ID Aniqlash

1. Telegram da @userinfobot ni oching
2. `/start` bosing
3. Sizning ID ingizni ko'rsatadi
4. ID ni `.env` dagi `TELEGRAM_ADMIN_IDS` ga qo'ying

## 💳 Cryptomus Setup

### 1. Account Yaratish

1. https://cryptomus.com ga kiring
2. Ro'yxatdan o'ting
3. Merchant yarating
4. API keys olish

### 2. Webhook Sozlash

1. Cryptomus dashboardda webhook URL ni sozlang:
   ```
   https://your-domain.com/api/webhook/cryptomus
   ```

2. Webhook secretni `.env` ga qo'ying

## 🚀 Production Deployment

### Nginx Configuration

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

### Systemd Service

`/etc/systemd/system/traffic-share.service`:

```ini
[Unit]
Description=Traffic Share API
After=network.target postgresql.service redis.service

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/workspace
Environment="PATH=/workspace/venv/bin"
ExecStart=/workspace/venv/bin/uvicorn traffic_share.server.main:app --host 0.0.0.0 --port 8000 --workers 4
Restart=always

[Install]
WantedBy=multi-user.target
```

Ishga tushirish:
```bash
sudo systemctl daemon-reload
sudo systemctl enable traffic-share
sudo systemctl start traffic-share
```

## 📊 Database Backup

```bash
# Manual backup
python traffic_share/scripts/backup_task.py

# Yoki pg_dump
pg_dump -U traffic_user -d traffic_share -F c -f backup.dump
```

## 🔧 Utility Scripts

### Buyer Token Rotation
```bash
python traffic_share/scripts/rotate_tokens.py <buyer_id>
```

### Session Cleanup
```bash
python traffic_share/scripts/clear_sessions.py
```

### Export Statistics
```bash
python traffic_share/scripts/export_stats.py
```

## 🐛 Debugging

### Loglarni Ko'rish

```bash
# Server logs
tail -f logs/traffic_share.log

# Docker logs
docker-compose logs -f api
```

### Database Tekshirish

```bash
psql -U traffic_user -d traffic_share

# Tables
\dt

# User count
SELECT COUNT(*) FROM users;

# Active sessions
SELECT COUNT(*) FROM traffic_sessions WHERE status = 'active';
```

### Redis Tekshirish

```bash
redis-cli

# Test
PING

# Keys
KEYS traffic_share:*
```

## ⚠️ Common Issues

### Database Connection Error

**Problem:** `psycopg2.OperationalError: could not connect`

**Solution:**
1. PostgreSQL ishlab turganini tekshiring: `sudo systemctl status postgresql`
2. Database va user mavjudligini tekshiring
3. `.env` dagi `DATABASE_URL` to'g'riligini tekshiring

### Redis Connection Error

**Problem:** `redis.exceptions.ConnectionError`

**Solution:**
1. Redis ishlab turganini tekshiring: `sudo systemctl status redis`
2. `.env` dagi `REDIS_URL` to'g'riligini tekshiring

### Bot Token Invalid

**Problem:** `telegram.error.InvalidToken`

**Solution:**
1. Bot token to'g'riligini tekshiring
2. @BotFather dan yangi token oling

## 📞 Yordam

Qo'shimcha savollarga javob:

1. **API documentation:** http://localhost:8000/docs
2. **Health check:** http://localhost:8000/api/system/health
3. **Logs:** `logs/traffic_share.log`

## ✅ Yakuniy Tekshiruv

Hammasi ishlayotganini tekshirish:

```bash
# 1. Server ishlayapti
curl http://localhost:8000/api/system/health

# 2. Database ulanish
psql -U traffic_user -d traffic_share -c "SELECT 1;"

# 3. Redis ulanish
redis-cli ping

# 4. Bot ishlayapti (telegram botga /start yuboring)
```

---

**Tabriklaymiz! Traffic Share backend tizimi tayyor! 🎉**
