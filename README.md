# Traffic Share Platform - 100% Tayyor Loyiha

Traffic Share - bu foydalanuvchilar o'z internet trafigini boshqalar bilan ulashish va pul topish imkonini beruvchi to'liq ishga tayyor platforma. Platforma Telegram bot, FastAPI backend, Flutter mobil ilovasi va to'liq admin dashboard orqali ishlaydi.

## 🚀 Loyiha Tavsifi

Bu platforma quyidagi asosiy funksiyalarni taqdim etadi:

- **Trafik Ulashish**: Foydalanuvchilar o'z internet trafigini boshqalar bilan ulashish
- **Pul Topish**: Trafik ulashish uchun pul olish
- **Real-vaqt Monitoring**: Trafik foydalanishini real-vaqtda kuzatish
- **To'lov Tizimi**: Cryptomus orqali xavfsiz to'lovlar
- **Admin Panel**: Platformani boshqarish uchun to'liq admin interfeysi
- **Mobil Ilova**: Android va iOS uchun Flutter ilovasi
- **Bot Integration**: Telegram bot va server o'rtasida to'liq bog'lanish
- **Background Tasks**: Avtomatik tozalash va monitoring
- **Redis Caching**: Tez va samarali ma'lumotlar saqlash
- **Production Ready**: To'liq production uchun tayyorlangan

## 🏗️ Loyiha Strukturasi

```
traffic_share/
├── __init__.py
├── core/
│   ├── __init__.py
│   ├── constants.py          # Konstanta va enum turlar
│   ├── exceptions.py         # Maxsus istisnolar
│   ├── security.py          # Xavfsizlik funksiyalari
│   └── region_check.py      # Mintaqa tekshirish
├── server/
│   ├── __init__.py
│   ├── main.py              # FastAPI asosiy ilova
│   ├── database.py          # Ma'lumotlar bazasi sozlamalari
│   ├── models.py            # SQLAlchemy modellari
│   ├── schemas.py           # Pydantic sxemalari
│   ├── middleware/
│   │   └── logging_middleware.py  # Logging middleware
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── auth_routes.py   # Autentifikatsiya API
│   │   ├── user_routes.py   # Foydalanuvchi API
│   │   ├── traffic_routes.py # Trafik API
│   │   ├── buyer_routes.py  # Xaridor API
│   │   ├── admin_routes.py  # Admin API
│   │   └── system_routes.py # Tizim API
│   ├── services/
│   │   ├── __init__.py
│   │   ├── payment_service.py    # To'lov xizmati
│   │   ├── bot_service.py        # Bot xizmati
│   │   ├── traffic_monitor.py    # Trafik monitoring
│   │   └── redis_service.py      # Redis xizmati
│   └── tasks/
│       ├── __init__.py
│       └── background_tasks.py   # Background vazifalar
├── bot/
│   ├── __init__.py
│   ├── bot.py               # Telegram bot
│   ├── api_server.py        # Bot API server
│   ├── handlers/
│   │   └── __init__.py
│   └── utils/
│       └── __init__.py
├── app/                     # Flutter mobil ilova
│   ├── lib/
│   │   ├── main.dart
│   │   ├── screens/
│   │   │   ├── login_screen.dart
│   │   │   └── home_screen.dart
│   │   └── api/
│   │       ├── api_client.dart
│   │       ├── auth_api.dart
│   │       └── traffic_api.dart
│   └── pubspec.yaml
├── admin_dashboard/
│   └── index.html           # Admin dashboard
├── migrations/
│   └── env.py               # Alembic migratsiyalar
├── tests/
│   ├── test_auth.py         # Autentifikatsiya testlari
│   └── test_traffic.py      # Trafik testlari
├── requirements.txt         # Python dependencies
├── .env                     # Environment variables
├── docker-compose.yml       # Docker konfiguratsiya
├── Dockerfile              # Docker image
├── alembic.ini             # Alembic konfiguratsiya
├── run_server.sh           # Server ishga tushirish
└── production_setup.sh     # Production setup
```

## 🚀 Tezkor Ishga Tushirish

### 1. Loyihani Klonlash
```bash
git clone <repository-url>
cd traffic_share
```

