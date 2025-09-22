import 'dart:async';
import 'package:flutter/material.dart';
import 'package:firebase_auth/firebase_auth.dart';
import '../services/api_service.dart';
import '../models/app_user.dart';

class AuthProvider extends ChangeNotifier {
  final FirebaseAuth _auth = FirebaseAuth.instance;
  User? firebaseUser;
  AppUser? appUser;
  StreamSubscription<User?>? _sub;
  bool loading = true;

  AuthProvider() {
    _sub = _auth.authStateChanges().listen((u) => _onAuthChanged(u));
  }

  Future<void> _onAuthChanged(User? u) async {
    firebaseUser = u;
    if (u != null) {
      // appelle backend pour synchroniser / récupérer profil
      try {
        final data = await ApiService.verifyToken();
        appUser = AppUser.fromJson(data);
      } catch (e) {
        appUser = null;
        debugPrint("verifyToken error: $e");
      }
    } else {
      appUser = null;
    }
    loading = false;
    notifyListeners();
  }

  Future<void> disposeProvider() async {
    await _sub?.cancel();
  }

  // helper pour forcer refresh token + backend sync
  Future<void> refreshBackendProfile() async {
    if (firebaseUser == null) return;
    final data = await ApiService.verifyToken();
    appUser = AppUser.fromJson(data);
    notifyListeners();
  }
}
