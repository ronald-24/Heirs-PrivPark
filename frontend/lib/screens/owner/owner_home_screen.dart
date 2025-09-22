import 'package:flutter/material.dart';
import '../../services/api_service.dart';
import '../parking/add_parking_screen.dart';
import 'owner_edit_parking_screen.dart';

class OwnerHomeScreen extends StatefulWidget {
  const OwnerHomeScreen({super.key});

  @override
  State<OwnerHomeScreen> createState() => _OwnerHomeScreenState();
}

class _OwnerHomeScreenState extends State<OwnerHomeScreen> {
  List<dynamic> parkings = [];
  bool loading = true;

  @override
  void initState() {
    super.initState();
    _loadOwnerParkings();
  }

  Future<void> _loadOwnerParkings() async {
    try {
      final res = await ApiService.getOwnerParkings();
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
      appBar: AppBar(title: const Text("My Parkings")),
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
                    trailing: IconButton(
                      icon: const Icon(Icons.edit),
                      onPressed: () {
                        Navigator.push(
                          context,
                          MaterialPageRoute(
                            builder: (_) => OwnerEditParkingScreen(parking: p),
                          ),
                        );
                      },
                    ),
                  ),
                );
              },
            ),
      floatingActionButton: FloatingActionButton(
        onPressed: () {
          Navigator.push(
            context,
            MaterialPageRoute(builder: (_) => const AddParkingScreen()),
          );
        },
        child: const Icon(Icons.add),
      ),
    );
  }
}
