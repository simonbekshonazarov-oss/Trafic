

🏗️ TRAFFIC SHARE – Loyihaning to‘liq struktura tuzilmasi 

traffic_share/ 
├── __init__.py
      ├── server/
         ├── main.py 
         ├── config.py 
         ├── database.py
         ├── models.py
         ├── schemas.py 
         ├── dependencies.py  
         ├── utils.py 
         ├── logger.py 
         └── limiter.py  
         ├── services/ 
            ├── __init__.py 
            ├── auth_service.py
            ├── user_service.py 
            ├── traffic_service.py                       ├── buyer_service.py                       ├── payment_service.py                  ├── notification_service.py             └── admin_service.py               ├── routes/                                            ├── __init__.py                                   ├── auth_routes.py                           ├── user_routes.py                           ├── traffic_routes.py                        ├── buyer_routes.py                         ├── payment_routes.py                   ├── admin_routes.py                        └── system_routes.py           ├── tasks/                                                   ├── __init__.py         
         ├── cleanup_task.py  
         ├── notify_task.py 
         ├── stats_task.py
         └── backup_task.py 
├── core/ 
       ├── security.py 
       ├── exceptions.py 
       ├── constants.py 
       └── region_check.py 
├── migrations/ 
       ├── env.py
├── versions/ 
       └── 2025_10_26_init_db.py  └── tests/ 
       ├── test_auth.py 
       ├── test_traffic.py 
       ├── test_buyer.py 
       └── test_payment.py
├── bot/ 
      ├── __init__.py 
      ├── bot.py  
      ├── handlers/ 
         ├── __init__.py 
         ├── user_handlers.py 
         ├── admin_handlers.py 
         ├── callback_handlers.py 
         └── notification_handlers.py
      ├── utils/ 
         ├── __init__.py 
         ├── requests_helper.py
         ├── message_templates.py
         └── state_manager.py 
  
├── app/
  ├── lib/ 
   ├── main.dart
      ├── api/ 
      ├── api_client.dart
      ├── auth_api.dart
      ├── traffic_api.dart
      ├── user_api.dart 
      ├── buyer_api.dart 
      └── payment_api.dart 
   ├── models/
      ├── user_model.dart 
      ├── traffic_model.dart 
      ├── package_model.dart 
      └── payment_model.dart 
   ├── screens/ 
      ├── login_screen.dart  
      ├── home_screen.dart  
      ├── traffic_screen.dart  
      ├── wallet_screen.dart 
      └── settings_screen.dart 
     |── widgets/ 
       ├── traffic_card.dart 
       ├── balance_card.dart 
       └── loading_indicator.dart
    └── pubspec.yaml 
  ├── scripts/ 
      ├── init_db.py
      ├── seed_data.py  
      ├── rotate_tokens.py 
      ├── clear_sessions.py 
      └── export_stats.py
├── .env 
├── requirements.txt 
├── alembic.ini
├── README.md
├── run_server.sh 
└── docker-compose.yml 
└── config.py 

🔍 Modul turlari bo‘yicha qisqacha tavsif 

Modul  Fayl    Maqsadi
server
/main.py  FastAPI app yaratiladi, barcha route-lar ulangan joy
routes/ Har bir yo‘nalish (auth, user, buyer, traffic) uchun alohida API fayl services
/Backend logikasi shu yerda — modelni boshqarish, hisoblash, token generatsiya va h.k.
models.py ORM jadval tuzilmalari
schemas.py API so‘rov va javob validatorlari
bot/Telegram bot uchun barcha fayllar
app/Flutter mobil ilova kodi
tasks/Fon jarayonlar (notify, backup, stats)
scripts/Admin uchun konsol yordamchi fayllar (init, seed, rotate)
.env Sirli kalitlar va sozlamalar
requirements.txt  Python kutubxonalar ro‘yxati 

🧠 Strukturani afzalliklari 

✅ To‘liq modular arxitektura – har bir modul mustaqil ishlaydi
✅ Clean separation – API, servis, va data qatlamlar ajratilgan
✅ Oson kengaytiriladi – yangi endpoint, modul, yoki xizmat qo‘shish oson
✅ Yuqori xavfsizlik – token, IP va foydalanuvchi boshqaruvi markazlashtirilgan



🚀 TRAFFIC SHARE — TO‘LIQ ISH OQIMI (SYSTEM FLOW OVERVIEW) 

🎯 Loyiha maqsadi 

