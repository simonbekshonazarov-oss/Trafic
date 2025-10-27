# 🍎 iOS APP BUILD GUIDE

Traffic Share loyihasi uchun iOS ilovasi yaratish qo'llanmasi.

---

## 📋 PREREQUISITES

### 1. macOS Computer
- macOS 12.0 (Monterey) yoki yuqori
- Xcode 14.0+
- CocoaPods

### 2. Apple Developer Account
- Apple Developer Program ($99/year)
- Developer certificate
- Provisioning profile

### 3. Flutter Setup
```bash
# Flutter SDK
flutter doctor

# iOS toolchain check
flutter doctor --verbose | grep iOS
```

---

## 🔧 INITIAL SETUP

### 1. Open iOS Project

```bash
cd /workspace/app
flutter pub get

# Open iOS project in Xcode
open ios/Runner.xcworkspace
```

### 2. Bundle Identifier

Xcode da:
1. **Runner** → **Signing & Capabilities**
2. **Bundle Identifier**: `com.trafficshare.app`
3. **Team**: Sizning Apple Developer team

### 3. App Info

**ios/Runner/Info.plist**:

```xml
<key>CFBundleName</key>
<string>Traffic Share</string>

<key>CFBundleDisplayName</key>
<string>Traffic Share</string>

<key>CFBundleIdentifier</key>
<string>$(PRODUCT_BUNDLE_IDENTIFIER)</string>

<key>CFBundleVersion</key>
<string>1</string>

<key>CFBundleShortVersionString</key>
<string>1.0.0</string>

<!-- Permissions -->
<key>NSPhotoLibraryUsageDescription</key>
<string>Traffic Share needs access to your photos</string>

<key>NSCameraUsageDescription</key>
<string>Traffic Share needs access to your camera</string>

<key>NSLocationWhenInUseUsageDescription</key>
<string>Traffic Share needs your location for traffic sharing</string>

<!-- HTTP requests (if needed) -->
<key>NSAppTransportSecurity</key>
<dict>
    <key>NSAllowsArbitraryLoads</key>
    <true/>
    <key>NSExceptionDomains</key>
    <dict>
        <key>185.139.230.196</key>
        <dict>
            <key>NSExceptionAllowsInsecureHTTPLoads</key>
            <true/>
            <key>NSIncludesSubdomains</key>
            <true/>
        </dict>
    </dict>
</dict>
```

---

## 🛠️ BUILD FOR DEVICE

### 1. Connect Device
- iOS device via USB
- Enable Developer Mode on device
- Trust computer

### 2. Select Target
Xcode:
- Product → Destination → Your iPhone

### 3. Build
```bash
# Via Xcode
Product → Build (⌘B)

# Via Flutter
flutter build ios --release
```

---

## 📦 CREATE IPA

### 1. Archive

Xcode:
- Product → Archive
- Wait for build to complete

### 2. Export

1. Window → Organizer
2. Select archive
3. **Distribute App**
4. Choose method:
   - **App Store Connect** (production)
   - **Ad Hoc** (testing)
   - **Enterprise** (internal)
   - **Development** (debug)

### 3. Select Options

- **App Thinning:** All compatible devices
- **Rebuild from Bitcode:** Yes
- **Strip Swift symbols:** Yes
- **Include manifest:** For Ad Hoc

### 4. Export IPA

- Choose destination folder
- Wait for export
- IPA file ready!

---

## 🚀 DISTRIBUTION

### Option 1: TestFlight (Recommended)

1. **Upload to App Store Connect**
   - Xcode → Organizer → Upload
   - Or use Transporter app

2. **Configure TestFlight**
   - App Store Connect → My Apps
   - Select app → TestFlight
   - Add internal/external testers
   - Provide test information

3. **Share Link**
   - Get TestFlight link
   - Send to testers
   - They install via TestFlight app

### Option 2: Ad Hoc Distribution

1. **Register Devices**
   - Get UDIDs
   - Add to Apple Developer Portal
   - Regenerate provisioning profile

2. **Build Ad Hoc**
   - Export with Ad Hoc method
   - Include manifest.plist

3. **Distribute**
   - Upload IPA to server
   - Create installation link
   - Users install via Safari

### Option 3: App Store

1. **Prepare App**
   - App Store Connect → My Apps
   - Create new app
   - Fill all metadata:
     - App name
     - Description
     - Screenshots (required)
     - App icon (1024x1024)
     - Privacy policy URL
     - Support URL
     - Keywords
     - Category

2. **Upload Build**
   - Xcode → Archive → Upload
   - Wait for processing

3. **Submit for Review**
   - Select build version
   - Add reviewer notes
   - Submit

