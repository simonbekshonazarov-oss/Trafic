import 'package:flutter/material.dart';
import 'package:flutter/foundation.dart';
import '../api/user_api.dart';

class BalanceProvider with ChangeNotifier {
  final UserApi _userApi = UserApi();

  double _available = 0.0;
  double _pending = 0.0;
  double _totalEarned = 0.0;
  bool _isLoading = false;

  double get available => _available;
  double get pending => _pending;
  double get totalEarned => _totalEarned;
  bool get isLoading => _isLoading;
  bool get canWithdraw => _available >= 5.0;

  Future<void> loadBalance() async {
    try {
      _isLoading = true;
      notifyListeners();

      final data = await _userApi.getBalance();

      _available = (data['available'] ?? 0.0).toDouble();
      _pending = (data['pending'] ?? 0.0).toDouble();
      _totalEarned = (data['total_earned'] ?? 0.0).toDouble();

      _isLoading = false;
      notifyListeners();
    } catch (e) {
      _isLoading = false;
      notifyListeners();
      debugPrint('Load balance error: $e');
    }
  }

  void updateFromTraffic(double earnings) {
    _pending += earnings;
    notifyListeners();
  }
}
