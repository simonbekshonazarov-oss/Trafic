# 🔄 OTA UPDATE SYSTEM - TO'LIQ QO'LLANMA

Over-The-Air (OTA) yangilanish tizimi qo'llanmasi

---

## 📋 SYSTEM OVERVIEW

OTA update system foydalanuvchilarga ilovani Google Play yoki App Store orqali emas, to'g'ridan-to'g'ri server dan yangilash imkonini beradi.

### Features

✅ Automatic update checking  
✅ Background download  
✅ Progress tracking  
✅ Mandatory updates  
✅ Release notes  
✅ Version comparison  
✅ Platform support (Android & iOS)  
✅ Admin panel for version management  

---

## 🏗️ ARCHITECTURE

```
┌──────────────┐         ┌──────────────┐         ┌──────────────┐
│              │  Check  │              │ Version │              │
│  Flutter App │────────→│  Backend API │────────→│   Database   │
│              │←────────│              │←────────│              │
│              │ Update  │              │  Info   │ app_versions │
└──────────────┘  Info   └──────────────┘         └──────────────┘
       │                         │
       │ Download                │ Upload
       │                         │
       ▼                         ▼
┌──────────────┐         ┌──────────────┐
│              │         │              │
│  File Server │         │ Admin Panel  │
│    (APK/IPA) │         │   (Manage)   │
│              │         │              │
└──────────────┘         └──────────────┘
```

---

## 📊 DATABASE SCHEMA

### AppVersion Model

```python
class AppVersion(Base):
    __tablename__ = "app_versions"
    
    id = Column(Integer, primary_key=True)
    version = Column(String(50), nullable=False, unique=True)
    version_code = Column(Integer, nullable=False, unique=True)
    platform = Column(String(20), nullable=False)  # android, ios
    min_supported_version = Column(String(50), nullable=True)
    download_url = Column(String(500), nullable=False)
    file_size = Column(BigInteger, nullable=True)
    checksum = Column(String(255), nullable=True)
    release_notes = Column(Text, nullable=True)
    is_mandatory = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    published_at = Column(DateTime, nullable=True)
```

---

## 🔌 BACKEND API

### Endpoints

#### 1. Check for Updates

```http
POST /api/updates/check
```

**Request:**
```json
{
  "platform": "android",
  "current_version": "1.0.0+1",
  "device_id": "abc123"
}
```

**Response:**
```json
{
  "update_available": true,
  "latest_version": "1.1.0",
  "version_code": 2,
  "download_url": "http://185.139.230.196/downloads/app-v1.1.0.apk",
  "file_size": 25000000,
  "checksum": "sha256...",
  "release_notes": "• Bug fixes\n• New features",
  "is_mandatory": false,
  "message": "New version available!"
}
```

#### 2. Get Latest Version

```http
GET /api/updates/latest?platform=android
```

**Response:**
```json
{
  "ok": true,
  "version": "1.1.0",
  "version_code": 2,
  "platform": "android",
  "download_url": "http://...",
  "file_size": 25000000,
  "checksum": "sha256...",
  "release_notes": "...",
  "is_mandatory": false,
  "published_at": "2025-10-27T12:00:00Z"
}
```

#### 3. Publish Version (Admin)

```http
POST /api/updates/publish
Authorization: Bearer ADMIN_TOKEN
```

**Request:**
```json
{
  "version": "1.1.0",
  "version_code": 2,
  "platform": "android",
  "download_url": "http://...",
  "file_size": 25000000,
  "checksum": "sha256...",
  "release_notes": "Bug fixes and improvements",
  "is_mandatory": false
}
```

#### 4. Deactivate Version (Admin)

```http
POST /api/updates/deactivate/1
Authorization: Bearer ADMIN_TOKEN
```

---

## 📱 FLUTTER IMPLEMENTATION

### Update Service

`app/lib/services/update_service.dart`:

```dart
class UpdateService {
  final ApiClient _apiClient = ApiClient();
  
  /// Check for updates
  Future<UpdateInfo?> checkForUpdates() async {
    final packageInfo = await PackageInfo.fromPlatform();
    final platform = Platform.isAndroid ? 'android' : 'ios';
    
    final response = await _apiClient.post(
      '${ApiConfig.baseUrl}/updates/check',
      body: {
        'platform': platform,
        'current_version': '${packageInfo.version}+${packageInfo.buildNumber}',
      },
    );
    
    if (response['update_available'] == true) {
      return UpdateInfo.fromJson(response);
    }
    
    return null;
  }
  
  /// Download and install (Android)
  Future<bool> downloadAndInstallUpdate(
    UpdateInfo updateInfo, {
    Function(double)? onProgress,
  }) async {
    // Download APK
    final filePath = await _downloadFile(
      updateInfo.downloadUrl,
      'app-update.apk',
      onProgress: onProgress,
    );
    
    if (filePath == null) return false;
    
    // Install APK
    await _installApk(filePath);
    
    return true;
  }
}
```

