import 'package:flutter/material.dart';
import '../../services/api_service.dart';

class AdminReservationsScreen extends StatefulWidget {
  const AdminReservationsScreen({super.key});

  @override
  State<AdminReservationsScreen> createState() => _AdminReservationsScreenState();
}

class _AdminReservationsScreenState extends State<AdminReservationsScreen> {
  List<dynamic> reservations = [];
  bool loading = true;

  @override
  void initState() {
    super.initState();
    _loadReservations();
  }

  Future<void> _loadReservations() async {
    try {
      final res = await ApiService.getMyReservations();
      setState(() {
        reservations = res;
        loading = false;
      });
    } catch (e) {
      setState(() => loading = false);
      ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text("Error: $e")));
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text("Manage Reservations")),
      body: loading
          ? const Center(child: CircularProgressIndicator())
          : ListView.builder(
              itemCount: reservations.length,
              itemBuilder: (ctx, i) {
                final r = reservations[i];
                return Card(
                  child: ListTile(
                    title: Text("Reservation #${r['id']}"),
                    subtitle: Text("Status: ${r['status']}"),
                    trailing: PopupMenuButton<String>(
                      onSelected: (status) async {
                        await ApiService.updateReservationStatus(r['id'].toString(), status);
                        _loadReservations();
                      },
                      itemBuilder: (ctx) => const [
                        PopupMenuItem(value: "confirmed", child: Text("Confirm")),
                        PopupMenuItem(value: "cancelled", child: Text("Cancel")),
                      ],
                    ),
                  ),
                );
              },
            ),
    );
  }
}
