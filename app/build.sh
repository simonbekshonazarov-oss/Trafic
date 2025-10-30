#!/bin/bash
set -e

echo "=== Flutter Yig'ish Skripti ==="
echo ""

# Flutter tekshiruvi
if command -v flutter &> /dev/null; then
    echo "✅ Flutter topildi: $(flutter --version | head -1)"
    cd /workspace/app
    
    echo ""
    echo "📦 Paketlarni o'rnatish..."
    flutter pub get
    
    echo ""
    echo "🔍 Kod tahlili..."
    flutter analyze || true
    
    echo ""
    echo "🏗️  APK yig'ish..."
    flutter build apk --release
    
    echo ""
    echo "✅ Yig'ish muvaffaqiyatli!"
    ls -lh build/app/outputs/flutter-apk/*.apk 2>/dev/null || echo "APK fayl topilmadi"
else
    echo "❌ Flutter topilmadi!"
    echo ""
    echo "Quyidagi usullardan birini ishlating:"
    echo ""
    echo "1. Flutter o'rnatish:"
    echo "   git clone https://github.com/flutter/flutter.git -b stable"
    echo "   export PATH=\"\$PATH:\$(pwd)/flutter/bin\""
    echo ""
    echo "2. Docker bilan:"
    echo "   docker run -it --rm -v \"\$(pwd):/app\" -w /app cirrusci/flutter:stable flutter build apk --release"
    echo ""
    echo "3. Build_STATUS.md faylini ko'ring"
fi
