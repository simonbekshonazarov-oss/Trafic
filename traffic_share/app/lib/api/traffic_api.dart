import 'package:dio/dio.dart';
import 'package:device_info_plus/device_info_plus.dart';
import 'api_client.dart';

class TrafficApi {
  final ApiClient _apiClient = ApiClient();

  Future<Map<String, dynamic>> registerDevice({
    required String deviceId,
    required String os,
    required String ip,
  }) async {
    try {
      final response = await _apiClient.dio.post('/user/device/register', data: {
        'device_id': deviceId,
        'os': os,
        'ip': ip,
      });
      return response.data;
    } on DioException catch (e) {
      throw _handleError(e);
    }
  }

  Future<Map<String, dynamic>> startTrafficSession({
    required String deviceId,
    required String localIp,
    required String publicIp,
    required String clientVersion,
  }) async {
    try {
      final response = await _apiClient.dio.post('/traffic/start', data: {
        'device_id': deviceId,
        'local_ip': localIp,
        'public_ip': publicIp,
        'client_version': clientVersion,
      });
      return response.data;
    } on DioException catch (e) {
      throw _handleError(e);
    }
  }

  Future<Map<String, dynamic>> updateTraffic({
    required String sessionId,
    required int bytesTx,
    required int bytesRx,
    required int intervalSeconds,
  }) async {
    try {
      final response = await _apiClient.dio.post('/traffic/update', data: {
        'session_id': sessionId,
        'bytes_tx': bytesTx,
        'bytes_rx': bytesRx,
        'interval_seconds': intervalSeconds,
      });
      return response.data;
    } on DioException catch (e) {
      throw _handleError(e);
    }
  }

  Future<Map<String, dynamic>> stopTrafficSession({
    required String sessionId,
    required int finalBytesTx,
    required int finalBytesRx,
  }) async {
    try {
      final response = await _apiClient.dio.post('/traffic/stop', data: {
        'session_id': sessionId,
        'final_bytes_tx': finalBytesTx,
        'final_bytes_rx': finalBytesRx,
      });
      return response.data;
    } on DioException catch (e) {
      throw _handleError(e);
    }
  }

  Future<List<dynamic>> getTrafficHistory() async {
    try {
      final response = await _apiClient.dio.get('/traffic/history');
      return response.data;
    } on DioException catch (e) {
      throw _handleError(e);
    }
  }

  Future<Map<String, dynamic>> getTrafficSummary() async {
    try {
      final response = await _apiClient.dio.get('/traffic/summary');
      return response.data;
    } on DioException catch (e) {
      throw _handleError(e);
    }
  }

  Future<String> getDeviceId() async {
    final deviceInfo = DeviceInfoPlugin();
    if (Platform.isAndroid) {
      final androidInfo = await deviceInfo.androidInfo;
      return androidInfo.id;
    } else if (Platform.isIOS) {
      final iosInfo = await deviceInfo.iosInfo;
      return iosInfo.identifierForVendor ?? 'unknown';
    }
    return 'unknown';
  }

  String _handleError(DioException e) {
    if (e.response?.data != null) {
      return e.response!.data['message'] ?? 'An error occurred';
    }
    return e.message ?? 'Network error occurred';
  }
}
