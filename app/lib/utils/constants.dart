import 'package:flutter/material.dart';

// API Configuration
class ApiConfig {
  // VPS IP yoki domain
  static const String baseUrl = 'http://185.139.230.196/api';
  
  // Endpoints
  static const String register = '/auth/register';
  static const String requestLoginCode = '/auth/request_login_code';
  static const String verifyCode = '/auth/verify_code';
  static const String refreshToken = '/auth/refresh';
  
  static const String userMe = '/user/me';
  static const String userUpdate = '/user/update';
  static const String deviceRegister = '/user/device/register';
  
  static const String trafficStart = '/traffic/start';
  static const String trafficUpdate = '/traffic/update';
  static const String trafficStop = '/traffic/stop';
  static const String trafficHistory = '/traffic/history';
  static const String trafficSummary = '/traffic/summary';
  
  static const String balance = '/balance';
  static const String withdrawRequest = '/withdraw/request';
  static const String withdrawStatus = '/withdraw/status';
}

// App Colors
class AppColors {
  static const Color primary = Color(0xFF2196F3);
  static const Color secondary = Color(0xFF00BCD4);
  static const Color accent = Color(0xFF4CAF50);
  static const Color error = Color(0xFFF44336);
  static const Color warning = Color(0xFFFF9800);
  static const Color success = Color(0xFF4CAF50);
  
  static const Color background = Color(0xFFF5F5F5);
  static const Color surface = Color(0xFFFFFFFF);
  static const Color textPrimary = Color(0xFF212121);
  static const Color textSecondary = Color(0xFF757575);
}

// App Constants
class AppConstants {
  static const String appName = 'Traffic Share';
  static const String appVersion = '1.0.0';
  
  static const double pricePerGB = 0.50;
  static const double minWithdrawal = 5.0;
  
  // SharedPreferences Keys
  static const String keyAccessToken = 'access_token';
  static const String keyRefreshToken = 'refresh_token';
  static const String keyUserId = 'user_id';
  static const String keyTelegramId = 'telegram_id';
  static const String keyDeviceId = 'device_id';
}

// Traffic Status
enum TrafficStatus {
  inactive,
  starting,
  active,
  stopping,
  error,
}

// Payment Status
enum PaymentStatus {
  pending,
  processing,
  completed,
  failed,
}