4. **Review Process**
   - 1-3 days typically
   - Respond to any questions
   - Once approved, release!

---

## 🔧 COMMON ISSUES & FIXES

### Issue 1: Signing Failed

**Error:** "No signing certificate found"

**Fix:**
```
1. Xcode → Preferences → Accounts
2. Select your Apple ID
3. Download Manual Profiles
4. Or let Xcode manage signing automatically
```

### Issue 2: Pod Install Failed

**Error:** "CocoaPods not installed"

**Fix:**
```bash
sudo gem install cocoapods
cd ios
pod install
```

### Issue 3: Build Failed

**Error:** Various build errors

**Fix:**
```bash
# Clean
flutter clean
cd ios
rm -rf Pods Podfile.lock
pod install
cd ..
flutter pub get
flutter build ios
```

### Issue 4: API Connection

**Error:** "Connection refused"

**Fix:**
- Check Info.plist NSAppTransportSecurity
- Verify API URL in constants.dart
- Test API from browser first

---

## 📱 REQUIRED ASSETS

### App Icon

**Sizes needed:**
- 1024x1024 (App Store)
- 180x180 (@3x)
- 167x167 (@2x iPad Pro)
- 152x152 (@2x iPad)
- 120x120 (@2x iPhone)
- 87x87 (@3x)
- 80x80 (@2x)
- 76x76 (@1x iPad)
- 58x58 (@2x)
- 40x40 (@1x)
- 29x29 (@1x)

**Create with:**
```bash
# Use icon generator tools
# Or provide single 1024x1024 and let Xcode resize
```

### Screenshots

**Required sizes:**
- iPhone 6.7" (1290x2796) - 3 images
- iPhone 6.5" (1284x2778) - 3 images  
- iPhone 5.5" (1242x2208) - 3 images
- iPad Pro 12.9" (2048x2732) - 3 images
- iPad Pro 11" (1668x2388) - 3 images

---

## 🎨 FLUTTER IOS CONFIG

### pubspec.yaml

```yaml
name: traffic_share
description: Traffic Share mobile app

version: 1.0.0+1

environment:
  sdk: '>=3.0.0 <4.0.0'

dependencies:
  flutter:
    sdk: flutter
  
  # Existing dependencies...
  
  # iOS specific (if needed)
  flutter_local_notifications: ^16.0.0
  
flutter:
  uses-material-design: true
  
  # Assets
  assets:
    - assets/images/
    - assets/icons/
```

### ios/Runner/Info.plist (Complete)

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleDevelopmentRegion</key>
    <string>$(DEVELOPMENT_LANGUAGE)</string>
    <key>CFBundleDisplayName</key>
    <string>Traffic Share</string>
    <key>CFBundleExecutable</key>
    <string>$(EXECUTABLE_NAME)</string>
    <key>CFBundleIdentifier</key>
    <string>$(PRODUCT_BUNDLE_IDENTIFIER)</string>
    <key>CFBundleInfoDictionaryVersion</key>
    <string>6.0</string>
    <key>CFBundleName</key>
    <string>Traffic Share</string>
    <key>CFBundlePackageType</key>
    <string>APPL</string>
    <key>CFBundleShortVersionString</key>
    <string>$(FLUTTER_BUILD_NAME)</string>
    <key>CFBundleSignature</key>
    <string>????</string>
    <key>CFBundleVersion</key>
    <string>$(FLUTTER_BUILD_NUMBER)</string>
    <key>LSRequiresIPhoneOS</key>
    <true/>
    <key>UILaunchStoryboardName</key>
    <string>LaunchScreen</string>
    <key>UIMainStoryboardFile</key>
    <string>Main</string>
    <key>UISupportedInterfaceOrientations</key>
    <array>
        <string>UIInterfaceOrientationPortrait</string>
    </array>
    <key>UISupportedInterfaceOrientations~ipad</key>
    <array>
        <string>UIInterfaceOrientationPortrait</string>
        <string>UIInterfaceOrientationLandscapeLeft</string>
        <string>UIInterfaceOrientationLandscapeRight</string>
    </array>
    <key>UIViewControllerBasedStatusBarAppearance</key>
    <false/>
    <key>CADisableMinimumFrameDurationOnPhone</key>
    <true/>
    <key>UIApplicationSupportsIndirectInputEvents</key>
    <true/>
    
    <!-- Permissions -->
    <key>NSLocationWhenInUseUsageDescription</key>
    <string>Traffic Share needs your location for traffic sharing</string>
    <key>NSPhotoLibraryUsageDescription</key>
    <string>Upload photos for profile</string>
    <key>NSCameraUsageDescription</key>
    <string>Take photos for profile</string>
    
    <!-- Network -->
    <key>NSAppTransportSecurity</key>
    <dict>
        <key>NSAllowsArbitraryLoads</key>
        <true/>
        <key>NSExceptionDomains</key>
        <dict>
            <key>185.139.230.196</key>
            <dict>
                <key>NSExceptionAllowsInsecureHTTPLoads</key>
                <true/>
                <key>NSIncludesSubdomains</key>
                <true/>
            </dict>
        </dict>
    </dict>
