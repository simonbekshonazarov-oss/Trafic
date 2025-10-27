# 📱 Traffic Share - Flutter Mobile App

Foydalanuvchilar internet trafiklarini ulashib pul ishlash uchun Android ilova.

## 🎯 Xususiyatlar

- ✅ Telegram login
- ✅ Traffic sharing (start/stop)
- ✅ Real-time statistics
- ✅ Balance tracking
- ✅ Withdrawal requests
- ✅ Daily/Weekly/Monthly stats

## 📦 Struktura

```
lib/
├── api/              # API client & endpoints
│   ├── api_client.dart
│   ├── auth_api.dart
│   ├── traffic_api.dart
│   └── user_api.dart
├── models/           # Data models
│   ├── user_model.dart
│   └── traffic_model.dart
├── providers/        # State management
│   ├── auth_provider.dart
│   ├── traffic_provider.dart
│   └── balance_provider.dart
├── screens/          # UI screens
│   ├── splash_screen.dart
│   ├── login_screen.dart
│   └── home_screen.dart
├── widgets/          # Reusable widgets
│   ├── traffic_card.dart
│   ├── balance_card.dart
│   └── stats_card.dart
├── utils/            # Utilities
│   └── constants.dart
└── main.dart         # Entry point
```

## 🚀 Build

### Prerequisites
- Flutter SDK 3.0+
- Android Studio / Android SDK
- Java JDK 11+

### Commands

```bash
# Get dependencies
flutter pub get

# Run debug
flutter run

# Build release APK
flutter build apk --release

# Build split APKs
flutter build apk --split-per-abi --release
```

## 🔧 Configuration

`lib/utils/constants.dart` da API URL ni sozlang:

```dart
static const String baseUrl = 'http://185.139.230.196/api';
```

## 📱 Install

APK build qilgandan keyin:

```bash
# USB orqali
adb install build/app/outputs/flutter-apk/app-release.apk

# Yoki APK ni telefonga ko'chirib o'rnatish
```

## 📖 API Integration

Backend API: http://185.139.230.196/api

Endpoints:
- POST /auth/request_login_code
- POST /auth/verify_code
- POST /traffic/start
- POST /traffic/update
- POST /traffic/stop
- GET /balance

## 🎨 Customization

- **App name**: `android/app/src/main/AndroidManifest.xml`
- **Package**: `android/app/build.gradle`
- **Icon**: `android/app/src/main/res/mipmap-*/ic_launcher.png`
- **Colors**: `lib/utils/constants.dart`

## 📄 License

Private - Traffic Share Project
