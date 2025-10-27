# 🚀 Traffic Share - Tez Boshlash

## 1-Qadam: Environment Sozlash

```bash
cp .env.example .env
```

`.env` faylda minimal sozlamalar:

```env
SECRET_KEY=your-secret-key-min-32-chars-xxxxxxxxxx
DATABASE_URL=postgresql://user:pass@localhost:5432/traffic_share
REDIS_URL=redis://localhost:6379/0
TELEGRAM_BOT_TOKEN=your-bot-token
TELEGRAM_ADMIN_IDS=your-telegram-id
CRYPTOMUS_API_KEY=your-api-key
CRYPTOMUS_MERCHANT_ID=your-merchant-id
```

## 2-Qadam: Dependencies

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## 3-Qadam: Database

PostgreSQL yarating:
```bash
sudo -u postgres psql
CREATE DATABASE traffic_share;
CREATE USER traffic_user WITH PASSWORD 'password';
GRANT ALL PRIVILEGES ON DATABASE traffic_share TO traffic_user;
\q
```

Database initsializatsiya:
```bash
python traffic_share/scripts/init_db.py
```

## 4-Qadam: Ishga Tushirish

```bash
./run_server.sh
```

## 5-Qadam: Test

Brauzerda: http://localhost:8000/docs

## Docker (Eng Oson)

```bash
cp .env.example .env
# .env sozlang
docker-compose up -d
```

---

**Tayyor! API ishlamoqda: http://localhost:8000** 🎉
