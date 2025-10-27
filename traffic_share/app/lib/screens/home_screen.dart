import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';

class HomeScreen extends StatefulWidget {
  @override
  _HomeScreenState createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  bool _isSharing = false;
  double _balance = 0.0;
  String _sessionId = '';
  int _bytesShared = 0;

  @override
  void initState() {
    super.initState();
    _loadUserData();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text('Traffic Share'),
        centerTitle: true,
        actions: [
          IconButton(
            icon: Icon(Icons.settings),
            onPressed: () {
              // Navigate to settings
            },
          ),
        ],
      ),
      body: Padding(
        padding: EdgeInsets.all(16.0),
        child: Column(
          children: [
            // Balance Card
            Card(
              child: Padding(
                padding: EdgeInsets.all(16.0),
                child: Column(
                  children: [
                    Text(
                      'Your Balance',
                      style: TextStyle(
                        fontSize: 18,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                    SizedBox(height: 10),
                    Text(
                      '\$${_balance.toStringAsFixed(2)}',
                      style: TextStyle(
                        fontSize: 32,
                        fontWeight: FontWeight.bold,
                        color: Colors.green,
                      ),
                    ),
                    SizedBox(height: 10),
                    Text(
                      'Minimum withdrawal: \$5.00',
                      style: TextStyle(
                        color: Colors.grey[600],
                      ),
                    ),
                  ],
                ),
              ),
            ),
            SizedBox(height: 20),
            
            // Traffic Sharing Status
            Card(
              child: Padding(
                padding: EdgeInsets.all(16.0),
                child: Column(
                  children: [
                    Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        Text(
                          'Traffic Sharing',
                          style: TextStyle(
                            fontSize: 18,
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                        Switch(
                          value: _isSharing,
                          onChanged: _isSharing ? _stopSharing : _startSharing,
                          activeColor: Colors.green,
                        ),
                      ],
                    ),
                    SizedBox(height: 10),
                    Text(
                      _isSharing ? 'Currently sharing traffic' : 'Not sharing traffic',
                      style: TextStyle(
                        color: _isSharing ? Colors.green : Colors.grey[600],
                      ),
                    ),
                    if (_isSharing) ...[
                      SizedBox(height: 10),
                      Text(
                        'Session ID: ${_sessionId.substring(0, 8)}...',
                        style: TextStyle(
                          fontSize: 12,
                          color: Colors.grey[600],
                        ),
                      ),
                      Text(
                        'Data shared: ${(_bytesShared / 1024 / 1024).toStringAsFixed(2)} MB',
                        style: TextStyle(
                          fontSize: 12,
                          color: Colors.grey[600],
                        ),
                      ),
                    ],
                  ],
                ),
              ),
            ),
            SizedBox(height: 20),
            
            // Statistics
            Card(
              child: Padding(
                padding: EdgeInsets.all(16.0),
                child: Column(
                  children: [
                    Text(
                      'Today\'s Statistics',
                      style: TextStyle(
                        fontSize: 18,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                    SizedBox(height: 10),
                    Row(
                      mainAxisAlignment: MainAxisAlignment.spaceAround,
                      children: [
                        Column(
                          children: [
                            Text(
                              '0',
                              style: TextStyle(
                                fontSize: 24,
                                fontWeight: FontWeight.bold,
                                color: Colors.blue,
                              ),
                            ),
                            Text('Sessions'),
                          ],
                        ),
                        Column(
                          children: [
                            Text(
                              '0 GB',
                              style: TextStyle(
                                fontSize: 24,
                                fontWeight: FontWeight.bold,
                                color: Colors.orange,
                              ),
                            ),
                            Text('Data Shared'),
                          ],
                        ),
                        Column(
                          children: [
                            Text(
                              '\$0.00',
                              style: TextStyle(
                                fontSize: 24,
                                fontWeight: FontWeight.bold,
                                color: Colors.green,
                              ),
                            ),
                            Text('Earnings'),
                          ],
                        ),
                      ],
                    ),
                  ],
                ),
              ),
            ),
            SizedBox(height: 20),
            
            // Action Buttons
            Row(
              children: [
                Expanded(
                  child: ElevatedButton.icon(
                    onPressed: _balance >= 5.0 ? _requestWithdrawal : null,
                    icon: Icon(Icons.money),
                    label: Text('Withdraw'),
                    style: ElevatedButton.styleFrom(
                      backgroundColor: Colors.green,
                      foregroundColor: Colors.white,
                    ),
                  ),
                ),
                SizedBox(width: 10),
                Expanded(
                  child: ElevatedButton.icon(
                    onPressed: () {
                      // Navigate to history
                    },
                    icon: Icon(Icons.history),
                    label: Text('History'),
                  ),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }

  Future<void> _loadUserData() async {
    // TODO: Load user data from API
    setState(() {
      _balance = 0.0;
    });
  }

  Future<void> _startSharing(bool value) async {
    setState(() {
      _isSharing = true;
    });

    try {
      // Register device first
      final deviceResponse = await http.post(
        Uri.parse('http://localhost:8000/api/user/device/register'),
        headers: {
          'Content-Type': 'application/json',
          'Authorization': 'Bearer YOUR_TOKEN_HERE', // TODO: Get from storage
        },
        body: jsonEncode({
          'device_id': 'device_123', // TODO: Get actual device ID
          'os': 'android',
          'ip': '192.168.1.100', // TODO: Get actual IP
        }),
      );

      if (deviceResponse.statusCode == 200) {
        // Start traffic session
        final sessionResponse = await http.post(
          Uri.parse('http://localhost:8000/api/traffic/start'),
          headers: {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer YOUR_TOKEN_HERE',
          },
          body: jsonEncode({
            'device_id': 'device_123',
            'local_ip': '192.168.1.100',
            'public_ip': '203.0.113.1', // TODO: Get actual public IP
            'client_version': '1.0.0',
          }),
        );

        if (sessionResponse.statusCode == 200) {
          final data = jsonDecode(sessionResponse.body);
          setState(() {
            _sessionId = data['session_id'];
          });
          
          // Start periodic updates
          _startPeriodicUpdates();
        }
      }
    } catch (e) {
      setState(() {
        _isSharing = false;
      });
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Error starting traffic sharing: $e')),
      );
    }
  }

  Future<void> _stopSharing(bool value) async {
    setState(() {
      _isSharing = false;
    });

    try {
      final response = await http.post(
        Uri.parse('http://localhost:8000/api/traffic/stop'),
        headers: {
          'Content-Type': 'application/json',
          'Authorization': 'Bearer YOUR_TOKEN_HERE',
        },
        body: jsonEncode({
          'session_id': _sessionId,
          'final_bytes_tx': _bytesShared,
          'final_bytes_rx': 0,
        }),
      );

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Session completed! Earnings: \$${data['earnings']}'),
          ),
        );
        _loadUserData(); // Refresh balance
      }
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Error stopping traffic sharing: $e')),
      );
    }
  }

  void _startPeriodicUpdates() {
    // TODO: Implement periodic traffic updates
    // This would send traffic data every 10 seconds
  }

  Future<void> _requestWithdrawal() async {
    // TODO: Implement withdrawal request
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: Text('Withdrawal Request'),
        content: Text('Withdrawal feature coming soon!'),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: Text('OK'),
          ),
        ],
      ),
    );
  }
}