Traffic Share — bu foydalanuvchilar (providers) o‘z internet trafiklarini ilova orqali ulashadigan va xaridorlar (buyers) bu trafikka API orqali ulana oladigan tizim.
Barcha aloqa va ma’lumot almashish API endpointlar orqali amalga oshadi.
Markaziy boshqaruv markazi — server.py (backend). 

🧩 Asosiy komponentlar 

• server.py (FastAPI backend) — butun tizim logikasi, ma’lumotlar bazasi, autentifikatsiya, monitoring va API endpointlarni boshqaradi. 

• Apk ilova (Flutter frontend) — foydalanuvchi trafik ulashish, monitoring, kirish/chiqish, balans va tunel boshqaruvini bajaradi. 

• bot.py (Telegram bot) — foydalanuvchi va admin uchun real-vaqt xabarlar, balans, to‘lov, kod yuborish xizmatlarini bajaradi. 

• config.py — .env fayldan o‘zgaruvchilarni o‘qiydi va serverda ishlatadi. 

• .env — maxfiy kalitlar, tokenlar, DB konfiguratsiyasi, API kalitlari. 

• PostgreSQL — barcha ma’lumotlar saqlanadigan asosiy ma’lumotlar bazasi. 

⚙️ I. Foydalanuvchi ish oqimi (Mobile App tarafidan) 

1️⃣. Ro‘yxatdan o‘tish / Kirish 

• Ilova foydalanuvchining Telegram raqamini yuboradi. 

• Server login kod generatsiya qiladi. 

• bot.py foydalanuvchining Telegramiga kodni yuboradi. 

• Foydalanuvchi ilovada kodni kiritadi. 

• Server kodni tekshiradi → login sessiya yaratiladi. 

🧠 Natija: foydalanuvchi tizimda ro‘yxatdan o‘tgan yoki kirgan. 

2️⃣. Trafik ulanishini faollashtirish 

• Ilovada foydalanuvchi “Start Sharing Traffic” bosadi. 

• Ilova foydalanuvchi IP, qurilma turi, joylashuvni aniqlaydi. 

• Server mintaqani tekshiradi: faqat USA/EU IP-lar ruxsat etiladi. 

• Agar foydalanuvchi VPN yoki noto‘g‘ri IP bilan kirsa — server ulanishni rad etadi. 

• Server ilovaga “tunelni ishga tushirish” signalini yuboradi. 

🧠 Natija: foydalanuvchi trafik uzatishni boshlaydi. 

3️⃣. Trafik ma’lumotlarini yuborish 

• Ilova real-vaqt rejimida trafik hajmini hisoblaydi. 

• Ilova serverga muntazam ravishda trafik ma’lumotlarini API orqali yuboradi. 

• Server ushbu trafikni traffic_sessions jadvaliga yozadi va buyers paketlariga taqsimlaydi. 

• Shu bilan birga bot.py foydalanuvchi uchun “Live traffic” statusini yangilab boradi. 

🧠 Natija: foydalanuvchining trafiklari real vaqt bazaga va statistikaga tushadi. 

4️⃣. Trafikni to‘xtatish 

• Ilova “Stop Sharing” tugmasini bosadi. 

• Server seansni yakunlaydi, statusni “completed” ga o‘zgartiradi. 

• Balans hisoblanadi (trafik hajmi * $/GB). 

• Foydalanuvchining balans jadvaliga yoziladi. 

• bot.py orqali foydalanuvchiga “Session completed” haqida bildirish yuboriladi. 

🧠 Natija: sessiya yopiladi, balans yangilanadi. 

5️⃣. Balans va to‘lov 

• Foydalanuvchi ilovadan balansini ko‘radi (API orqali serverdan olinadi). 

• Agar balans ≥ 5 $, foydalanuvchi “Withdraw” so‘rov yuboradi. 

• Server cryptomus bilan to‘lovni amalga oshiradi. 

• bot.py admin kanaliga chek yuboradi va foydalanuvchiga “Payment completed” xabari jo‘natadi. 

🧠 Natija: foydalanuvchi to‘lovni oladi, balansdan yechiladi. 

⚙️ II. Buyer ish oqimi (trafik xaridorlari) 

1️⃣. Buyer ro‘yxatdan o‘tishi 

• Admin yangi buyer yaratadi va unga token ajratadi. 

• Tokenlar orqali buyerlar API bilan ishlaydi. 

2️⃣. Trafik paketlarini olish 

• Buyer o‘z tokeni bilan serverga so‘rov yuboradi. 

• Server available holatdagi trafik paketlardan buyerga birini taqdim etadi. 

• Paket ma’lumotlari: user_id, ip, uuid, size_bytes. 

