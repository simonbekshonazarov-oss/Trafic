# 🗄️ PostgreSQL va Redis O'rnatish (Ubuntu 24.04)

VPS: **185.139.230.196**

## 📦 1. PostgreSQL O'rnatish

### 1.1. Repository Yangilash

```bash
sudo apt update
sudo apt upgrade -y
```

### 1.2. PostgreSQL O'rnatish

```bash
# PostgreSQL 15 o'rnatish
sudo apt install postgresql postgresql-contrib -y

# Versiyani tekshirish
psql --version
```

### 1.3. PostgreSQL Serviceni Ishga Tushirish

```bash
# Start
sudo systemctl start postgresql

# Enable (avtomatik ishga tushish)
sudo systemctl enable postgresql

# Status tekshirish
sudo systemctl status postgresql
```

### 1.4. PostgreSQL Sozlash

```bash
# PostgreSQL user sifatida kirish
sudo -u postgres psql

# Yoki to'g'ridan-to'g'ri:
sudo -i -u postgres
psql
```

### 1.5. Database va User Yaratish

PostgreSQL shell ichida:

```sql
-- Database yaratish
CREATE DATABASE traffic_share;

-- User yaratish
CREATE USER traffic_user WITH PASSWORD 'QuvvatliParol_2024!';

-- Barcha huquqlarni berish
GRANT ALL PRIVILEGES ON DATABASE traffic_share TO traffic_user;

-- Database uchun owner qilish
ALTER DATABASE traffic_share OWNER TO traffic_user;

-- Public schema huquqlari
\c traffic_share
GRANT ALL ON SCHEMA public TO traffic_user;

-- Chiqish
\q
```

### 1.6. External Connection Sozlash

PostgreSQL default faqat localhost dan ulanishga ruxsat beradi.

**postgresql.conf sozlash:**

```bash
sudo nano /etc/postgresql/15/main/postgresql.conf
```

Quyidagi qatorni toping va o'zgartiring:

```
# O'zgartirish:
listen_addresses = 'localhost'

# Shu qilib o'zgartiring (barcha IP dan ruxsat):
listen_addresses = '*'
```

**pg_hba.conf sozlash:**

```bash
sudo nano /etc/postgresql/15/main/pg_hba.conf
```

Faylning oxiriga qo'shing:

```
# IPv4 local connections (traffic_share uchun)
host    traffic_share    traffic_user    127.0.0.1/32    md5
host    traffic_share    traffic_user    localhost       md5
```

### 1.7. PostgreSQL Restart

```bash
sudo systemctl restart postgresql
```

### 1.8. Ulanishni Test Qilish

```bash
# Local connection
psql -h localhost -U traffic_user -d traffic_share

# Password kiritish (QuvvatliParol_2024!)
# Agar kirishingiz bo'lsa - SUCCESS!

# Test query
SELECT version();

# Chiqish
\q
```

---

## 🔴 2. Redis O'rnatish

### 2.1. Redis O'rnatish

```bash
# Redis server o'rnatish
sudo apt install redis-server -y

# Versiyani tekshirish
redis-server --version
```

### 2.2. Redis Konfiguratsiya

```bash
sudo nano /etc/redis/redis.conf
```

Kerakli o'zgarishlar:

```conf
# Supervised mode
supervised systemd

# Memory policy (optional)
maxmemory 256mb
maxmemory-policy allkeys-lru

# Password (optional, tavsiya etiladi)
# requirepass YourStrongPassword123

# Save settings (persistence)
save 900 1
save 300 10
save 60 10000
```

### 2.3. Redis Serviceni Ishga Tushirish

```bash
# Start
sudo systemctl start redis-server

# Enable
sudo systemctl enable redis-server

# Status
sudo systemctl status redis-server
```

### 2.4. Redis Test

```bash
# Redis CLI ga kirish
redis-cli

# Test ping
127.0.0.1:6379> ping
# Javob: PONG

# Set/Get test
127.0.0.1:6379> set test "hello"
127.0.0.1:6379> get test
# Javob: "hello"

# Chiqish
127.0.0.1:6379> exit
```

---

## 🔧 3. .env Fayl Sozlash

`.env` faylda quyidagi ma'lumotlarni to'ldiring:

```bash
cd /opt/traffic_share
nano .env
```

```.env
# Database (Local PostgreSQL)
DATABASE_URL=postgresql://traffic_user:QuvvatliParol_2024!@localhost:5432/traffic_share
DB_POOL_SIZE=20
DB_MAX_OVERFLOW=10
DB_ECHO=False

# Redis (Local)
REDIS_URL=redis://localhost:6379/0
REDIS_KEY_PREFIX=traffic_share:

# Security
SECRET_KEY=your-very-strong-secret-key-minimum-32-characters-long-change-this-immediately
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
REFRESH_TOKEN_EXPIRE_DAYS=30

# Server
HOST=0.0.0.0
PORT=8000
WORKERS=4

# Telegram Bot
TELEGRAM_BOT_TOKEN=your-bot-token-from-botfather
TELEGRAM_ADMIN_IDS=your-telegram-id-numbers-comma-separated
TELEGRAM_ADMIN_CHANNEL=

# Cryptomus Payment
CRYPTOMUS_API_KEY=your-cryptomus-api-key
CRYPTOMUS_MERCHANT_ID=your-cryptomus-merchant-id
CRYPTOMUS_API_URL=https://api.cryptomus.com/v1
CRYPTOMUS_WEBHOOK_SECRET=your-webhook-secret

# Other settings...
DEBUG=False
LOG_LEVEL=INFO
CORS_ORIGINS=*
```

