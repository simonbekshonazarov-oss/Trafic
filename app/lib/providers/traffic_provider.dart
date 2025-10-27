import 'dart:async';
import 'package:flutter/material.dart';
import 'package:device_info_plus/device_info_plus.dart';
import 'package:network_info_plus/network_info_plus.dart';
import '../api/traffic_api.dart';
import '../models/traffic_model.dart';
import '../utils/constants.dart';

class TrafficProvider with ChangeNotifier {
  final TrafficApi _trafficApi = TrafficApi();

  TrafficStatus _status = TrafficStatus.inactive;
  String? _sessionId;
  int _bytesTx = 0;
  int _bytesRx = 0;
  double _currentEarnings = 0.0;
  Timer? _updateTimer;
  TrafficSummary? _summary;
  List<TrafficSession> _history = [];

  TrafficStatus get status => _status;
  String? get sessionId => _sessionId;
  int get bytesTx => _bytesTx;
  int get bytesRx => _bytesRx;
  int get bytesTotal => _bytesTx + _bytesRx;
  double get currentEarnings => _currentEarnings;
  double get totalGB => bytesTotal / (1024 * 1024 * 1024);
  TrafficSummary? get summary => _summary;
  List<TrafficSession> get history => _history;

  Future<bool> startSharing() async {
    try {
      _status = TrafficStatus.starting;
      notifyListeners();

      // Get device info
      final deviceInfo = DeviceInfoPlugin();
      final androidInfo = await deviceInfo.androidInfo;
      final deviceId = androidInfo.id;

      // Get network info
      final networkInfo = NetworkInfo();
      final wifiIP = await networkInfo.getWifiIP();

      // Start session
      final response = await _trafficApi.startSession(
        deviceId: deviceId,
        localIp: wifiIP,
        publicIp: wifiIP,
        clientVersion: AppConstants.appVersion,
      );

      _sessionId = response['session_id'];
      _status = TrafficStatus.active;
      _bytesTx = 0;
      _bytesRx = 0;
      _currentEarnings = 0.0;

      // Start update timer (every 10 seconds)
      _startUpdateTimer();

      notifyListeners();
      return true;
    } catch (e) {
      _status = TrafficStatus.error;
      notifyListeners();
      return false;
    }
  }

  void _startUpdateTimer() {
    _updateTimer?.cancel();
    _updateTimer = Timer.periodic(const Duration(seconds: 10), (timer) {
      _updateSession();
    });
  }

  Future<void> _updateSession() async {
    if (_sessionId == null || _status != TrafficStatus.active) return;

    try {
      // Simulate traffic (in real app, measure actual traffic)
      final newBytesTx = _simulateTraffic();
      final newBytesRx = _simulateTraffic();

      await _trafficApi.updateSession(
        sessionId: _sessionId!,
        bytesTx: newBytesTx,
        bytesRx: newBytesRx,
        intervalSeconds: 10,
      );

      _bytesTx += newBytesTx;
      _bytesRx += newBytesRx;
      _currentEarnings = totalGB * AppConstants.pricePerGB;

      notifyListeners();
    } catch (e) {
      // Handle error
      print('Update session error: $e');
    }
  }

  int _simulateTraffic() {
    // Simulate random traffic (1-10 MB per 10 seconds)
    // In real app, measure actual network traffic
    return (1 + (9 * (DateTime.now().millisecond / 1000))).toInt() * 1024 * 1024;
  }

  Future<bool> stopSharing() async {
    try {
      _status = TrafficStatus.stopping;
      notifyListeners();

      _updateTimer?.cancel();

      if (_sessionId != null) {
        final response = await _trafficApi.stopSession(
          sessionId: _sessionId!,
          finalBytesTx: _bytesTx,
          finalBytesRx: _bytesRx,
        );

        _currentEarnings = response['earnings'] ?? _currentEarnings;
      }

      _status = TrafficStatus.inactive;
      _sessionId = null;

      notifyListeners();
      return true;
    } catch (e) {
      _status = TrafficStatus.error;
      notifyListeners();
      return false;
    }
  }

  Future<void> loadSummary() async {
    try {
      final data = await _trafficApi.getSummary();
      _summary = TrafficSummary.fromJson(data);
      notifyListeners();
    } catch (e) {
      print('Load summary error: $e');
    }
  }

  Future<void> loadHistory() async {
    try {
      final data = await _trafficApi.getHistory();
      _history = data.map((json) => TrafficSession.fromJson(json)).toList();
      notifyListeners();
    } catch (e) {
      print('Load history error: $e');
    }
  }

  @override
  void dispose() {
    _updateTimer?.cancel();
    super.dispose();
  }
}
