import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../providers/auth_provider.dart';
import '../../services/api_service.dart';

class ProfileScreen extends StatefulWidget {
  const ProfileScreen({super.key});

  @override
  State<ProfileScreen> createState() => _ProfileScreenState();
}

class _ProfileScreenState extends State<ProfileScreen> {
  bool _loading = false;
  Map<String, dynamic>? _profile;

  @override
  void initState() {
    super.initState();
    _load();
  }

  Future<void> _load() async {
    setState(() => _loading = true);
    try {
      final p = await ApiService.getProfile();
      setState(() => _profile = p);
    } catch (e) {
      debugPrint("getProfile error: $e");
    } finally {
      setState(() => _loading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    final auth = Provider.of<AuthProvider>(context);
    return Scaffold(
      appBar: AppBar(title: const Text("Profil")),
      body: _loading
          ? const Center(child: CircularProgressIndicator())
          : Padding(
              padding: const EdgeInsets.all(20),
              child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
                const CircleAvatar(radius: 40, child: Icon(Icons.person, size: 48)),
                const SizedBox(height: 12),
                Text("Email: ${_profile?['email'] ?? auth.firebaseUser?.email ?? ''}"),
                const SizedBox(height: 6),
                Text("Nom: ${_profile?['display_name'] ?? auth.firebaseUser?.displayName ?? ''}"),
                const SizedBox(height: 6),
                Text("Rôle: ${_profile?['role'] ?? 'user'}"),
              ]),
            ),
    );
  }
}
