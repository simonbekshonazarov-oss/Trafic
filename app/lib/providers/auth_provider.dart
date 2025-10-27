import 'package:flutter/material.dart';
import 'package:shared_preferences/shared_preferences.dart';
import '../api/auth_api.dart';
import '../api/user_api.dart';
import '../models/user_model.dart';
import '../utils/constants.dart';

class AuthProvider with ChangeNotifier {
  final AuthApi _authApi = AuthApi();
  final UserApi _userApi = UserApi();

  User? _currentUser;
  bool _isLoading = false;
  String? _error;

  User? get currentUser => _currentUser;
  bool get isLoading => _isLoading;
  String? get error => _error;
  bool get isAuthenticated => _currentUser != null;

  Future<bool> register({
    required int telegramId,
    String? phone,
    String? username,
  }) async {
    try {
      _isLoading = true;
      _error = null;
      notifyListeners();

      await _authApi.register(
        telegramId: telegramId,
        phone: phone,
        username: username,
      );

      _isLoading = false;
      notifyListeners();
      return true;
    } catch (e) {
      _error = e.toString();
      _isLoading = false;
      notifyListeners();
      return false;
    }
  }

  Future<bool> requestLoginCode(int telegramId) async {
    try {
      _isLoading = true;
      _error = null;
      notifyListeners();

      final success = await _authApi.requestLoginCode(telegramId);

      _isLoading = false;
      notifyListeners();
      return success;
    } catch (e) {
      _error = e.toString();
      _isLoading = false;
      notifyListeners();
      return false;
    }
  }

  Future<bool> verifyCode({
    required int telegramId,
    required String code,
  }) async {
    try {
      _isLoading = true;
      _error = null;
      notifyListeners();

      final response = await _authApi.verifyCode(
        telegramId: telegramId,
        code: code,
      );

      // Load user profile
      await loadUserProfile();

      _isLoading = false;
      notifyListeners();
      return true;
    } catch (e) {
      _error = e.toString();
      _isLoading = false;
      notifyListeners();
      return false;
    }
  }

  Future<void> loadUserProfile() async {
    try {
      final userData = await _userApi.getProfile();
      _currentUser = User.fromJson(userData);
      notifyListeners();
    } catch (e) {
      _error = e.toString();
      notifyListeners();
    }
  }

  Future<void> logout() async {
    await _authApi.logout();
    _currentUser = null;
    notifyListeners();
  }

  void clearError() {
    _error = null;
    notifyListeners();
  }
}