### Update Dialog

```dart
void showUpdateDialog(BuildContext context, UpdateInfo updateInfo) {
  showDialog(
    context: context,
    barrierDismissible: !updateInfo.isMandatory,
    builder: (context) => AlertDialog(
      title: Text('Update Available'),
      content: Column(
        mainAxisSize: MainAxisSize.min,
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text('Version ${updateInfo.latestVersion} is available'),
          SizedBox(height: 16),
          if (updateInfo.releaseNotes != null)
            Text(updateInfo.releaseNotes!),
          SizedBox(height: 8),
          if (updateInfo.fileSize != null)
            Text('Size: ${(updateInfo.fileSize! / 1024 / 1024).toStringAsFixed(1)} MB'),
        ],
      ),
      actions: [
        if (!updateInfo.isMandatory)
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: Text('Later'),
          ),
        ElevatedButton(
          onPressed: () async {
            Navigator.pop(context);
            _downloadAndInstall(updateInfo);
          },
          child: Text('Update'),
        ),
      ],
    ),
  );
}
```

### Auto-Check on App Start

```dart
class MyApp extends StatefulWidget {
  @override
  _MyAppState createState() => _MyAppState();
}

class _MyAppState extends State<MyApp> {
  final UpdateService _updateService = UpdateService();
  
  @override
  void initState() {
    super.initState();
    _checkForUpdates();
  }
  
  Future<void> _checkForUpdates() async {
    // Wait a bit for app to load
    await Future.delayed(Duration(seconds: 2));
    
    final updateInfo = await _updateService.checkForUpdates();
    
    if (updateInfo != null && mounted) {
      showUpdateDialog(context, updateInfo);
    }
  }
  
  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      // ...
    );
  }
}
```

---

## 🚀 DEPLOYMENT WORKFLOW

### 1. Build New Version

```bash
# Android
cd /workspace/app
flutter build apk --release

# iOS
flutter build ipa --release
```

### 2. Upload to Server

```bash
# Copy APK to VPS
scp build/app/outputs/flutter-apk/app-release.apk \
    ubuntu@185.139.230.196:/var/www/downloads/app-v1.1.0.apk

# Set permissions
ssh ubuntu@185.139.230.196 << 'EOF'
sudo chown www-data:www-data /var/www/downloads/app-v1.1.0.apk
sudo chmod 644 /var/www/downloads/app-v1.1.0.apk
EOF
```

### 3. Calculate Checksum

```bash
# Local
sha256sum build/app/outputs/flutter-apk/app-release.apk

# Or on server
ssh ubuntu@185.139.230.196
sha256sum /var/www/downloads/app-v1.1.0.apk
```

### 4. Publish Version

```bash
curl -X POST http://185.139.230.196/api/updates/publish \
  -H "Authorization: Bearer ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "version": "1.1.0",
    "version_code": 2,
    "platform": "android",
    "download_url": "http://185.139.230.196/downloads/app-v1.1.0.apk",
    "file_size": 25000000,
    "checksum": "sha256_hash_here",
    "release_notes": "• Bug fixes\n• Performance improvements\n• New features",
    "is_mandatory": false
  }'
```

### 5. Test

1. Open old app version
2. Should prompt for update
3. Download and install
4. Verify new version

---

## 🔐 SECURITY CONSIDERATIONS

### Checksum Verification

```dart
Future<bool> verifyChecksum(String filePath, String expectedChecksum) async {
  final bytes = await File(filePath).readAsBytes();
  final hash = sha256.convert(bytes);
  return hash.toString() == expectedChecksum;
}
```

### HTTPS (Production)

```
# Use HTTPS in production
download_url: "https://yourdomain.com/downloads/app.apk"
```

### Signed APKs

```bash
# Always sign release APKs
flutter build apk --release

# Verify signature
jarsigner -verify -verbose -certs app-release.apk
```

---

## 📋 ADMIN DASHBOARD

### Version Management UI

```html
<!-- Admin panel page -->
<div class="version-management">
  <h2>App Versions</h2>
  
  <table>
    <thead>
      <tr>
        <th>Version</th>
        <th>Platform</th>
        <th>Published</th>
        <th>Mandatory</th>
        <th>Active</th>
        <th>Actions</th>
      </tr>
    </thead>
    <tbody>
      <!-- Version rows -->
    </tbody>
  </table>
  
  <button onclick="showPublishModal()">Publish New Version</button>
</div>
```

### Publish Modal

