import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../providers/traffic_provider.dart';
import '../utils/constants.dart';

class TrafficCard extends StatelessWidget {
  const TrafficCard({super.key});

  @override
  Widget build(BuildContext context) {
    return Consumer<TrafficProvider>(
      builder: (context, traffic, child) {
        return Card(
          child: Padding(
            padding: const EdgeInsets.all(20),
            child: Column(
              children: [
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    const Text(
                      'Traffic Sharing',
                      style: TextStyle(
                        fontSize: 18,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                    _buildStatusBadge(traffic.status),
                  ],
                ),
                const SizedBox(height: 24),
                
                // Traffic Stats
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceAround,
                  children: [
                    _buildStat(
                      'Data',
                      '${traffic.totalGB.toStringAsFixed(2)} GB',
                      Icons.cloud_upload,
                    ),
                    _buildStat(
                      'Earned',
                      '\$${traffic.currentEarnings.toStringAsFixed(2)}',
                      Icons.attach_money,
                    ),
                  ],
                ),
                
                const SizedBox(height: 24),
                
                // Start/Stop Button
                SizedBox(
                  width: double.infinity,
                  child: ElevatedButton.icon(
                    onPressed: traffic.status == TrafficStatus.active
                        ? () => _stopSharing(context, traffic)
                        : traffic.status == TrafficStatus.inactive
                            ? () => _startSharing(context, traffic)
                            : null,
                    icon: Icon(
                      traffic.status == TrafficStatus.active
                          ? Icons.stop
                          : Icons.play_arrow,
                    ),
                    label: Text(
                      _getButtonText(traffic.status),
                      style: const TextStyle(fontSize: 16),
                    ),
                    style: ElevatedButton.styleFrom(
                      backgroundColor: traffic.status == TrafficStatus.active
                          ? AppColors.error
                          : AppColors.success,
                      padding: const EdgeInsets.symmetric(vertical: 16),
                    ),
                  ),
                ),
              ],
            ),
          ),
        );
      },
    );
  }

  Widget _buildStatusBadge(TrafficStatus status) {
    Color color;
    String text;
    IconData icon;

    switch (status) {
      case TrafficStatus.active:
        color = AppColors.success;
        text = 'Active';
        icon = Icons.check_circle;
        break;
      case TrafficStatus.starting:
        color = AppColors.warning;
        text = 'Starting...';
        icon = Icons.hourglass_empty;
        break;
      case TrafficStatus.stopping:
        color = AppColors.warning;
        text = 'Stopping...';
        icon = Icons.hourglass_empty;
        break;
      case TrafficStatus.error:
        color = AppColors.error;
        text = 'Error';
        icon = Icons.error;
        break;
      default:
        color = AppColors.textSecondary;
        text = 'Inactive';
        icon = Icons.pause_circle;
    }

    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
      decoration: BoxDecoration(
        color: color.withValues(alpha: 0.1),
        borderRadius: BorderRadius.circular(12),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(icon, size: 16, color: color),
          const SizedBox(width: 4),
          Text(
            text,
            style: TextStyle(
              color: color,
              fontWeight: FontWeight.bold,
              fontSize: 12,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildStat(String label, String value, IconData icon) {
    return Column(
      children: [
        Icon(icon, color: AppColors.primary, size: 32),
        const SizedBox(height: 8),
        Text(
          value,
          style: const TextStyle(
            fontSize: 20,
            fontWeight: FontWeight.bold,
          ),
        ),
        Text(
          label,
          style: const TextStyle(
            color: AppColors.textSecondary,
            fontSize: 14,
          ),
        ),
      ],
    );
  }

  String _getButtonText(TrafficStatus status) {
    switch (status) {
      case TrafficStatus.active:
        return 'Stop Sharing';
      case TrafficStatus.starting:
        return 'Starting...';
      case TrafficStatus.stopping:
        return 'Stopping...';
      default:
        return 'Start Sharing';
    }
  }

  Future<void> _startSharing(BuildContext context, TrafficProvider traffic) async {
    final success = await traffic.startSharing();
    if (!context.mounted) return;
    if (!success) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Failed to start sharing')),
      );
    }
  }

  Future<void> _stopSharing(BuildContext context, TrafficProvider traffic) async {
    final success = await traffic.stopSharing();
    if (!context.mounted) return;
    if (success) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text(
            'Session ended! Earned: \$${traffic.currentEarnings.toStringAsFixed(2)}',
          ),
        ),
      );
    }
  }
}
