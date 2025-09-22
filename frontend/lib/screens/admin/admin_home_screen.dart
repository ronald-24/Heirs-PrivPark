import 'package:flutter/material.dart';
import '../../services/api_service.dart';
import 'admin_users_screen.dart';
import 'admin_parkings_screen.dart';
import 'admin_reservations_screen.dart';

class AdminHomeScreen extends StatefulWidget {
  const AdminHomeScreen({super.key});

  @override
  State<AdminHomeScreen> createState() => _AdminHomeScreenState();
}

class _AdminHomeScreenState extends State<AdminHomeScreen> {
  int usersCount = 0;
  int parkingsCount = 0;
  int reservationsCount = 0;

  @override
  void initState() {
    super.initState();
    _loadStats();
  }

  Future<void> _loadStats() async {
    try {
      final users = await ApiService.getAdminUsers();
      final parks = await ApiService.getParkings();
      final res = await ApiService.getMyReservations();
      setState(() {
        usersCount = users.length;
        parkingsCount = parks.length;
        reservationsCount = res.length;
      });
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text("Error: $e")));
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text("Admin Dashboard")),
      body: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          children: [
            Card(child: ListTile(leading: const Icon(Icons.people), title: const Text("Users"), trailing: Text("$usersCount"))),
            Card(child: ListTile(leading: const Icon(Icons.local_parking), title: const Text("Parkings"), trailing: Text("$parkingsCount"))),
            Card(child: ListTile(leading: const Icon(Icons.book_online), title: const Text("Reservations"), trailing: Text("$reservationsCount"))),
            const SizedBox(height: 20),
            ElevatedButton(onPressed: () {
              Navigator.push(context, MaterialPageRoute(builder: (_) => const AdminUsersScreen()));
            }, child: const Text("Manage Users")),
            ElevatedButton(onPressed: () {
              Navigator.push(context, MaterialPageRoute(builder: (_) => const AdminParkingsScreen()));
            }, child: const Text("Manage Parkings")),
            ElevatedButton(onPressed: () {
              Navigator.push(context, MaterialPageRoute(builder: (_) => const AdminReservationsScreen()));
            }, child: const Text("Manage Reservations")),
          ],
        ),
      ),
    );
  }
}