• Har bir foydalanuvchi + IP kombinatsiyasi faqat bitta paketga biriktiriladi. 

3️⃣. Trafik holatini yangilash 

• Buyer trafikni ishlatayotgan paytda serverga statuslarni yuboradi: in_progress, completed, failed. 

• Server paket holatini yangilaydi. 

• Har bir yakunlangan trafik package_allocations va buyer_logs da qayd etiladi. 

4️⃣. Monitoring va hisob 

• Admin dashboard orqali buyerlar faoliyatini ko‘radi: 

• qancha paket ajratilgan 

• qancha ishlatilgan 

• qancha trafik jo‘natilgan 

• Buyer tokenlari kerak bo‘lsa yangilanadi (rotate) yoki o‘chiriladi (revoke). 

🧠 Natija: har bir buyerning ishlashi nazorat ostida bo‘ladi. 

⚙️ III. Admin ish oqimi 

1️⃣. Admin tizimga kirish 

• Telegram ID orqali admin tanib olinadi. 

• Admin panel yoki bot orqali tizimga ulanadi. 

2️⃣. Foydalanuvchi boshqaruvi 

• Admin barcha foydalanuvchilar ro‘yxatini ko‘radi. 

• Foydalanuvchini bloklash, faollashtirish, balans ko‘rish, trafik tarixini kuzatish. 

3️⃣. Buyer boshqaruvi 

• Buyer yaratish, tahrirlash, token yaratish yoki o‘chirish. 

• Har bir buyer uchun: 

• aktiv paketlar soni 

• yakunlangan paketlar 

• oxirgi faol vaqt 

• token holati 

4️⃣. Paket boshqaruvi 

• Yangi paketlar yaratish (bulk_create). 

• Paketni buyerga biriktirish yoki bekor qilish. 

• Eskirgan (allocated lekin in_progress bo‘lmagan) paketlarni avtomatik tozalash. 

• Har bir paketning tarixini ko‘rish (kimga berilgan, qancha ishlatilgan). 

5️⃣. Tizim nazorati 

• Server sog‘lomlik (RAM, CPU, uptime) monitoringi. 

• Har minutdagi API so‘rovlar soni. 

• Aktiv foydalanuvchilar va buyerlar statistikasi. 

• Xatolik loglari, tarmoq yuklanishlari. 

• DB zaxira nusxasini olish (backup). 

6️⃣. Bildirishnomalar va yangilanishlar 

• Admin yangi ilova versiyasi chiqqanda bot va ilovaga notification yuboradi. 

• bot.py orqali foydalanuvchilarga “update available” xabari tarqatiladi. 

• Har kunlik hisobot admin kanaliga yuboriladi: 

• kunlik foydalanuvchi soni 

• umumiy trafik hajmi 

• buyerlar bo‘yicha taqsimot 

🧠 Natija: tizim barqaror ishlaydi, nazorat markazlashtirilgan. 

⚙️ IV. Bot ish oqimi 

1️⃣. Login kodi yuborish 

• Serverdan so‘rov kelganda bot foydalanuvchiga login kod yuboradi. 

• Foydalanuvchi uni ilovada kiritadi. 

2️⃣. Balans va trafik 

• Bot serverdan foydalanuvchi trafik ma’lumotlarini olib beradi. 

• Balans, kunlik/oylik statistikalar ko‘rsatiladi. 

3️⃣. To‘lov 

• Withdraw so‘rov server orqali tasdiqlangach, bot foydalanuvchiga to‘lov haqida xabar beradi. 

• Admin kanalga to‘lov cheki yuboriladi. 

4️⃣. Admin xabarlari 

• Server adminlar uchun bot orqali: 

• yangi foydalanuvchi kirganini 

• buyer token yaratilganini 

• muhim yangiliklarni yuboradi. 

🧠 V. Tizimdagi asosiy jarayonlar bir-biriga bog‘lanishi 

JarayonBoshlovchiAmal bajaruvchiNatijaRo‘yxatdan o‘tishIlovaServer + BotFoydalanuvchi sessiyasi yaratiladiTrafik yuborishIlovaServerTrafik bazaga tushadiTrafik taqsimotiServerBuyerPaketlar ajratiladiTrafik nazoratiServerAdminStatistik ma’lumotlarTo‘lovIlova/BotServer + PayPal APIPul foydalanuvchiga o‘tkaziladiBildirishnomaServerBot/IlovaXabarlar yuboriladiToken boshqaruviAdminServerToken yangilanishi yoki o‘chirilishiAudit va logServerPostgreSQLHarakatlar tarixda saqlanadi 