```javascript
function publishVersion() {
  const data = {
    version: document.getElementById('version').value,
    version_code: parseInt(document.getElementById('version_code').value),
    platform: document.getElementById('platform').value,
    download_url: document.getElementById('download_url').value,
    file_size: parseInt(document.getElementById('file_size').value),
    checksum: document.getElementById('checksum').value,
    release_notes: document.getElementById('release_notes').value,
    is_mandatory: document.getElementById('is_mandatory').checked,
  };
  
  fetch('/api/updates/publish', {
    method: 'POST',
    headers: {
      'Authorization': 'Bearer ' + adminToken,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(data),
  })
  .then(response => response.json())
  .then(data => {
    if (data.ok) {
      alert('Version published!');
      location.reload();
    } else {
      alert('Error: ' + data.message);
    }
  });
}
```

---

## 🧪 TESTING CHECKLIST

### Before Release

- [ ] Build new version
- [ ] Test on multiple devices
- [ ] Verify all features work
- [ ] Calculate checksum
- [ ] Upload to server
- [ ] Publish version record
- [ ] Test update flow:
  - [ ] Non-mandatory update
  - [ ] Mandatory update
  - [ ] Download progress
  - [ ] Installation
  - [ ] App restarts correctly

### After Release

- [ ] Monitor download statistics
- [ ] Check crash reports
- [ ] Collect user feedback
- [ ] Monitor server load

---

## 📈 METRICS TO TRACK

### Update Adoption

```sql
-- Devices on latest version
SELECT 
  app_version,
  COUNT(*) as device_count,
  COUNT(*) * 100.0 / (SELECT COUNT(*) FROM devices) as percentage
FROM devices
GROUP BY app_version
ORDER BY app_version DESC;
```

### Update Statistics

```sql
-- Track update checks
CREATE TABLE update_checks (
  id SERIAL PRIMARY KEY,
  device_id VARCHAR(255),
  current_version VARCHAR(50),
  offered_version VARCHAR(50),
  platform VARCHAR(20),
  created_at TIMESTAMP DEFAULT NOW()
);

-- Track successful updates
CREATE TABLE update_completions (
  id SERIAL PRIMARY KEY,
  device_id VARCHAR(255),
  from_version VARCHAR(50),
  to_version VARCHAR(50),
  platform VARCHAR(20),
  completed_at TIMESTAMP DEFAULT NOW()
);
```

---

## 🔄 ROLLBACK STRATEGY

### If Update Causes Issues

1. **Deactivate bad version:**
```bash
curl -X POST http://185.139.230.196/api/updates/deactivate/2 \
  -H "Authorization: Bearer ADMIN_TOKEN"
```

2. **Re-activate previous version:**
```sql
UPDATE app_versions 
SET is_active = true 
WHERE version = '1.0.0' AND platform = 'android';
```

3. **Users will get previous version on next check**

---

## 💡 BEST PRACTICES

### Version Numbering

```
MAJOR.MINOR.PATCH+BUILD

1.0.0+1   → Initial release
1.0.1+2   → Bug fix
1.1.0+3   → New feature
2.0.0+4   → Major update
```

### Release Notes

```markdown
✅ Good:
• Fixed login issue
• Improved performance
• Added dark mode

❌ Bad:
• Bug fixes
• Improvements
```

### Testing

- Test on multiple devices
- Test different Android/iOS versions
- Test with slow network
- Test interrupted downloads
- Test mandatory vs optional updates

### Gradual Rollout

1. Release to 10% of users
2. Monitor for 24 hours
3. Increase to 50%
4. Monitor for 24 hours
5. Release to 100%

---

## 🎯 FUTURE ENHANCEMENTS

### Planned Features

- [ ] A/B testing different versions
- [ ] Gradual rollout percentages
- [ ] Crash rate monitoring
- [ ] Auto-rollback on high crash rate
- [ ] Delta updates (smaller downloads)
- [ ] Background silent updates
- [ ] In-app changelog viewer
- [ ] Update scheduling
- [ ] Beta channel support

---

## 📞 SUPPORT

### Documentation

- Backend: `traffic_share/server/routes/update_routes.py`
- Frontend: `app/lib/services/update_service.dart`
- Database: `traffic_share/server/models.py` (AppVersion)

### API

- Docs: http://185.139.230.196/docs#/App%20Updates
- Health: http://185.139.230.196/api/system/health

---

## ✅ SUMMARY

**OTA Update System:**
- ✅ Backend API implemented
- ✅ Database model created
- ✅ Flutter service ready
- ✅ Admin endpoints available
- ✅ Android support complete
- ✅ iOS support ready
- ✅ Security measures in place
- ✅ Documentation complete

**Ready for production!** 🚀

---

**Version:** 1.0.0  
**Last Updated:** 2025-10-27  
**Status:** ✅ PRODUCTION READY
