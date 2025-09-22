import 'package:dio/dio.dart';

class ApiService {
  static final Dio _dio = Dio(
    BaseOptions(
      baseUrl: "http://localhost:8000/api", // ⚠️ à changer si backend déployé
      connectTimeout: const Duration(seconds: 10),
      receiveTimeout: const Duration(seconds: 10),
      headers: {"Content-Type": "application/json"},
    ),
  );

  static String? _token;

  /// 🛡️ Ajouter le token Firebase pour authentification
  static void setToken(String token) {
    _token = token;
    _dio.options.headers['Authorization'] = 'Bearer $token';
  }

  /// 🔐 Authentification
  static Future<Map<String, dynamic>> verifyToken() async {
    final res = await _dio.post("/auth/verify-token");
    return res.data;
  }

  static Future<Map<String, dynamic>> getProfile() async {
    final res = await _dio.get("/auth/me");
    return res.data;
  }

  static Future<void> logout() async {
    await _dio.post("/auth/logout");
    _token = null;
    _dio.options.headers.remove('Authorization');
  }

  /// 👤 Utilisateurs
  static Future<Map<String, dynamic>> getUserMe() async {
    final res = await _dio.get("/users/me");
    return res.data;
  }

  static Future<Map<String, dynamic>> updateUser(Map<String, dynamic> data) async {
    final res = await _dio.put("/users/me", data: data);
    return res.data;
  }

  /// 🅿️ Parkings
  static Future<List<dynamic>> getParkings() async {
    final res = await _dio.get("/parkings");
    return res.data;
  }

  static Future<Map<String, dynamic>> createParking(Map<String, dynamic> data) async {
    final res = await _dio.post("/parkings", data: data);
    return res.data;
  }

  static Future<List<dynamic>> getOwnerParkings() async {
    final res = await _dio.get("/owner/parkings");
    return res.data;
  }

  /// 📅 Réservations
  static Future<List<dynamic>> getMyReservations() async {
    final res = await _dio.get("/reservations");
    return res.data;
  }

  static Future<Map<String, dynamic>> createReservation(Map<String, dynamic> data) async {
    final res = await _dio.post("/reservations", data: data);
    return res.data;
  }

  static Future<Map<String, dynamic>> updateReservationStatus(String id, String status) async {
    final res = await _dio.put("/reservations/$id", data: {"status": status});
    return res.data;
  }

  /// 👨‍💼 Administration
  static Future<List<dynamic>> getAdminUsers() async {
    final res = await _dio.get("/admin/users");
    return res.data;
  }

  static Future<void> deleteUser(String id) async {
    await _dio.delete("/admin/users/$id");
  }

  static Future<void> approveParking(String id) async {
    await _dio.post("/admin/parkings/$id/approve");
  }

  static Future<void> rejectParking(String id) async {
    await _dio.post("/admin/parkings/$id/reject");
  }
}