🧱 VI. Texnik asoslar 

• Backend: FastAPI + SQLAlchemy 

• Database: PostgreSQL 

• Caching/Rate limit: Redis 

• Frontend: Flutter (Android APK) 

• Bot: Python-telegram-bot 

• Payment: cryptomus api 

• Deployment: VPS (Ubuntu 24.04), Nginx reverse proxy 

• Logging: Uvicorn + RotatingFileHandler 

• Monitoring: Prometheus (optional) 

🔒 VII. Xavfsizlik choralari 

• Har bir API token sha256 hash holida saqlanadi. 

• Har bir endpoint rate-limit ostida (limiter). 

• Region tekshiruvi — faqat USA/EU IP-lar qabul qilinadi. 

• VPN yoki ma’lum server IP-lar “denylist” orqali bloklanadi. 

• HTTPS majburiy. 

• .env serverda lokal, repo’da yo‘q. 

📊 VIII. Asosiy statistik modullar 

• Foydalanuvchilar soni / faol ulanishlar 

• Kunlik va oylik trafik (GB) 

• Buyerlar bo‘yicha trafik taqsimoti 

• To‘lovlar statistikasi 

• Server sog‘lomlik (uptime, so‘rovlar/minut) 

• Admin uchun umumiy dashboard 

✅ IX. Loyiha ish sikli (bosqichlar bo‘yicha) 

• Foydalanuvchi login qiladi 

• Ilova server bilan ulanish o‘rnatadi 

• IP va region tekshiriladi 

• Trafik sessiyasi boshlanadi 

• Server trafikni buyerlar paketlariga taqsimlaydi 

• Buyer trafikni ishlatadi 

• Sessiya tugaydi, balans hisoblanadi 

• PayPal orqali to‘lov amalga oshiriladi 

• Bot va ilovaga xabar yuboriladi 

• Admin panelda natijalar kuzatiladi 

Bu tavsif — butun loyihaning 100 % to‘liq ish jarayonini, modullararo aloqalarni va backend-logikani bosqichma-bosqich ko‘rsatib beradi.




Api endpointlarini 
Toʻliq API Endpointlar roʻyxati — barcha modul va funksiyalar (toʻliq, batafsil) 

Quyida loyihangizdagi barcha kerakli API endpointlar toʻliq roʻyxati berilgan. Har bir endpoint uchun: HTTP metod, path, auth talabi, maqsad (qisqacha), kiruvchi maʼlumot (summary), natija / DB taʼsir va eslatma / acceptance keltirilgan. Ushbu roʻyxat server.py (FastAPI) uchun toʻliq API contract hisoblanadi — ilova va bot shu endpointlar orqali 100% ishlaydi. 

Qayd: Auth maydonida NONE — autentifikatsiya talab qilinmaydi; USER — foydalanuvchi JWT yoki token; BUYER — buyer API token; ADMIN — admin JWT / admin API key; BOT — bot auth (bot token yoki bot-to-server secret). 

1. Auth (Roʻyxat, Login, Token) 

POST /api/auth/register 

• Auth: NONE 

• Maqsad: Yangi foydalanuvchini yaratish (telegram_id / phone / email) 

• Request (summary): { "telegram_id": 12345, "phone": "+998...", "username": "bob" } 

• DB effect: INSERT INTO users (creates unverified user) 

• Response: { "user_id": 1, "message": "verification_sent" } 

• Notes: triggers /api/bot/send_login_code internally. 

POST /api/auth/request_login_code 

• Auth: NONE 

• Maqsad: Telegram bot orqali login kodi joʻnatish (ilovadan chaqiriladi) 

• Request: { "telegram_id": 12345 } 

• DB effect: INSERT INTO login_codes (code, expires_at) 

• Response: { "ok": true } 

• Notes: Bot will send code to telegram user via bot service endpoint. 

POST /api/auth/verify_code 

• Auth: NONE 

• Maqsad: Foydalanuvchi tomonidan kiritilgan kodni tekshirish va token berish 

• Request: { "telegram_id": 12345, "code": "123456" } 

• DB effect: UPDATE login_codes SET used=TRUE, UPDATE users SET is_verified=TRUE, INSERT session/token 

• Response: { "access_token": "...", "refresh_token": "...", "expires_in": 3600 } 

• Notes: issue JWT (or opaque token). Save refresh token if using. 

POST /api/auth/refresh 

• Auth: NONE (provides refresh token) 

• Maqsad: Token yangilash 

• Request: { "refresh_token": "..." } 

• DB effect: validate refresh token, optionally revoke old one, issue new access token 

