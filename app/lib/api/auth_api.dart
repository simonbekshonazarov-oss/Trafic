import 'api_client.dart';
import '../utils/constants.dart';

class AuthApi {
  final ApiClient _client = ApiClient();

  Future<Map<String, dynamic>> register({
    required int telegramId,
    String? phone,
    String? username,
  }) async {
    return await _client.post(
      ApiConfig.register,
      {
        'telegram_id': telegramId,
        'phone': phone,
        'username': username,
      },
    );
  }

  Future<bool> requestLoginCode(int telegramId) async {
    final response = await _client.post(
      ApiConfig.requestLoginCode,
      {'telegram_id': telegramId},
    );
    return response['ok'] ?? false;
  }

  Future<Map<String, dynamic>> verifyCode({
    required int telegramId,
    required String code,
  }) async {
    final response = await _client.post(
      ApiConfig.verifyCode,
      {
        'telegram_id': telegramId,
        'code': code,
      },
    );

    // Save tokens
    if (response['access_token'] != null) {
      await _client.saveTokens(
        response['access_token'],
        response['refresh_token'],
      );
    }

    return response;
  }

  Future<Map<String, dynamic>> refreshToken(String refreshToken) async {
    final response = await _client.post(
      ApiConfig.refreshToken,
      {'refresh_token': refreshToken},
    );

    // Save new tokens
    if (response['access_token'] != null) {
      await _client.saveTokens(
        response['access_token'],
        response['refresh_token'],
      );
    }

    return response;
  }

  Future<void> logout() async {
    await _client.clearTokens();
  }
}
