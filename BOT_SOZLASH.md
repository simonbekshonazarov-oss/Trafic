# 🤖 TELEGRAM BOT SOZLASH VA TUZATISH

## ✅ MUAMMO TUZATILDI

### Asosiy o'zgarishlar:

1. **Bot instance tuzatildi** - Har safar yangi bot yaratish o'rniga, global bot instance ishlatiladi
2. **send_login_code tuzatildi** - Endi to'g'ri ishlaydi va xatoliklarni log qiladi
3. **Auth endpoint tuzatildi** - Kod avtomatik yuboriladi

## 📝 BOT SOZLASH QO'LLANMASI

### 1. Telegram Bot Yaratish

1. Telegram'da [@BotFather](https://t.me/BotFather) ga boring
2. `/newbot` buyrug'ini yuboring
3. Bot nomini kiriting (masalan: "Traffic Share Bot")
4. Bot username kiriting (masalan: @trafficshare_bot)
5. BotFather sizga TOKEN beradi (masalan: `1234567890:ABCdefGHIjklMNOpqrsTUVwxyz`)

### 2. .env Faylini Sozlash

`.env` faylida quyidagilarni o'zgartiring:

```bash
# Telegram Bot
TELEGRAM_BOT_TOKEN=SIZNING_HAQIQIY_TOKEN  # BotFather'dan olingan token
TELEGRAM_ADMIN_IDS=SIZNING_TELEGRAM_ID    # @userinfobot dan olishingiz mumkin
```

### 3. Telegram ID ni Topish

1. Telegram'da [@userinfobot](https://t.me/userinfobot) ga boring
2. Botga `/start` yuboring
3. Bot sizga ID'ingizni ko'rsatadi (masalan: 123456789)

### 4. Bot Bilan Aloqa O'rnatish

**MUHIM:** Kod yuborilishidan oldin bot bilan aloqa bo'lishi kerak!

1. Telegram'da botingizni toping (username orqali)
2. `/start` buyrug'ini yuboring
3. Bot sizga xush kelibsiz xabarini yuboradi

### 5. Testlash

```bash
# Bot test qilish
python3 test_bot_send.py

# Bot ishga tushirish (alohida terminal)
python3 -m traffic_share.bot.bot
```

## 🔍 MUAMMOLARNI BARTARAF ETISH

### Muammo: "Failed to send login code"

**Sabablari:**
1. ❌ Bot token noto'g'ri yoki eskirgan
2. ❌ Botni /start qilmagansiz
3. ❌ Telegram ID noto'g'ri
4. ❌ Bot o'chirilgan yoki bloklangan

**Yechimlar:**
1. ✅ BotFather'da yangi token oling va .env ga kiriting
2. ✅ Telegram'da botingizga /start yuboring
3. ✅ @userinfobot dan to'g'ri ID ni oling
4. ✅ Bot activ ekanligini BotFather'da tekshiring

### Muammo: "Bot not found"

```bash
# .env faylini tekshirish
cat .env | grep TELEGRAM_BOT_TOKEN

# Token to'g'riligini tekshirish (Python)
python3 << EOF
from telegram import Bot
import asyncio

async def check():
    bot = Bot(token="SIZNING_TOKEN")
    me = await bot.get_me()
    print(f"✅ Bot topildi: @{me.username}")

asyncio.run(check())
EOF
```

### Muammo: "Unauthorized"

Bu bot token noto'g'ri degani. Yangi token oling:
1. @BotFather ga boring
2. `/mybots` -> botingizni tanlang -> "API Token"
3. Token'ni ko'chiring va .env ga kiriting

## 📊 LOGLARNI TEKSHIRISH

```bash
# Server loglarini ko'rish
tail -f logs/traffic_share.log

# Faqat bot xabarlarini ko'rish
tail -f logs/traffic_share.log | grep "Login code"

# Xatoliklarni ko'rish
tail -f logs/traffic_share.log | grep "ERROR"
```

## 🎯 TO'LIQ TEST

1. **Bot sozlash:**
```bash
# .env faylida token va ID sozlang
nano .env
```

2. **Bot ishga tushirish:**
```bash
# Terminal 1: Server
uvicorn traffic_share.server.main:app --reload

# Terminal 2: Bot (ixtiyoriy - faqat /start kabi commandlar uchun)
python3 -m traffic_share.bot.bot
```

3. **Test:**
```bash
# Test skript
python3 test_bot_send.py

# Yoki API orqali
curl -X POST http://localhost:8000/api/auth/request_login_code \
  -H "Content-Type: application/json" \
  -d '{"telegram_id": SIZNING_ID}'
```

## 📱 MOBILE APP SOZLASH

Mobile app `.env` faylida API URL'ni sozlang:

```dart
// lib/utils/constants.dart
static const String API_BASE_URL = "http://SIZNING_SERVER_IP:8000";
```

## ✅ NATIJA

Endi kod yuborilganda:
1. ✅ Server kodini yaratadi
2. ✅ Bot avtomatik yuboradi
3. ✅ Foydalanuvchi Telegram'da oladi
4. ✅ Logda "Login code sent to XXX" ko'rinadi

Agar hali ham ishlamasa, `test_bot_send.py` skriptni ishga tushiring va xatolarni tekshiring.