• Response: { "access_token": "...", "refresh_token": "..." } 

2. User (Profil, Settings, Sessions) 

GET /api/user/me 

• Auth: USER 

• Maqsad: Foydalanuvchi profilini olish 

• Response: { "id": 1, "telegram_id": 12345, "username": "bob", "balance": 12.34, ... } 

• DB: SELECT * FROM users 

POST /api/user/update 

• Auth: USER 

• Maqsad: Profilni yangilash 

• Request: { "phone": "...", "email": "...", "settings": { ... } } 

• DB: UPDATE users SET ... 

• Response: { "ok": true } 

POST /api/user/device/register 

• Auth: USER 

• Maqsad: Ilova / qurilma roʻyxatdan oʻtkazish (device_id) 

• Request: { "device_id": "uuid", "os": "android", "ip": "1.2.3.4" } 

• DB: INSERT INTO devices/sessions (user_id, device_id, last_active) 

• Response: { "session_id": "..." } 

GET /api/user/devices 

• Auth: USER / ADMIN (admin can pass user_id) 

• Maqsad: Foydalanuvchining qurilmalari va sessiyalari roʻyxati 

• Response: list of devices/sessions 

3. Traffic / Tunnel (Start/Update/Stop, History) 

POST /api/traffic/start 

• Auth: USER 

• Maqsad: Yangi trafik sessiyasini boshlash (tunel start) 

• Request: { "device_id": "uuid", "local_ip": "10.x.x.x", "public_ip": "1.2.3.4", "client_version": "1.0.0" } 

• DB effect: INSERT INTO traffic_sessions (user_id, device_id, start_time, start_ip) 

• Response: { "session_id": "...", "ok": true } 

• Acceptance: returns session_id to be used for updates. 

POST /api/traffic/update 

• Auth: USER 

• Maqsad: Real-time trafik metriklarini yuborish (periodic) 

• Request: { "session_id": "...", "bytes_tx": 1024, "bytes_rx": 2048, "interval_seconds": 10 } 

• DB effect: INSERT INTO traffic_logs (session_id, bytes_tx, bytes_rx, ts) and/or UPDATE traffic_sessions SET bytes_total = bytes_total + ... 

• Response: { "ok": true } 

• Notes: prefer batching; use async writes/queue if high throughput. 

POST /api/traffic/stop 

• Auth: USER 

• Maqsad: Sessiyani yopish va final statistikani joʻnatish 

• Request: { "session_id": "...", "final_bytes_tx": 12345, "final_bytes_rx": 0 } 

• DB effect: UPDATE traffic_sessions SET end_time=now(), bytes_total=...; INSERT final traffic_log 

• Response: { "ok": true } 

GET /api/traffic/history 

• Auth: USER / ADMIN 

• Maqsad: Trafik tarixini olish (filters: date range, session_id) 

• Request params: ?from=2025-10-01&to=2025-10-26&page=1 

• Response: paginated history rows. 

GET /api/traffic/summary 

• Auth: USER / ADMIN 

• Maqsad: Day/week/month/all aggregation (GBs, sessions) 

• Response: { "daily": 1.2, "weekly": 8.5, ... } 

4. Balance & Payments (withdrawals, payouts) 

GET /api/balance 

• Auth: USER 

• Maqsad: Hisob balansini olish (tariflarga asosan hisoblangan) 

• Response: { "available": 12.5, "pending": 3.0, "currency": "USD" } 

