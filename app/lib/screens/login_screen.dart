import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../providers/auth_provider.dart';
import '../utils/constants.dart';

class LoginScreen extends StatefulWidget {
  const LoginScreen({super.key});

  @override
  State<LoginScreen> createState() => _LoginScreenState();
}

class _LoginScreenState extends State<LoginScreen> {
  final _telegramIdController = TextEditingController();
  final _codeController = TextEditingController();
  bool _codeSent = false;

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: SafeArea(
        child: Padding(
          padding: const EdgeInsets.all(24.0),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              const Icon(
                Icons.share,
                size: 80,
                color: AppColors.primary,
              ),
              const SizedBox(height: 24),
              const Text(
                'Traffic Share',
                textAlign: TextAlign.center,
                style: TextStyle(
                  fontSize: 32,
                  fontWeight: FontWeight.bold,
                ),
              ),
              const SizedBox(height: 8),
              const Text(
                'Login with Telegram',
                textAlign: TextAlign.center,
                style: TextStyle(
                  fontSize: 16,
                  color: AppColors.textSecondary,
                ),
              ),
              const SizedBox(height: 48),
              
              // Telegram ID Input
              TextField(
                controller: _telegramIdController,
                keyboardType: TextInputType.number,
                decoration: InputDecoration(
                  labelText: 'Telegram ID',
                  hintText: 'Enter your Telegram ID',
                  prefixIcon: const Icon(Icons.telegram),
                  border: OutlineInputBorder(
                    borderRadius: BorderRadius.circular(12),
                  ),
                ),
              ),
              
              if (_codeSent) ...[
                const SizedBox(height: 16),
                TextField(
                  controller: _codeController,
                  keyboardType: TextInputType.number,
                  decoration: InputDecoration(
                    labelText: 'Verification Code',
                    hintText: 'Enter code from Telegram',
                    prefixIcon: const Icon(Icons.lock),
                    border: OutlineInputBorder(
                      borderRadius: BorderRadius.circular(12),
                    ),
                  ),
                ),
              ],
              
              const SizedBox(height: 24),
              
              Consumer<AuthProvider>(
                builder: (context, auth, child) {
                  if (auth.isLoading) {
                    return const Center(child: CircularProgressIndicator());
                  }
                  
                  return ElevatedButton(
                    onPressed: () => _handleLogin(context),
                    child: Text(
                      _codeSent ? 'Verify Code' : 'Send Code',
                      style: const TextStyle(fontSize: 16),
                    ),
                  );
                },
              ),
              
              const SizedBox(height: 16),
              
              Consumer<AuthProvider>(
                builder: (context, auth, child) {
                  if (auth.error != null) {
                    return Text(
                      auth.error!,
                      style: const TextStyle(color: AppColors.error),
                      textAlign: TextAlign.center,
                    );
                  }
                  return const SizedBox.shrink();
                },
              ),
            ],
          ),
        ),
      ),
    );
  }

  Future<void> _handleLogin(BuildContext context) async {
    final auth = Provider.of<AuthProvider>(context, listen: false);
    
    if (!_codeSent) {
      // Request login code
      final telegramId = int.tryParse(_telegramIdController.text);
      if (telegramId == null) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('Please enter valid Telegram ID')),
        );
        return;
      }
      
      final success = await auth.requestLoginCode(telegramId);
      if (success) {
        setState(() => _codeSent = true);
        if (context.mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(content: Text('Code sent to your Telegram!')),
          );
        }
      }
    } else {
      // Verify code
      final telegramId = int.tryParse(_telegramIdController.text);
      final code = _codeController.text;
      
      if (telegramId == null || code.isEmpty) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('Please enter code')),
        );
        return;
      }
      
      final success = await auth.verifyCode(
        telegramId: telegramId,
        code: code,
      );
      
      if (success && context.mounted) {
        Navigator.pushReplacementNamed(context, '/home');
      }
    }
  }

  @override
  void dispose() {
    _telegramIdController.dispose();
    _codeController.dispose();
    super.dispose();
  }
}
