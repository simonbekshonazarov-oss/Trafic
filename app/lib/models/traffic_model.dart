class TrafficSession {
  final int id;
  final String sessionId;
  final int userId;
  final DateTime startTime;
  final DateTime? endTime;
  final int bytesTotal;
  final double earnings;
  final String status;

  TrafficSession({
    required this.id,
    required this.sessionId,
    required this.userId,
    required this.startTime,
    this.endTime,
    required this.bytesTotal,
    required this.earnings,
    required this.status,
  });

  factory TrafficSession.fromJson(Map<String, dynamic> json) {
    return TrafficSession(
      id: json['id'],
      sessionId: json['session_id'],
      userId: json['user_id'],
      startTime: DateTime.parse(json['start_time']),
      endTime: json['end_time'] != null
          ? DateTime.parse(json['end_time'])
          : null,
      bytesTotal: json['bytes_total'] ?? 0,
      earnings: (json['earnings'] ?? 0.0).toDouble(),
      status: json['status'] ?? 'active',
    );
  }

  double get totalGB => bytesTotal / (1024 * 1024 * 1024);

  Duration get duration {
    final end = endTime ?? DateTime.now();
    return end.difference(startTime);
  }
}

class TrafficSummary {
  final double dailyGb;
  final double weeklyGb;
  final double monthlyGb;
  final double totalGb;
  final double dailyEarnings;
  final double weeklyEarnings;
  final double monthlyEarnings;
  final double totalEarnings;

  TrafficSummary({
    required this.dailyGb,
    required this.weeklyGb,
    required this.monthlyGb,
    required this.totalGb,
    required this.dailyEarnings,
    required this.weeklyEarnings,
    required this.monthlyEarnings,
    required this.totalEarnings,
  });

  factory TrafficSummary.fromJson(Map<String, dynamic> json) {
    return TrafficSummary(
      dailyGb: (json['daily_gb'] ?? 0.0).toDouble(),
      weeklyGb: (json['weekly_gb'] ?? 0.0).toDouble(),
      monthlyGb: (json['monthly_gb'] ?? 0.0).toDouble(),
      totalGb: (json['total_gb'] ?? 0.0).toDouble(),
      dailyEarnings: (json['daily_earnings'] ?? 0.0).toDouble(),
      weeklyEarnings: (json['weekly_earnings'] ?? 0.0).toDouble(),
      monthlyEarnings: (json['monthly_earnings'] ?? 0.0).toDouble(),
      totalEarnings: (json['total_earnings'] ?? 0.0).toDouble(),
    );
  }
}
