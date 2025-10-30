#!/bin/bash

###############################################################################
# FLUTTER FIXES VERIFICATION SCRIPT
# Bu skript barcha tuzatishlarni tekshiradi
###############################################################################

set -e  # Exit on error

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}  FLUTTER TUZATISHLARNI TEKSHIRISH${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo ""

# Check if Flutter is installed
if ! command -v flutter &> /dev/null; then
    echo -e "${RED}❌ Flutter topilmadi${NC}"
    echo -e "${YELLOW}Flutter o'rnatish: https://flutter.dev/docs/get-started/install${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Flutter topildi: $(flutter --version | head -n 1)${NC}"
echo ""

###############################################################################
# STEP 1: Clean previous build
###############################################################################

echo -e "${BLUE}═══ 1. OLDINGI BUILD'NI TOZALASH ═══${NC}"
flutter clean
echo -e "${GREEN}✅ Tozalash tugadi${NC}"
echo ""

###############################################################################
# STEP 2: Get dependencies
###############################################################################

echo -e "${BLUE}═══ 2. DEPENDENCY'LARNI YANGILASH ═══${NC}"
flutter pub get
if [ $? -ne 0 ]; then
    echo -e "${YELLOW}⚠️  Version konfliktlari aniqlandi. Major yangilanish o'tkazilmoqda...${NC}"
    flutter pub upgrade --major-versions
fi
echo -e "${GREEN}✅ Dependency'lar yangilandi${NC}"
echo ""

###############################################################################
# STEP 3: Check outdated packages
###############################################################################

echo -e "${BLUE}═══ 3. ESKIRGAN PAKETLARNI TEKSHIRISH ═══${NC}"
flutter pub outdated
echo ""

###############################################################################
# STEP 4: Analyze code
###############################################################################

echo -e "${BLUE}═══ 4. KODNI TAHLIL QILISH ═══${NC}"
flutter analyze --no-pub > analyze_report.txt 2>&1
ANALYZE_EXIT_CODE=$?

if [ $ANALYZE_EXIT_CODE -eq 0 ]; then
    echo -e "${GREEN}✅ Tahlil muvaffaqiyatli! Hech qanday xato topilmadi.${NC}"
    rm analyze_report.txt
else
    echo -e "${YELLOW}⚠️  Ba'zi xatolar topildi. Batafsil ma'lumot uchun analyze_report.txt ni ko'ring.${NC}"
    echo ""
    echo -e "${BLUE}Birinchi 20 qator:${NC}"
    head -n 20 analyze_report.txt
fi
echo ""

###############################################################################
# STEP 5: Run tests
###############################################################################

echo -e "${BLUE}═══ 5. TESTLARNI ISHGA TUSHIRISH ═══${NC}"
flutter test
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Barcha testlar muvaffaqiyatli o'tdi${NC}"
else
    echo -e "${YELLOW}⚠️  Ba'zi testlar muvaffaqiyatsiz bo'ldi${NC}"
fi
echo ""

###############################################################################
# STEP 6: Try to build APK
###############################################################################

echo -e "${BLUE}═══ 6. APK YARATISHNI SINASH ═══${NC}"
echo -e "${YELLOW}Bu biroz vaqt olishi mumkin...${NC}"
echo ""

flutter build apk --release > build_report.txt 2>&1
BUILD_EXIT_CODE=$?

if [ $BUILD_EXIT_CODE -eq 0 ]; then
    echo -e "${GREEN}✅ APK muvaffaqiyatli yaratildi!${NC}"
    echo ""
    echo -e "${BLUE}APK manzili:${NC}"
    echo "  build/app/outputs/flutter-apk/app-release.apk"
    echo ""
    echo -e "${BLUE}APK hajmi:${NC}"
    ls -lh build/app/outputs/flutter-apk/app-release.apk | awk '{print "  "$5}'
    rm build_report.txt
else
    echo -e "${RED}❌ APK yaratishda xato${NC}"
    echo ""
    echo -e "${BLUE}Xato tafssiloti (oxirgi 30 qator):${NC}"
    tail -n 30 build_report.txt
    echo ""
    echo -e "${YELLOW}To'liq hisobot: build_report.txt${NC}"
fi
echo ""

###############################################################################
# SUMMARY
###############################################################################

echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}  XULOSA${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo ""

echo "Tuzatilgan xatolar:"
echo "  ✅ CardTheme → CardThemeData"
echo "  ✅ update_service.dart API post method"
echo "  ✅ Foydalanilmagan importlar o'chirildi"
echo "  ✅ print → debugPrint"
echo "  ✅ withOpacity → withValues"
echo "  ✅ use_build_context_synchronously"
echo "  ✅ Super parameters (key)"
echo "  ✅ Asset directories yaratildi"
echo "  ✅ pubspec.yaml paketlar yangilandi"
echo "  ✅ test/widget_test.dart yaratildi"
echo ""

if [ $ANALYZE_EXIT_CODE -eq 0 ] && [ $BUILD_EXIT_CODE -eq 0 ]; then
    echo -e "${GREEN}✅ BARCHA XATOLAR TUZATILDI! 🎉${NC}"
    echo ""
    echo "Keyingi qadamlar:"
    echo "  1. APK ni qurilmada sinab ko'ring"
    echo "  2. Serverga yoki distribyusiya platformasiga yuklang"
    echo "  3. Foydalanuvchilar bilan ulashing"
else
    echo -e "${YELLOW}⚠️  Ba'zi muammolar qoldi${NC}"
    echo ""
    echo "Quyidagi fayllarni tekshiring:"
    echo "  - analyze_report.txt (agar mavjud bo'lsa)"
    echo "  - build_report.txt (agar mavjud bo'lsa)"
fi
echo ""

echo -e "${GREEN}Skript tugadi! 🚀${NC}"
