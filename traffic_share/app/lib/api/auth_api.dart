import 'package:dio/dio.dart';
import 'api_client.dart';

class AuthApi {
  final ApiClient _apiClient = ApiClient();

  Future<Map<String, dynamic>> register({
    required int telegramId,
    String? username,
    String? phone,
    String? email,
  }) async {
    try {
      final response = await _apiClient.dio.post('/auth/register', data: {
        'telegram_id': telegramId,
        'username': username,
        'phone': phone,
        'email': email,
      });
      return response.data;
    } on DioException catch (e) {
      throw _handleError(e);
    }
  }

  Future<Map<String, dynamic>> requestLoginCode(int telegramId) async {
    try {
      final response = await _apiClient.dio.post('/auth/request_login_code', data: {
        'telegram_id': telegramId,
      });
      return response.data;
    } on DioException catch (e) {
      throw _handleError(e);
    }
  }

  Future<Map<String, dynamic>> verifyCode({
    required int telegramId,
    required String code,
  }) async {
    try {
      final response = await _apiClient.dio.post('/auth/verify_code', data: {
        'telegram_id': telegramId,
        'code': code,
      });
      
      if (response.data['access_token'] != null) {
        await _apiClient.setToken(response.data['access_token']);
      }
      
      return response.data;
    } on DioException catch (e) {
      throw _handleError(e);
    }
  }

  Future<void> logout() async {
    await _apiClient.clearToken();
  }

  String _handleError(DioException e) {
    if (e.response?.data != null) {
      return e.response!.data['message'] ?? 'An error occurred';
    }
    return e.message ?? 'Network error occurred';
  }
}
