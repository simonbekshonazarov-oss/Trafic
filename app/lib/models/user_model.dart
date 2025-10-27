class User {
  final int id;
  final int telegramId;
  final String? username;
  final String? phone;
  final String? email;
  final double balance;
  final double totalEarned;
  final bool isActive;
  final bool isVerified;
  final DateTime createdAt;
  final DateTime? lastLoginAt;

  User({
    required this.id,
    required this.telegramId,
    this.username,
    this.phone,
    this.email,
    required this.balance,
    required this.totalEarned,
    required this.isActive,
    required this.isVerified,
    required this.createdAt,
    this.lastLoginAt,
  });

  factory User.fromJson(Map<String, dynamic> json) {
    return User(
      id: json['id'],
      telegramId: json['telegram_id'],
      username: json['username'],
      phone: json['phone'],
      email: json['email'],
      balance: (json['balance'] ?? 0.0).toDouble(),
      totalEarned: (json['total_earned'] ?? 0.0).toDouble(),
      isActive: json['is_active'] ?? true,
      isVerified: json['is_verified'] ?? false,
      createdAt: DateTime.parse(json['created_at']),
      lastLoginAt: json['last_login_at'] != null
          ? DateTime.parse(json['last_login_at'])
          : null,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'telegram_id': telegramId,
      'username': username,
      'phone': phone,
      'email': email,
      'balance': balance,
      'total_earned': totalEarned,
      'is_active': isActive,
      'is_verified': isVerified,
      'created_at': createdAt.toIso8601String(),
      'last_login_at': lastLoginAt?.toIso8601String(),
    };
  }
}