---

## ✅ 4. Database Initialization

```bash
cd /opt/traffic_share
source venv/bin/activate

# Database tables yaratish
python traffic_share/scripts/init_db.py

# Success bo'lishi kerak:
# "Database initialized successfully!"
```

---

## 🧪 5. Test Qilish

### PostgreSQL Test

```bash
# Connection string test
python3 << EOF
import psycopg2
try:
    conn = psycopg2.connect(
        "postgresql://traffic_user:QuvvatliParol_2024!@localhost:5432/traffic_share"
    )
    print("✅ PostgreSQL connection: SUCCESS")
    conn.close()
except Exception as e:
    print(f"❌ PostgreSQL connection: FAILED - {e}")
EOF
```

### Redis Test

```bash
# Redis test
python3 << EOF
import redis
try:
    r = redis.Redis(host='localhost', port=6379, db=0)
    r.ping()
    print("✅ Redis connection: SUCCESS")
except Exception as e:
    print(f"❌ Redis connection: FAILED - {e}")
EOF
```

### Full Stack Test

```bash
# Virtual environment
source venv/bin/activate

# Test imports
python3 << EOF
from traffic_share.server.database import engine
from traffic_share.server.config import settings

print("✅ Imports: SUCCESS")
print(f"Database URL: {settings.DATABASE_URL}")
print(f"Redis URL: {settings.REDIS_URL}")

# Test DB connection
try:
    conn = engine.connect()
    conn.close()
    print("✅ Database connection: SUCCESS")
except Exception as e:
    print(f"❌ Database connection: FAILED - {e}")
EOF
```

---

## 🔐 6. Security Best Practices

### PostgreSQL

```bash
# PostgreSQL user parolini o'zgartirish
sudo -u postgres psql
ALTER USER traffic_user WITH PASSWORD 'YangiQuvvatliParol!';
\q
```

### Redis

```bash
# Redis passwordni sozlash
sudo nano /etc/redis/redis.conf

# Uncomment va o'zgartiring:
requirepass YourRedisPassword123

# Restart
sudo systemctl restart redis-server

# Test with password
redis-cli
AUTH YourRedisPassword123
PING
```

Agar Redis password sozlagan bo'lsangiz, `.env` da:

```env
REDIS_URL=redis://:YourRedisPassword123@localhost:6379/0
```

---

## 📊 7. Monitoring

### PostgreSQL Status

```bash
# Service status
sudo systemctl status postgresql

# Connections
sudo -u postgres psql -c "SELECT count(*) FROM pg_stat_activity;"

# Database size
sudo -u postgres psql -c "SELECT pg_size_pretty(pg_database_size('traffic_share'));"
```

### Redis Status

```bash
# Service status
sudo systemctl status redis-server

# Info
redis-cli info

# Memory usage
redis-cli info memory
```

---

## 🔄 8. Backup

### PostgreSQL Backup

```bash
# Manual backup
sudo -u postgres pg_dump traffic_share > backup_$(date +%Y%m%d).sql

# Restore
sudo -u postgres psql traffic_share < backup_20241027.sql
```

### Redis Backup

```bash
# Redis automatically saves to /var/lib/redis/dump.rdb
# Manual save:
redis-cli SAVE

# Copy backup
sudo cp /var/lib/redis/dump.rdb ~/redis_backup_$(date +%Y%m%d).rdb
```

---

## 🐛 Troubleshooting

### PostgreSQL Issues

**Problem**: Connection refused

```bash
# Check service
sudo systemctl status postgresql

# Check port
sudo netstat -plunt | grep 5432

# Check logs
sudo tail -f /var/log/postgresql/postgresql-15-main.log
```

**Problem**: Authentication failed

```bash
# Check pg_hba.conf
sudo nano /etc/postgresql/15/main/pg_hba.conf

# Restart
sudo systemctl restart postgresql
```

### Redis Issues

**Problem**: Connection refused

```bash
# Check service
sudo systemctl status redis-server

# Check port
sudo netstat -plunt | grep 6379

# Check logs
sudo tail -f /var/log/redis/redis-server.log
```

---

## ✅ Final Checklist

- [ ] PostgreSQL o'rnatildi
- [ ] Database `traffic_share` yaratildi
- [ ] User `traffic_user` yaratildi
- [ ] PostgreSQL service ishlab turibdi
- [ ] Connection test o'tkazildi
- [ ] Redis o'rnatildi
- [ ] Redis service ishlab turibdi
- [ ] Redis test o'tkazildi
- [ ] `.env` fayl sozlandi
- [ ] Database tables yaratildi (`init_db.py`)
- [ ] Full stack test o'tkazildi

---

**Tayyor!** PostgreSQL va Redis to'liq sozlandi va ishga tayyor! ✅
