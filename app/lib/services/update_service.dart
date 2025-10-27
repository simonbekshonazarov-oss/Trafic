import 'dart:io';
import 'package:http/http.dart' as http;
import 'package:package_info_plus/package_info_plus.dart';
import 'package:path_provider/path_provider.dart';
import 'package:flutter/foundation.dart';
import '../api/api_client.dart';
import '../utils/constants.dart';

class UpdateService {
  final ApiClient _apiClient = ApiClient();
  
  /// Check for app updates
  Future<UpdateInfo?> checkForUpdates() async {
    try {
      final packageInfo = await PackageInfo.fromPlatform();
      final platform = Platform.isAndroid ? 'android' : 'ios';
      
      final response = await _apiClient.post(
        '${ApiConfig.baseUrl}/updates/check',
        body: {
          'platform': platform,
          'current_version': '${packageInfo.version}+${packageInfo.buildNumber}',
          'device_id': await _getDeviceId(),
        },
      );
      
      if (response['update_available'] == true) {
        return UpdateInfo.fromJson(response);
      }
      
      return null;
    } catch (e) {
      debugPrint('Check update error: $e');
      return null;
    }
  }
  
  /// Download and install update (Android)
  Future<bool> downloadAndInstallUpdate(UpdateInfo updateInfo, {
    Function(double)? onProgress,
  }) async {
    if (!Platform.isAndroid) {
      // iOS updates go through App Store
      return false;
    }
    
    try {
      // Download APK
      final filePath = await _downloadFile(
        updateInfo.downloadUrl,
        'app-update.apk',
        onProgress: onProgress,
      );
      
      if (filePath == null) {
        return false;
      }
      
      // Install APK (requires permission)
      await _installApk(filePath);
      
      return true;
    } catch (e) {
      debugPrint('Download/install error: $e');
      return false;
    }
  }
  
  /// Download file with progress
  Future<String?> _downloadFile(
    String url,
    String filename, {
    Function(double)? onProgress,
  }) async {
    try {
      final dir = await getTemporaryDirectory();
      final file = File('${dir.path}/$filename');
      
      final request = await http.Client().send(http.Request('GET', Uri.parse(url)));
      final total = request.contentLength ?? 0;
      var downloaded = 0;
      
      final sink = file.openWrite();
      
      await for (var chunk in request.stream) {
        sink.add(chunk);
        downloaded += chunk.length;
        
        if (onProgress != null && total > 0) {
          onProgress(downloaded / total);
        }
      }
      
      await sink.close();
      
      return file.path;
    } catch (e) {
      debugPrint('Download file error: $e');
      return null;
    }
  }
  
  /// Install APK (Android only)
  Future<void> _installApk(String filePath) async {
    // Implementation depends on package: install_plugin or open_file
    // This is a placeholder
    throw UnimplementedError('APK installation requires platform-specific implementation');
  }
  
  /// Get device ID
  Future<String> _getDeviceId() async {
    // Implementation depends on device_info_plus or similar package
    return 'device_id_placeholder';
  }
  
  /// Open app store for update (iOS)
  void openAppStore() {
    // Implementation for iOS App Store link
  }
}

class UpdateInfo {
  final bool updateAvailable;
  final String? latestVersion;
  final int? versionCode;
  final String downloadUrl;
  final int? fileSize;
  final String? checksum;
  final String? releaseNotes;
  final bool isMandatory;
  final String message;
  
  UpdateInfo({
    required this.updateAvailable,
    this.latestVersion,
    this.versionCode,
    required this.downloadUrl,
    this.fileSize,
    this.checksum,
    this.releaseNotes,
    this.isMandatory = false,
    required this.message,
  });
  
  factory UpdateInfo.fromJson(Map<String, dynamic> json) {
    return UpdateInfo(
      updateAvailable: json['update_available'] ?? false,
      latestVersion: json['latest_version'],
      versionCode: json['version_code'],
      downloadUrl: json['download_url'] ?? '',
      fileSize: json['file_size'],
      checksum: json['checksum'],
      releaseNotes: json['release_notes'],
      isMandatory: json['is_mandatory'] ?? false,
      message: json['message'] ?? '',
    );
  }
}
