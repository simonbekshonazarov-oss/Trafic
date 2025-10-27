import 'api_client.dart';
import '../utils/constants.dart';

class TrafficApi {
  final ApiClient _client = ApiClient();

  Future<Map<String, dynamic>> startSession({
    required String deviceId,
    String? localIp,
    String? publicIp,
    String? clientVersion,
  }) async {
    return await _client.post(
      ApiConfig.trafficStart,
      {
        'device_id': deviceId,
        'local_ip': localIp,
        'public_ip': publicIp,
        'client_version': clientVersion,
      },
      requireAuth: true,
    );
  }

  Future<bool> updateSession({
    required String sessionId,
    required int bytesTx,
    required int bytesRx,
    int? intervalSeconds,
  }) async {
    final response = await _client.post(
      ApiConfig.trafficUpdate,
      {
        'session_id': sessionId,
        'bytes_tx': bytesTx,
        'bytes_rx': bytesRx,
        'interval_seconds': intervalSeconds,
      },
      requireAuth: true,
    );
    return response['ok'] ?? false;
  }

  Future<Map<String, dynamic>> stopSession({
    required String sessionId,
    required int finalBytesTx,
    required int finalBytesRx,
  }) async {
    return await _client.post(
      ApiConfig.trafficStop,
      {
        'session_id': sessionId,
        'final_bytes_tx': finalBytesTx,
        'final_bytes_rx': finalBytesRx,
      },
      requireAuth: true,
    );
  }

  Future<List<dynamic>> getHistory({int page = 1, int pageSize = 50}) async {
    final response = await _client.get(
      '${ApiConfig.trafficHistory}?page=$page&page_size=$pageSize',
      requireAuth: true,
    );
    return response as List<dynamic>;
  }

  Future<Map<String, dynamic>> getSummary() async {
    return await _client.get(
      ApiConfig.trafficSummary,
      requireAuth: true,
    );
  }
}