• DB: calculates from traffic_logs * price_per_gb` minus payouts. 

POST /api/withdraw/request 

• Auth: USER 

• Maqsad: Withdraw (payout) soʻrovi yaratish 

• Request: { "amount": 10.0, "method": "paypal", "target": "paypal@example.com" } 

• DB effect: INSERT INTO payments (user_id, amount, method, status='pending') 

• Response: { "payment_id": 123, "status": "pending" } 

• Business rules: check min/max, sufficient balance. 

GET /api/withdraw/status/{payment_id} 

• Auth: USER / ADMIN 

• Maqsad: Toʻlov statusini olish 

• Response: { "payment_id":123, "status":"completed", "tx_reference":"..." } 

POST /api/payments/paypal/create_payout (internal/admin) 

• Auth: ADMIN (or server-to-paypal background) 

• Maqsad: PayPal Payout yaratish (sandbox/live) 

• Request: { "payment_id": 123 } 

• DB effect: interacts with PayPal API; on success UPDATE payments SET status='completed', tx_reference=... 

• Webhook: PayPal will call /api/webhook/paypal for asynchronous confirmation. 

POST /api/webhook/paypal 

• Auth: NONE (verify request signature) 

• Maqsad: PayPal webhook endpoint — update payment status 

• Request: PayPal webhook payload 

• DB effect: UPDATE payments accordingly 

• Security: verify PayPal signature. 

5. Bot (server ↔ bot interactions) 

POST /api/bot/send_login_code 

• Auth: BOT (or internal) 

• Maqsad: Bot triggered to send login code to user (server instructs bot) 

• Request: { "telegram_id": 12345, "code": "123456" } 

• Effect: call Telegram API via bot; log login_codes entry. 

POST /api/bot/notify_admin 

• Auth: BOT / SERVER 

• Maqsad: Bot/Server push notification to admin(s) via bot 

• Request: { "type":"withdraw_request","payload": {...} } 

• Effect: push message to admin telegram ids (via bot). 

POST /api/bot/update_balance 

• Auth: BOT / SERVER 

• Maqsad: Update user's balance shown in bot (optional) 

• Request: { "user_id": 1, "balance": 12.5 } 

• Effect: update users.balance or send message. 

POST /api/bot/live_traffic 

• Auth: BOT / SERVER 

• Maqsad: push live traffic events (for admin channels / user channels) 

• Request: { "user_id":1, "session_id":"...", "bytes": 1024 } 

• Effect: send messages; log. 

6. Buyers & Packages (core buyer flow and package allocation) 

POST /api/admin/buyers 

• Auth: ADMIN 

• Maqsad: Yangi buyer yaratish 

• Request: { "name":"milon_buyer", "contact":"...", "region":"US" } 

• DB: INSERT INTO buyers 

• Response: buyer record. 

GET /api/admin/buyers 

• Auth: ADMIN 

• Maqsad: Buyerlar roʻyxati (filterable) 

• Response: list of buyers with stats. 

POST /api/admin/buyers/{buyer_id}/tokens 

• Auth: ADMIN 

• Maqsad: Buyer uchun API token yaratish 

• Request: { "expires_at": "...", "description":"prod" } 

• DB: INSERT INTO buyer_tokens (store hashed token) 

• Response: { "token": "plain_token_only_once" } 

GET /api/admin/buyers/{buyer_id}/tokens 

• Auth: ADMIN 

• Maqsad: Buyer token metadata (no raw token) 

• Response: list of tokens with meta. 

POST /api/admin/tokens/{token_id}/revoke 

• Auth: ADMIN 

• Maqsad: Token revoke / disable 

• DB: UPDATE buyer_tokens SET is_revoked=true 

• Response: { "ok": true } 

POST /api/admin/packages/bulk_create 

• Auth: ADMIN 

• Maqsad: Bulk package ingest (CSV/JSON) — create many packages for allocation 

• Request: { "packages": [ { "uuid": "...", "user_id": 1, "ip":"1.2.3.4", "size_bytes": 1000000 }, ... ] } 

• DB: insert into packages with status='available' 

• Response: { "created": N, "errors": [] } 

GET /api/admin/packages 

• Auth: ADMIN 

• Maqsad: Paketlar roʻyxati va filterlar (status, buyer_id, user_id, ip) 

• Response: paginated packages. 

POST /api/admin/packages/{package_id}/assign 

• Auth: ADMIN 

• Maqsad: Paketni qoʻlda buyerga tayinlash 

• DB: transactional UPDATE packages → assigned_buyer_id, status='allocated'; INSERT into package_allocations 

• Response: { "ok": true } 

POST /api/admin/packages/{package_id}/revoke 

• Auth: ADMIN 

• Maqsad: Paketni bekor qilish yoki qayta ishlovchi holatga oʻtkazish 

• DB: UPDATE packages SET status='revoked' or reset depending on policy. 

POST /api/buyer/packets/pull 

• Auth: BUYER (Authorization: Bearer <BUYER_TOKEN>) 

• Maqsad: Buyer yangi paket(lar) soʻraydi (core) 

• Request: { "max_count":1, "region":"US" } 

• DB logic: transactional selection SELECT ... FOR UPDATE SKIP LOCKED on packages where status='available' and assigned_buyer_id IS NULL and optional filters; then UPDATE those rows to status='allocated', assigned_buyer_id=buyer_id, assigned_at=now(); INSERT into package_allocations. 

• Response: { "packages": [ { "uuid":"...", "user_id":1, "ip":"1.2.3.4", "size_bytes": 1000000 } ] } or 204 No Content if none. 

• Notes: enforce one user + one ip + one package rule: check existing allocated/in_progress packages for same user+ip and skip/deny if present. Rate-limit required. 

POST /api/buyer/packets/{uuid}/status 

• Auth: BUYER 

• Maqsad: Paket holatini yangilash (accepted/in_progress/completed/failed) 

• Request: { "status":"in_progress", "bytes_sent": 123456 } 

• DB: UPDATE packages SET status = ..., bytes_sent=... and package_allocations history. 

• Response: { "ok": true } 

GET /api/buyer/me/allocations 

• Auth: BUYER 

• Maqsad: Oʻziga tegishli faol paketlarni koʻrish 

• Response: list of allocated/in_progress packages. 

GET /api/admin/buyers/{buyer_id}/usage 

• Auth: ADMIN 

• Maqsad: Buyer statistikasi (total_assigned, active, completed) 

• Response: statistics. 

7. Admin (Monitoring, Users, Controls) 

POST /api/admin/create_superadmin 

• Auth: initial bootstrap (one-time) 

• Maqsad: superadmin yaratish / secure seeding. 

GET /api/admin/users 

• Auth: ADMIN 

• Maqsad: All users list (with filters/pagination) 

• Response: list users (id, telegram_id, balance, is_active, created_at) 

POST /api/admin/user/{user_id}/ban 

• Auth: ADMIN 

• Maqsad: block a user (ban) 

• DB: UPDATE users SET is_active=false 

• Response: { "ok": true } 

POST /api/admin/notify 

• Auth: ADMIN 

• Maqsad: mass push notification to all or filtered users (via bot/in-app) 

• Request: { "target": "all|active|region:US", "message":"..." } 

• Effect: enqueue messages; bot sends notifications. 

GET /api/admin/reports/daily 

• Auth: ADMIN 

• Maqsad: Daily reports (trafic, payouts, active users) 

• Response: aggregated numbers and charts data. 

GET /api/admin/metrics 

• Auth: ADMIN 

• Maqsad: System metrics (requests per minute, error rates, db connections) 

• Response: values from Prometheus/psutil. 

8. System & Monitoring (health, version, logs) 

GET /api/system/health 

• Auth: NONE 

• Maqsad: healthcheck for load balancer / uptime monitors 

• Response: { "status":"ok", "time":"..." } 

GET /api/system/version 

• Auth: NONE or ADMIN 

• Maqsad: API & app version (for apk to check updates) 

• Response: { "api_version":"v1.0", "app_latest":"1.0.2", "force_update": false } 

GET /api/system/requests 

• Auth: ADMIN 

• Maqsad: recent request counts (1m/5m/15m) — sourced from Redis/metrics 

• Response: counters. 

GET /api/system/logs 

• Auth: ADMIN 

• Maqsad: recent server logs (searchable) 

• Request params: ?level=error&limit=100 

• Response: log lines. 

9. Webhooks & Third-party integrations 

POST /api/webhook/paypal 

• Auth: NONE (must verify signature) 

• Maqsad: PayPal sends payout events — server updates payments 

• DB: UPDATE payments SET status=..., tx_reference=... 

• Response: 200 OK if verified. 

POST /api/webhook/telegram (optional) 

• Auth: verify signature/secret 

• Maqsad: If using webhook mode for bot (instead of polling) — Telegram updates come here. Server processes messages if desired. 

POST /api/webhook/ipintel (optional) 

• Auth: internal 

• Maqsad: third-party IP intelligence callbacks (rare) — update ip_reputation DB. 

10. Utilities / Admin Tools / Maintenance 

POST /api/admin/packages/cleanup_stale_allocations 

• Auth: ADMIN 

• Maqsad: Clean allocated packages stuck beyond TTL (e.g., not confirmed in 60s) 

• Effect: reset to available or mark revoked depending on policy. 

POST /api/admin/rotate_buyer_token 

• Auth: ADMIN 

• Maqsad: rotate buyer token (revoke old + create new) 

• Response: returns new token (plaintext only once). 

POST /api/admin/backup/db 

• Auth: ADMIN 

• Maqsad: trigger DB backup to configured storage (S3) 

• Effect: background job. 

GET /api/admin/audit/search 

• Auth: ADMIN 

• Maqsad: search audit logs (filters: user, action, date) 

• Response: matched audit records. 

11. Security & Rate-limiting endpoints (internal) 

Token validation middleware 

• Behavior: every USER/BUYER/ADMIN request must be validated. 

• Revoke check: check token revocation list (Redis or DB). 

Rate limit state 

• Endpoints like /api/buyer/packets/pull and /api/auth/request_login_code must be rate-limited (per token, per ip). Use Redis. 

12. Example Request/Response snippets (compact) 

Pull packet (buyer) 

• Request: 

POST /api/buyer/packets/pull Authorization: Bearer BUYER_TOKEN { "max_count": 1, "region": "US" } 

• Response: 

200 OK { "packages": [ { "uuid": "pkg-abc-123", "user_id": 42, "ip": "93.184.216.34", "size_bytes": 1000000, "assigned_at": "2025-10-26T12:34:56Z" } ] } 

Update traffic (user) 

• Request: 

POST /api/traffic/update Authorization: Bearer USER_TOKEN { "session_id": "sess-uuid", "bytes_tx": 4096, "interval_seconds": 10 } 

• Response: 

200 OK { "ok": true } 

13. Acceptance & Operational notes (implementer guidance) 

• Atomic allocation: implement pull with Postgres FOR UPDATE SKIP LOCKED or UPDATE ... RETURNING to avoid double allocation. 

• Store only token hash in DB; return plaintext only on creation. 

• Rate limit: buyer pull must be restricted (e.g., 1 req/s, burst limit). 

• Allocated TTL: set allocated_ttl (configurable). If buyer does not confirm (in_progress) within TTL, auto-rollback or mark revoked depending on business rule. 

• Audit: write every allocation/event to package_allocations and buyer_logs. 

• Monitoring: expose /api/admin/metrics and instrument Prometheus metrics for request counts, allocation rates, DB errors, payout failures. 

• Security: all endpoints use HTTPS; admin endpoints require strong auth + IP allowlist for extra safety. 

14. Next practical steps 

• Ushbu endpoint spec bo‘yicha OpenAPI (Swagger) fayl yaratish — shu orqali ilova va bot kodlarini minimal qilish mumkin. 

• DB schema (SQLAlchemy / Alembic) bilan har bir jadvalni yarating. 

• pull endpoint uchun tranzaksion test script yozing va parallel soʻrovlarni simulyatsiya qiling. 

• Rate-limiting + token hash saqlash + audit loglarni implementatsiya qiling.



barcha API endpointlar — tarif va izohsiz toza ro‘yxat: 

1. Auth 

• POST /api/auth/register 

• POST /api/auth/request_login_code 

• POST /api/auth/verify_code 

• POST /api/auth/refresh 

2. User 

• GET /api/user/me 

• POST /api/user/update 

• POST /api/user/device/register 

• GET /api/user/devices 

3. Traffic 

• POST /api/traffic/start 

• POST /api/traffic/update 

• POST /api/traffic/stop 

• GET /api/traffic/history 

• GET /api/traffic/summary 

4. Balance & Payments 

• GET /api/balance 

5. Bot 

• POST /api/bot/send_login_code 

• POST /api/bot/notify_admin 

• POST /api/bot/update_balance 

• POST /api/bot/live_traffic 

6. Buyers & Packages 

• POST /api/admin/buyers 

• GET /api/admin/buyers 

• POST /api/admin/buyers/{buyer_id}/tokens 

• GET /api/admin/buyers/{buyer_id}/tokens 

• POST /api/admin/tokens/{token_id}/revoke 

• POST /api/admin/packages/bulk_create 

• GET /api/admin/packages 

• POST /api/admin/packages/{package_id}/assign 

• POST /api/admin/packages/{package_id}/revoke 

• POST /api/buyer/packets/pull 

• POST /api/buyer/packets/{uuid}/status 

• GET /api/buyer/me/allocations 

• GET /api/admin/buyers/{buyer_id}/usage 

7. Admin 

• POST /api/admin/create_superadmin 

• GET /api/admin/users 

• POST /api/admin/user/{user_id}/ban 

• POST /api/admin/notify 

• GET /api/admin/reports/daily 

• GET /api/admin/metrics 

8. System 

• GET /api/system/health 

• GET /api/system/version 

• GET /api/system/requests 

• GET /api/system/logs 

9. Webhooks 

• POST /api/webhook/paypal 

• POST /api/webhook/telegram 

• POST /api/webhook/ipintel 

10. Utilities / Maintenance 

• POST /api/admin/packages/cleanup_stale_allocations 

• POST /api/admin/rotate_buyer_token 

• POST /api/admin/backup/db 

• GET /api/admin/audit/search


to'lov tizimi paypal emas CRYPTOMUS bo'ladi loyihada ishlatilgan barcha paypal sozlati cryptomus bilan almashtirilsin va api so'rovlarini shu saytdan ko'rib chiq  https://doc.cryptomus.com/uz/methods/request-format
