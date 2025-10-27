#!/usr/bin/env python3
"""Check project completeness"""

import os
from pathlib import Path

# Required files
required_files = {
    'Core': [
        'traffic_share/core/constants.py',
        'traffic_share/core/exceptions.py',
        'traffic_share/core/security.py',
        'traffic_share/core/region_check.py',
    ],
    'Server': [
        'traffic_share/server/main.py',
        'traffic_share/server/config.py',
        'traffic_share/server/database.py',
        'traffic_share/server/models.py',
        'traffic_share/server/schemas.py',
        'traffic_share/server/dependencies.py',
        'traffic_share/server/utils.py',
        'traffic_share/server/logger.py',
        'traffic_share/server/limiter.py',
    ],
    'Services': [
        'traffic_share/server/services/auth_service.py',
        'traffic_share/server/services/user_service.py',
        'traffic_share/server/services/traffic_service.py',
        'traffic_share/server/services/buyer_service.py',
        'traffic_share/server/services/payment_service.py',
        'traffic_share/server/services/notification_service.py',
        'traffic_share/server/services/admin_service.py',
    ],
    'Routes': [
        'traffic_share/server/routes/auth_routes.py',
        'traffic_share/server/routes/user_routes.py',
        'traffic_share/server/routes/traffic_routes.py',
        'traffic_share/server/routes/payment_routes.py',
        'traffic_share/server/routes/buyer_routes.py',
        'traffic_share/server/routes/admin_routes.py',
        'traffic_share/server/routes/system_routes.py',
    ],
    'Tasks': [
        'traffic_share/server/tasks/cleanup_task.py',
        'traffic_share/server/tasks/stats_task.py',
        'traffic_share/server/tasks/notify_task.py',
        'traffic_share/server/tasks/backup_task.py',
    ],
    'Bot': [
        'traffic_share/bot/bot.py',
        'traffic_share/bot/handlers/user_handlers.py',
        'traffic_share/bot/handlers/admin_handlers.py',
        'traffic_share/bot/handlers/callback_handlers.py',
    ],
    'Scripts': [
        'traffic_share/scripts/init_db.py',
        'traffic_share/scripts/seed_data.py',
        'traffic_share/scripts/rotate_tokens.py',
        'traffic_share/scripts/clear_sessions.py',
        'traffic_share/scripts/export_stats.py',
    ],
    'Config': [
        'requirements.txt',
        '.env.example',
        'docker-compose.yml',
        'Dockerfile',
        'alembic.ini',
        'run_server.sh',
    ],
}

print("="*70)
print("TRAFFIC SHARE - LOYIHA TO'LIQLIGI TEKSHIRUVI")
print("="*70)

total_files = 0
missing_files = 0
existing_files = 0

for category, files in required_files.items():
    print(f"\n📁 {category}:")
    for file in files:
        total_files += 1
        if os.path.exists(file):
            size = os.path.getsize(file)
            print(f"  ✅ {file} ({size:,} bytes)")
            existing_files += 1
        else:
            print(f"  ❌ {file} - MISSING")
            missing_files += 1

print("\n" + "="*70)
print(f"NATIJA:")
print(f"  Jami fayllar: {total_files}")
print(f"  Mavjud: {existing_files} ✅")
print(f"  Yo'q: {missing_files} ❌")
print(f"  To'liqlik: {(existing_files/total_files)*100:.1f}%")
print("="*70)

if missing_files == 0:
    print("\n🎉 LOYIHA 100% TO'LIQ!")
else:
    print(f"\n⚠️  {missing_files} ta fayl yetishmayapti!")

