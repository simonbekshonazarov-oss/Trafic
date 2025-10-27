import 'api_client.dart';
import '../utils/constants.dart';

class UserApi {
  final ApiClient _client = ApiClient();

  Future<Map<String, dynamic>> getProfile() async {
    return await _client.get(
      ApiConfig.userMe,
      requireAuth: true,
    );
  }

  Future<Map<String, dynamic>> updateProfile({
    String? phone,
    String? email,
    String? username,
  }) async {
    return await _client.post(
      ApiConfig.userUpdate,
      {
        'phone': phone,
        'email': email,
        'username': username,
      },
      requireAuth: true,
    );
  }

  Future<Map<String, dynamic>> registerDevice({
    required String deviceId,
    String? deviceName,
    required String os,
    String? appVersion,
    String? ip,
  }) async {
    return await _client.post(
      ApiConfig.deviceRegister,
      {
        'device_id': deviceId,
        'device_name': deviceName,
        'os': os,
        'app_version': appVersion,
        'ip': ip,
      },
      requireAuth: true,
    );
  }

  Future<Map<String, dynamic>> getBalance() async {
    return await _client.get(
      ApiConfig.balance,
      requireAuth: true,
    );
  }
}
