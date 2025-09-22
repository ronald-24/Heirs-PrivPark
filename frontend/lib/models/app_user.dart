class AppUser {
  final int? id;
  final String firebaseUid;
  final String? email;
  final String? displayName;
  final String role;
  final DateTime? createdAt;

  AppUser({
    this.id,
    required this.firebaseUid,
    this.email,
    this.displayName,
    this.role = 'user',
    this.createdAt,
  });

  factory AppUser.fromJson(Map<String, dynamic> json) {
    return AppUser(
      id: json['id'],
      firebaseUid: json['firebase_uid'] ?? json['firebaseUid'] ?? '',
      email: json['email'],
      displayName: json['display_name'] ?? json['displayName'],
      role: json['role'] ?? 'user',
      createdAt: json['created_at'] != null ? DateTime.parse(json['created_at']) : null,
    );
  }
}
