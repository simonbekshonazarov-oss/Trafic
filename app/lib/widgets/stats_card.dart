import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../providers/traffic_provider.dart';
import '../utils/constants.dart';

class StatsCard extends StatelessWidget {
  const StatsCard({super.key});

  @override
  Widget build(BuildContext context) {
    return Consumer<TrafficProvider>(
      builder: (context, traffic, child) {
        final summary = traffic.summary;

        if (summary == null) {
          return const Card(
            child: Padding(
              padding: EdgeInsets.all(20),
              child: Center(child: CircularProgressIndicator()),
            ),
          );
        }

        return Column(
          children: [
            _buildPeriodCard(
              'Today',
              summary.dailyGb,
              summary.dailyEarnings,
              Icons.today,
              AppColors.primary,
            ),
            const SizedBox(height: 16),
            _buildPeriodCard(
              'This Week',
              summary.weeklyGb,
              summary.weeklyEarnings,
              Icons.date_range,
              AppColors.secondary,
            ),
            const SizedBox(height: 16),
            _buildPeriodCard(
              'This Month',
              summary.monthlyGb,
              summary.monthlyEarnings,
              Icons.calendar_month,
              AppColors.accent,
            ),
            const SizedBox(height: 16),
            _buildPeriodCard(
              'All Time',
              summary.totalGb,
              summary.totalEarnings,
              Icons.star,
              AppColors.warning,
            ),
          ],
        );
      },
    );
  }

  Widget _buildPeriodCard(
    String period,
    double gb,
    double earnings,
    IconData icon,
    Color color,
  ) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Row(
          children: [
            Container(
              padding: const EdgeInsets.all(12),
              decoration: BoxDecoration(
                color: color.withValues(alpha: 0.1),
                borderRadius: BorderRadius.circular(12),
              ),
              child: Icon(icon, color: color, size: 32),
            ),
            const SizedBox(width: 16),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    period,
                    style: const TextStyle(
                      color: AppColors.textSecondary,
                      fontSize: 14,
                    ),
                  ),
                  const SizedBox(height: 4),
                  Text(
                    '${gb.toStringAsFixed(2)} GB',
                    style: const TextStyle(
                      fontSize: 20,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                ],
              ),
            ),
            Column(
              crossAxisAlignment: CrossAxisAlignment.end,
              children: [
                const Text(
                  'Earned',
                  style: TextStyle(
                    color: AppColors.textSecondary,
                    fontSize: 12,
                  ),
                ),
                const SizedBox(height: 4),
                Text(
                  '\$${earnings.toStringAsFixed(2)}',
                  style: TextStyle(
                    color: color,
                    fontSize: 18,
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }
}
