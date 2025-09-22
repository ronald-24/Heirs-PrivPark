import 'package:flutter/material.dart';
import '../../services/api_service.dart';
import 'parking_detail_screen.dart';

class ParkingListScreen extends StatefulWidget {
  const ParkingListScreen({super.key});

  @override
  State<ParkingListScreen> createState() => _ParkingListScreenState();
}

class _ParkingListScreenState extends State<ParkingListScreen> {
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
      appBar: AppBar(title: const Text("Available Parkings")),
      body: loading
          ? const Center(child: CircularProgressIndicator())
          : ListView.builder(
              itemCount: parkings.length,
              itemBuilder: (ctx, i) {
                final p = parkings[i];
                return Card(
                  child: ListTile(
                    title: Text(p['title']),
                    subtitle: Text("\$${p['price_per_hour']} per hour"),
                    onTap: () {
                      Navigator.push(
                        context,
                        MaterialPageRoute(builder: (_) => ParkingDetailScreen(parking: p)),
                      );
                    },
                  ),
                );
              },
            ),
    );
  }
}