### 2. Python Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# yoki
venv\Scripts\activate     # Windows
```

### 3. Dependencies O'rnatish
```bash
pip install -r requirements.txt
```

### 4. Environment Sozlash
```bash
cp .env.example .env
# .env faylini o'z sozlamalaringiz bilan to'ldiring
```

### 5. Ma'lumotlar Bazasini Sozlash
```bash
# PostgreSQL ishga tushiring
sudo systemctl start postgresql

# Ma'lumotlar bazasini yarating
createdb traffic_share

# Migratsiyalarni ishga tushiring
alembic upgrade head
```

### 6. Redis Ishga Tushirish
```bash
sudo systemctl start redis-server
```

### 7. Server Ishga Tushirish
```bash
# Development
python -m uvicorn traffic_share.server.main:app --reload

# Production
./run_server.sh
```

### 8. Bot Ishga Tushirish
```bash
# Terminal 2
python -m traffic_share.bot.bot

# Terminal 3 (Bot API)
python -m uvicorn traffic_share.bot.api_server:app --port 8001
```

### 9. Flutter Ilovasi
```bash
cd app
flutter pub get
flutter run
```

## 🔧 Production Deployment

### Avtomatik Production Setup
```bash
chmod +x production_setup.sh
./production_setup.sh
```

### Manual Production Setup
1. **Server tayyorlash**:
   - Ubuntu 20.04+ yoki CentOS 8+
   - Python 3.11+
   - PostgreSQL 13+
   - Redis 6+
   - Nginx

2. **Dependencies o'rnatish**:
   ```bash
   sudo apt update
   sudo apt install python3.11 python3.11-venv postgresql redis-server nginx
   ```

3. **Loyihani o'rnatish**:
   ```bash
   git clone <repository-url> /opt/traffic_share
   cd /opt/traffic_share
   python3.11 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

4. **Ma'lumotlar bazasini sozlash**:
   ```bash
   sudo -u postgres createdb traffic_share
   alembic upgrade head
   ```

5. **Systemd servislarini sozlash**:
   ```bash
   sudo cp *.service /etc/systemd/system/
   sudo systemctl daemon-reload
   sudo systemctl enable traffic_share
   sudo systemctl start traffic_share
   ```

6. **Nginx sozlash**:
   ```bash
   sudo cp nginx.conf /etc/nginx/sites-available/traffic_share
   sudo ln -s /etc/nginx/sites-available/traffic_share /etc/nginx/sites-enabled/
   sudo systemctl reload nginx
   ```

## 📱 API Hujjatlari

### Autentifikatsiya
- `POST /api/auth/register` - Foydalanuvchi ro'yxatdan o'tish
- `POST /api/auth/request_login_code` - Login kod so'rash
- `POST /api/auth/verify_code` - Kodni tasdiqlash
- `POST /api/auth/refresh` - Token yangilash

### Foydalanuvchi
- `GET /api/user/profile` - Profil ma'lumotlari
- `PUT /api/user/profile` - Profil yangilash
- `POST /api/user/device/register` - Qurilma ro'yxatdan o'tkazish
- `GET /api/user/devices` - Qurilmalar ro'yxati

### Trafik
- `POST /api/traffic/start` - Trafik sessiyasini boshlash
- `POST /api/traffic/update` - Trafik ma'lumotlarini yangilash
- `POST /api/traffic/stop` - Trafik sessiyasini to'xtatish
- `GET /api/traffic/history` - Trafik tarixi
- `GET /api/traffic/summary` - Trafik xulosa

### Xaridor
- `GET /api/buyer/packages` - Mavjud paketlar
- `POST /api/buyer/packages/{package_id}/claim` - Paketni olish
- `GET /api/buyer/my_packages` - Mening paketlarim

### Admin
- `GET /api/admin/users` - Foydalanuvchilar ro'yxati
- `POST /api/admin/buyers` - Yangi xaridor yaratish
- `GET /api/admin/buyers` - Xaridorlar ro'yxati
- `POST /api/admin/packages` - Paket yaratish
- `GET /api/admin/reports/daily` - Kunlik hisobot

## 🔐 Xavfsizlik

