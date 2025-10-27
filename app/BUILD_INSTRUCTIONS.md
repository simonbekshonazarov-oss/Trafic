# 📱 Flutter APK Build Instructions

## 🔧 Prerequisites

1. **Flutter SDK** (3.0+)
   ```bash
   flutter --version
   ```

2. **Android Studio** or **Android SDK**

3. **Java JDK** (11+)

## 📦 Setup

### 1. Navigate to App Directory

```bash
cd /workspace/app
```

### 2. Get Dependencies

```bash
flutter pub get
```

### 3. Configure API URL

Edit `lib/utils/constants.dart`:

```dart
// VPS IP yoki domain
static const String baseUrl = 'http://185.139.230.196/api';
```

Agar HTTPS domain bo'lsa:
```dart
static const String baseUrl = 'https://yourdomain.com/api';
```

### 4. Update Android Manifest

`android/app/src/main/AndroidManifest.xml`:

```xml
<manifest xmlns:android="http://schemas.android.com/apk/res/android">
    <!-- Permissions -->
    <uses-permission android:name="android.permission.INTERNET" />
    <uses-permission android:name="android.permission.ACCESS_NETWORK_STATE" />
    <uses-permission android:name="android.permission.ACCESS_WIFI_STATE" />
    <uses-permission android:name="android.permission.FOREGROUND_SERVICE" />
    
    <application
        android:label="Traffic Share"
        android:icon="@mipmap/ic_launcher"
        android:usesCleartextTraffic="true">
        ...
    </application>
</manifest>
```

## 🏗️ Build APK

### Debug APK (Test uchun)

```bash
flutter build apk --debug
```

Output: `build/app/outputs/flutter-apk/app-debug.apk`

### Release APK (Production)

```bash
flutter build apk --release
```

Output: `build/app/outputs/flutter-apk/app-release.apk`

### Split APKs (Har bir architecture uchun)

```bash
flutter build apk --split-per-abi --release
```

Output:
- `app-armeabi-v7a-release.apk`
- `app-arm64-v8a-release.apk`
- `app-x86_64-release.apk`

## 📱 Install APK

### Via USB (ADB)

```bash
flutter install
# yoki
adb install build/app/outputs/flutter-apk/app-release.apk
```

### Via File Transfer

APK faylni telefonga ko'chirish va o'rnatish.

## 🔐 Signing (Release uchun)

### 1. Create Keystore

```bash
keytool -genkey -v -keystore ~/traffic-share-key.jks \
  -keyalg RSA -keysize 2048 -validity 10000 \
  -alias traffic-share
```

### 2. Configure Signing

`android/key.properties` yarating:

```properties
storePassword=your-store-password
keyPassword=your-key-password
keyAlias=traffic-share
storeFile=/path/to/traffic-share-key.jks
```

### 3. Update build.gradle

`android/app/build.gradle`:

```gradle
def keystoreProperties = new Properties()
def keystorePropertiesFile = rootProject.file('key.properties')
if (keystorePropertiesFile.exists()) {
    keystoreProperties.load(new FileInputStream(keystorePropertiesFile))
}

android {
    ...
    
    signingConfigs {
        release {
            keyAlias keystoreProperties['keyAlias']
            keyPassword keystoreProperties['keyPassword']
            storeFile keystoreProperties['storeFile'] ? file(keystoreProperties['storeFile']) : null
            storePassword keystoreProperties['storePassword']
        }
    }
    
    buildTypes {
        release {
            signingConfig signingConfigs.release
        }
    }
}
```

## 🎨 Customize

### App Name

`android/app/src/main/AndroidManifest.xml`:
```xml
android:label="Traffic Share"
```

### App Icon

Icon fayllarni qo'ying:
- `android/app/src/main/res/mipmap-hdpi/ic_launcher.png`
- `android/app/src/main/res/mipmap-mdpi/ic_launcher.png`
- `android/app/src/main/res/mipmap-xhdpi/ic_launcher.png`
- `android/app/src/main/res/mipmap-xxhdpi/ic_launcher.png`
- `android/app/src/main/res/mipmap-xxxhdpi/ic_launcher.png`

### Package Name

`android/app/build.gradle`:
```gradle
defaultConfig {
    applicationId "com.trafficshare.app"
    ...
}
```

## ✅ Test

### Run on Emulator/Device

```bash
flutter run
```

### Run in Release Mode

```bash
flutter run --release
```

## 📤 Distribute

### Option 1: Direct Download

APK ni web serverga upload qiling:
```
https://185.139.230.196/downloads/traffic-share.apk
```

### Option 2: Google Play Store

1. Google Play Developer account yarating
2. AAB (App Bundle) yarating:
   ```bash
   flutter build appbundle --release
   ```
3. Play Console ga upload qiling

## 🐛 Troubleshooting

### Build Failed

```bash
flutter clean
flutter pub get
flutter build apk --release
```

### Network Error

`AndroidManifest.xml` da `usesCleartextTraffic="true"` borligini tekshiring.

### Permission Issues

Kerakli permission'lar `AndroidManifest.xml` da yozilganligini tekshiring.

## 🎯 Quick Build Script

`build_apk.sh` yarating:

```bash
#!/bin/bash

echo "🏗️ Building Traffic Share APK..."

# Clean
flutter clean

# Get dependencies
flutter pub get

# Build release APK
flutter build apk --release --split-per-abi

echo "✅ Build complete!"
echo "📦 APK location: build/app/outputs/flutter-apk/"
ls -lh build/app/outputs/flutter-apk/
```

```bash
chmod +x build_apk.sh
./build_apk.sh
```

---

## 📊 APK Sizes (Approx)

- **Debug APK**: ~40-50 MB
- **Release APK**: ~20-30 MB
- **Split APKs**: ~15-20 MB har biri

## 🚀 Deploy APK

APK tayyor bo'lgandan keyin:

1. VPS ga upload qiling
2. Nginx orqali serve qiling
3. Foydalanuvchilarga link bering

Example nginx config:

```nginx
location /downloads {
    alias /var/www/downloads;
    autoindex on;
}
```

APK link: `http://185.139.230.196/downloads/traffic-share.apk`
