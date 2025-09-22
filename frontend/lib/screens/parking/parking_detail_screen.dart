import 'package:flutter/material.dart';

class ParkingDetailScreen extends StatelessWidget {
  final Map<String, dynamic> parking;
  const ParkingDetailScreen({super.key, required this.parking});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text(parking['title'] ?? "Parking Details")),
      body: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(parking['description'] ?? "No description"),
            const SizedBox(height: 10),
            Text("Price: \$${parking['price_per_hour']} / hour"),
            const SizedBox(height: 20),
            ElevatedButton(
              onPressed: () {
                // TODO: Implement reservation
              },
              child: const Text("Reserve Now"),
            )
          ],
        ),
      ),
    );
  }
}
