import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../providers/auth_provider.dart';
import '../providers/traffic_provider.dart';
import '../providers/balance_provider.dart';
import '../utils/constants.dart';
import '../widgets/traffic_card.dart';
import '../widgets/balance_card.dart';
import '../widgets/stats_card.dart';

class HomeScreen extends StatefulWidget {
  const HomeScreen({super.key});

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  int _currentIndex = 0;

  @override
  void initState() {
    super.initState();
    _loadData();
  }

  Future<void> _loadData() async {
    final auth = Provider.of<AuthProvider>(context, listen: false);
    final balance = Provider.of<BalanceProvider>(context, listen: false);
    final traffic = Provider.of<TrafficProvider>(context, listen: false);

    await auth.loadUserProfile();
    await balance.loadBalance();
    await traffic.loadSummary();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Traffic Share'),
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh),
            onPressed: _loadData,
          ),
          IconButton(
            icon: const Icon(Icons.logout),
            onPressed: () => _handleLogout(context),
          ),
        ],
      ),
      body: _buildBody(),
      bottomNavigationBar: BottomNavigationBar(
        currentIndex: _currentIndex,
        onTap: (index) => setState(() => _currentIndex = index),
        items: const [
          BottomNavigationBarItem(
            icon: Icon(Icons.home),
            label: 'Home',
          ),
          BottomNavigationBarItem(
            icon: Icon(Icons.show_chart),
            label: 'Stats',
          ),
          BottomNavigationBarItem(
            icon: Icon(Icons.account_balance_wallet),
            label: 'Wallet',
          ),
        ],
      ),
    );
  }

  Widget _buildBody() {
    switch (_currentIndex) {
      case 0:
        return _buildHomePage();
      case 1:
        return _buildStatsPage();
      case 2:
        return _buildWalletPage();
      default:
        return _buildHomePage();
    }
  }

  Widget _buildHomePage() {
    return RefreshIndicator(
      onRefresh: _loadData,
      child: SingleChildScrollView(
        physics: const AlwaysScrollableScrollPhysics(),
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            Consumer<AuthProvider>(
              builder: (context, auth, child) {
                return Card(
                  child: Padding(
                    padding: const EdgeInsets.all(16),
                    child: Column(
                      children: [
                        const CircleAvatar(
                          radius: 40,
                          child: Icon(Icons.person, size: 40),
                        ),
                        const SizedBox(height: 8),
                        Text(
                          auth.currentUser?.username ?? 'User',
                          style: const TextStyle(
                            fontSize: 20,
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                        Text(
                          'ID: ${auth.currentUser?.id ?? ""}',
                          style: const TextStyle(
                            color: AppColors.textSecondary,
                          ),
                        ),
                      ],
                    ),
                  ),
                );
              },
            ),
            const SizedBox(height: 16),
            const BalanceCard(),
            const SizedBox(height: 16),
            const TrafficCard(),
          ],
        ),
      ),
    );
  }

  Widget _buildStatsPage() {
    return RefreshIndicator(
      onRefresh: _loadData,
      child: const SingleChildScrollView(
        physics: AlwaysScrollableScrollPhysics(),
        padding: EdgeInsets.all(16),
        child: Column(
          children: [
            StatsCard(),
          ],
        ),
      ),
    );
  }

  Widget _buildWalletPage() {
    return RefreshIndicator(
      onRefresh: _loadData,
      child: SingleChildScrollView(
        physics: const AlwaysScrollableScrollPhysics(),
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            const BalanceCard(),
            const SizedBox(height: 16),
            Consumer<BalanceProvider>(
              builder: (context, balance, child) {
                return ElevatedButton.icon(
                  onPressed: balance.canWithdraw
                      ? () => _handleWithdraw(context)
                      : null,
                  icon: const Icon(Icons.account_balance_wallet),
                  label: Text(
                    balance.canWithdraw
                        ? 'Withdraw (\$${balance.available.toStringAsFixed(2)})'
                        : 'Minimum \$5.00 required',
                  ),
                );
              },
            ),
          ],
        ),
      ),
    );
  }

  void _handleWithdraw(BuildContext context) {
    // TODO: Implement withdrawal dialog
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(content: Text('Withdraw feature coming soon!')),
    );
  }

  Future<void> _handleLogout(BuildContext context) async {
    final auth = Provider.of<AuthProvider>(context, listen: false);
    await auth.logout();
    if (context.mounted) {
      Navigator.pushReplacementNamed(context, '/login');
    }
  }
}