</dict>
</plist>
```

---

## 🔐 CODE SIGNING

### Automatic Signing (Recommended)

1. Xcode → Target → Signing & Capabilities
2. ✅ Automatically manage signing
3. Select Team
4. Xcode handles certificates and profiles

### Manual Signing

1. Create certificates in Apple Developer Portal
2. Download provisioning profiles
3. Xcode → Target → Signing & Capabilities
4. ❌ Automatically manage signing
5. Select profiles manually

---

## 📊 BUILD SETTINGS

### Key Settings

**Runner Target:**
- **Deployment Target:** iOS 12.0+
- **Supported Devices:** iPhone, iPad
- **Architectures:** arm64, arm64e
- **Build Active Architecture Only:** NO (Release)

**Build Phases:**
- Run Script: Embed Flutter
- Compile Sources
- Link Binary with Libraries
- Embed Frameworks
- Copy Bundle Resources

---

## 🧪 TESTING

### Local Testing

```bash
# iOS Simulator
flutter run

# Physical device
flutter run --release
```

### TestFlight Testing

1. Upload build
2. Add testers
3. Distribute
4. Collect feedback
5. Fix issues
6. Update build

---

## 📈 APP STORE OPTIMIZATION

### Metadata

**App Name:** Traffic Share (max 30 chars)

**Subtitle:** Earn money sharing internet (max 30 chars)

**Keywords:** traffic,share,earn,money,internet,vpn (max 100 chars)

**Description:**
```
Traffic Share lets you earn money by sharing your unused internet bandwidth.

FEATURES:
• Easy Telegram login
• Real-time earnings tracking
• Secure payments via Cryptomus
• Automatic traffic management
• Detailed statistics
• Fast withdrawals

HOW IT WORKS:
1. Install and login with Telegram
2. Start sharing your traffic
3. Watch your balance grow
4. Withdraw earnings anytime

SECURE & PRIVATE:
• Bank-level encryption
• No personal data collected
• Transparent earnings calculation

Start earning today with Traffic Share!
```

**Privacy Policy:** Required URL

**Support URL:** Required URL

---

## ✅ PRE-SUBMISSION CHECKLIST

### Technical
- [ ] App builds without errors
- [ ] All features working on device
- [ ] No crashes
- [ ] API connections working
- [ ] Payment flow tested
- [ ] Permissions handled properly
- [ ] Push notifications (if any)
- [ ] Background tasks working

### Assets
- [ ] App icon (all sizes)
- [ ] Screenshots (all sizes)
- [ ] Preview video (optional)

### Metadata
- [ ] App name
- [ ] Description
- [ ] Keywords
- [ ] Privacy policy URL
- [ ] Support URL
- [ ] Copyright
- [ ] Age rating
- [ ] Category

### Legal
- [ ] Terms of service
- [ ] Privacy policy
- [ ] GDPR compliance (if EU users)
- [ ] Export compliance

---

## 🚀 RELEASE STRATEGY

### Version 1.0.0 (Initial)
- Basic features
- TestFlight beta (2-4 weeks)
- Collect feedback
- Fix critical bugs

### Version 1.1.0
- OTA update testing
- New features based on feedback
- Performance improvements

### Ongoing
- Regular updates
- Bug fixes
- Feature enhancements
- iOS version compatibility

---

## 📞 SUPPORT

### Apple Developer
- https://developer.apple.com
- https://developer.apple.com/support

### Flutter iOS
- https://docs.flutter.dev/deployment/ios
- https://flutter.dev/docs/get-started/install/macos

### App Store Connect
- https://appstoreconnect.apple.com
- https://developer.apple.com/app-store-connect

---

## 🎯 SUCCESS METRICS

Track:
- Downloads
- Active users
- Crash rate (target: <1%)
- Rating (target: 4.5+)
- Review responses
- Update adoption rate

---

## 🎉 LAUNCH!

1. ✅ Build app
2. ✅ Test thoroughly
3. ✅ Submit to App Store
4. ✅ Pass review
5. ✅ Release
6. ✅ Monitor metrics
7. ✅ Respond to reviews
8. ✅ Plan updates

**Omad!** 🚀

---

**Version:** 1.0.0  
**Last Updated:** 2025-10-27  
**Status:** ✅ READY FOR iOS BUILD