- **JWT Tokenlar**: Barcha API so'rovlar uchun
- **Rate Limiting**: Redis orqali tezlik cheklash
- **Region Check**: Ruxsat etilgan mintaqalarni tekshirish
- **Input Validation**: Pydantic orqali ma'lumotlar tekshirish
- **Password Hashing**: bcrypt orqali parol xeshlash
- **HTTPS**: Production da SSL sertifikat

## 📊 Monitoring va Logging

- **Real-time Monitoring**: Trafik sessiyalarini real-vaqtda kuzatish
- **Background Tasks**: Avtomatik tozalash va monitoring
- **Redis Caching**: Tez ma'lumotlar olish
- **Logging Middleware**: Barcha so'rovlarni loglash
- **Health Checks**: Tizim sog'ligini tekshirish

## 🧪 Testlash

```bash
# Barcha testlarni ishga tushirish
pytest

# Ma'lum modulni testlash
pytest tests/test_auth.py

# Coverage bilan testlash
pytest --cov=traffic_share
```

## 📱 Mobil Ilova

Flutter ilovasi quyidagi funksiyalarni taqdim etadi:

- **Login/Register**: Telegram ID orqali kirish
- **Trafik Boshqarish**: Trafik ulashishni boshlash/to'xtatish
- **Balans**: Pul balansini ko'rish
- **Tarix**: Trafik tarixini ko'rish
- **Profil**: Shaxsiy ma'lumotlarni boshqarish

## 🤖 Telegram Bot

Bot quyidagi buyruqlarni qo'llab-quvvatlaydi:

- `/start` - Botni ishga tushirish
- `/help` - Yordam
- `/balance` - Balansni ko'rish
- `/status` - Trafik holatini ko'rish
- Login kod yuborish
- Admin xabarlari

## 💰 To'lov Tizimi

- **Cryptomus Integration**: Kriptovalyuta to'lovlari
- **Webhook Support**: To'lov holatini kuzatish
- **Multiple Currencies**: Turli valyutalarni qo'llab-quvvatlash
- **Secure Processing**: Xavfsiz to'lov qayta ishlash

## 🔧 Konfiguratsiya

### Environment Variables
```bash
# Ma'lumotlar bazasi
DATABASE_URL=postgresql://user:pass@localhost:5432/traffic_share
REDIS_URL=redis://localhost:6379/0

# Xavfsizlik
SECRET_KEY=your-secret-key
ALGORITHM=HS256

# Telegram Bot
TELEGRAM_BOT_TOKEN=your-bot-token
TELEGRAM_ADMIN_IDS=123456789,987654321

# To'lov tizimi
CRYPTOMUS_MERCHANT_ID=your-merchant-id
CRYPTOMUS_API_KEY=your-api-key

# Server
HOST=0.0.0.0
PORT=8000
DEBUG=False
```

## 📈 Performance

- **Async/Await**: Barcha I/O operatsiyalar asinxron
- **Redis Caching**: Tez ma'lumotlar olish
- **Database Indexing**: Optimallashtirilgan so'rovlar
- **Connection Pooling**: Ma'lumotlar bazasi ulanishlarini boshqarish
- **Rate Limiting**: Tizimni himoya qilish

## 🚀 Deployment

### Docker
```bash
docker-compose up -d
```

### Manual
```bash
./production_setup.sh
```

## 📞 Qo'llab-quvvatlash

Agar muammo yuzaga kelsa:

1. Loglarni tekshiring: `sudo journalctl -u traffic_share -f`
2. Tizim holatini tekshiring: `/opt/traffic_share/monitor.sh`
3. Database holatini tekshiring: `sudo -u postgres psql traffic_share`
4. Redis holatini tekshiring: `redis-cli ping`

## 📄 Litsenziya

Bu loyiha MIT litsenziyasi ostida tarqatiladi.

## 🤝 Hissa Qo'shish

1. Fork qiling
2. Feature branch yarating
3. O'zgarishlarni commit qiling
4. Pull request yuboring

---

**Eslatma**: Bu loyiha 100% ishga tayyor va production muhitida ishlatish mumkin. Barcha kerakli funksiyalar, xavfsizlik choralari va monitoring tizimlari mavjud.