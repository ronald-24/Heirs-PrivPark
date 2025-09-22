import 'package:flutter/material.dart';
import '../parking/parking_list_screen.dart';
import '../reservations/reservations_screen.dart';
import '../owner/owner_home_screen.dart';
import '../admin/admin_home_screen.dart';
import '../../utils/constants.dart';

class HomeScreen extends StatelessWidget {
  const HomeScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text("HeirsPrivPark")),
      body: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            ElevatedButton(
              style: ElevatedButton.styleFrom(
                  backgroundColor: AppColors.primary),
              onPressed: () {
                Navigator.push(
                  context,
                  MaterialPageRoute(
                      builder: (_) => const ParkingListScreen()),
                );
              },
              child:
                  const Text("Find Parking", style: AppTextStyles.button),
            ),
            const SizedBox(height: 12),
            ElevatedButton(
              style: ElevatedButton.styleFrom(
                  backgroundColor: AppColors.primary),
              onPressed: () {
                Navigator.push(
                  context,
                  MaterialPageRoute(
                      builder: (_) => const ReservationsScreen()),
                );
              },
              child: const Text("My Reservations",
                  style: AppTextStyles.button),
            ),
            const SizedBox(height: 12),
            ElevatedButton(
              style: ElevatedButton.styleFrom(backgroundColor: Colors.green),
              onPressed: () {
                Navigator.push(
                  context,
                  MaterialPageRoute(
                      builder: (_) => const OwnerHomeScreen()),
                );
              },
              child: const Text("Owner Dashboard",
                  style: AppTextStyles.button),
            ),
            const SizedBox(height: 12),
            ElevatedButton(
              style: ElevatedButton.styleFrom(backgroundColor: Colors.red),
              onPressed: () {
                Navigator.push(
                  context,
                  MaterialPageRoute(
                      builder: (_) => const AdminHomeScreen()),
                );
              },
              child:
                  const Text("Admin Panel", style: AppTextStyles.button),
            ),
          ],
        ),
      ),
    );
  }
}
