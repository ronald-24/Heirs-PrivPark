import 'package:flutter/material.dart';
import '../../services/api_service.dart';

class AdminParkingsScreen extends StatefulWidget {
  const AdminParkingsScreen({super.key});

  @override
  State<AdminParkingsScreen> createState() => _AdminParkingsScreenState();
}

class _AdminParkingsScreenState extends State<AdminParkingsScreen> {
  List<dynamic> parkings = [];
  bool loading = true;

  @override
  void initState() {
    super.initState();
    _loadParkings();
  }

  Future<void> _loadParkings() async {
    try {
      final res = await ApiService.getParkings();
      setState(() {
        parkings = res;
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
      appBar: AppBar(title: const Text("Manage Parkings")),
      body: loading
          ? const Center(child: CircularProgressIndicator())
          : ListView.builder(
              itemCount: parkings.length,
              itemBuilder: (ctx, i) {
                final p = parkings[i];
                return Card(
                  child: ListTile(
                    title: Text(p['title']),
                    subtitle: Text("Status: ${p['status']}"),
                    trailing: Row(
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        IconButton(icon: const Icon(Icons.check, color: Colors.green), onPressed: () async {
                          await ApiService.approveParking(p['id'].toString());
                          _loadParkings();
                        }),
                        IconButton(icon: const Icon(Icons.close, color: Colors.red), onPressed: () async {
                          await ApiService.rejectParking(p['id'].toString());
                          _loadParkings();
                        }),
                      ],
                    ),
                  ),
                );
              },
            ),
    );
  }
}
