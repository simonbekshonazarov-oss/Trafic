import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import '../api/api_client.dart';
import '../api/auth_api.dart';

class LoginScreen extends StatefulWidget {
  @override
  _LoginScreenState createState() => _LoginScreenState();
}

class _LoginScreenState extends State<LoginScreen> {
  final _telegramIdController = TextEditingController();
  final _codeController = TextEditingController();
  bool _isLoading = false;
  String _message = '';
  final AuthApi _authApi = AuthApi();
  final ApiClient _apiClient = ApiClient();

  @override
  void initState() {
    super.initState();
    _apiClient.init();
    _checkExistingToken();
  }

  Future<void> _checkExistingToken() async {
    await _apiClient.loadToken();
    if (_apiClient._accessToken != null) {
      Navigator.pushReplacementNamed(context, '/home');
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text('Traffic Share'),
        centerTitle: true,
      ),
      body: Padding(
        padding: EdgeInsets.all(16.0),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(
              Icons.wifi_tethering,
              size: 80,
              color: Colors.blue,
            ),
            SizedBox(height: 20),
            Text(
              'Welcome to Traffic Share',
              style: TextStyle(
                fontSize: 24,
                fontWeight: FontWeight.bold,
              ),
            ),
            SizedBox(height: 10),
            Text(
              'Share your internet traffic and earn money',
              style: TextStyle(
                fontSize: 16,
                color: Colors.grey[600],
              ),
            ),
            SizedBox(height: 40),
            TextField(
              controller: _telegramIdController,
              decoration: InputDecoration(
                labelText: 'Telegram ID',
                border: OutlineInputBorder(),
                prefixIcon: Icon(Icons.person),
              ),
              keyboardType: TextInputType.number,
            ),
            SizedBox(height: 20),
            ElevatedButton(
              onPressed: _isLoading ? null : _requestLoginCode,
              child: _isLoading
                  ? CircularProgressIndicator()
                  : Text('Request Login Code'),
              style: ElevatedButton.styleFrom(
                minimumSize: Size(double.infinity, 50),
              ),
            ),
            SizedBox(height: 20),
            TextField(
              controller: _codeController,
              decoration: InputDecoration(
                labelText: 'Login Code',
                border: OutlineInputBorder(),
                prefixIcon: Icon(Icons.security),
              ),
              keyboardType: TextInputType.number,
              maxLength: 6,
            ),
            SizedBox(height: 20),
            ElevatedButton(
              onPressed: _isLoading ? null : _verifyCode,
              child: _isLoading
                  ? CircularProgressIndicator()
                  : Text('Login'),
              style: ElevatedButton.styleFrom(
                minimumSize: Size(double.infinity, 50),
                backgroundColor: Colors.green,
              ),
            ),
            if (_message.isNotEmpty)
              Padding(
                padding: EdgeInsets.only(top: 20),
                child: Text(
                  _message,
                  style: TextStyle(
                    color: _message.contains('Error') ? Colors.red : Colors.green,
                  ),
                ),
              ),
          ],
        ),
      ),
    );
  }

  Future<void> _requestLoginCode() async {
    if (_telegramIdController.text.isEmpty) {
      setState(() {
        _message = 'Please enter your Telegram ID';
      });
      return;
    }

    setState(() {
      _isLoading = true;
      _message = '';
    });

    try {
      final result = await _authApi.requestLoginCode(
        int.parse(_telegramIdController.text),
      );

      setState(() {
        _message = result['message'] ?? 'Login code sent to your Telegram!';
      });
    } catch (e) {
      setState(() {
        _message = 'Error: $e';
      });
    } finally {
      setState(() {
        _isLoading = false;
      });
    }
  }

  Future<void> _verifyCode() async {
    if (_codeController.text.isEmpty || _telegramIdController.text.isEmpty) {
      setState(() {
        _message = 'Please enter both Telegram ID and code';
      });
      return;
    }

    setState(() {
      _isLoading = true;
      _message = '';
    });

    try {
      final result = await _authApi.verifyCode(
        telegramId: int.parse(_telegramIdController.text),
        code: _codeController.text,
      );

      if (result['access_token'] != null) {
        Navigator.pushReplacementNamed(context, '/home');
      } else {
        setState(() {
          _message = result['message'] ?? 'Login failed';
        });
      }
    } catch (e) {
      setState(() {
        _message = 'Error: $e';
      });
    } finally {
      setState(() {
        _isLoading = false;
      });
    }
  }
}
