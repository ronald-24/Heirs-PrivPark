import 'package:firebase_auth/firebase_auth.dart';

class AuthService {
  final FirebaseAuth _auth = FirebaseAuth.instance;

  Stream<User?> get authStateChanges => _auth.authStateChanges();

  Future<User?> signIn(String email, String password) async {
    final cred = await _auth.signInWithEmailAndPassword(email: email, password: password);
    return cred.user;
  }

  Future<User?> register(String email, String password, {String? displayName}) async {
    final cred = await _auth.createUserWithEmailAndPassword(email: email, password: password);
    final user = cred.user;
    if (user != null && displayName != null) {
      await user.updateDisplayName(displayName);
      await user.reload();
    }
    return user;
  }

  Future<void> sendPasswordReset(String email) async => await _auth.sendPasswordResetEmail(email: email);

  Future<void> signOut() async => await _auth.signOut();
}
