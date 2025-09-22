import 'package:flutter/material.dart';
import '../../services/api_service.dart';

class OwnerEditParkingScreen extends StatefulWidget {
  final Map<String, dynamic> parking;
  const OwnerEditParkingScreen({super.key, required this.parking});

  @override
  State<OwnerEditParkingScreen> createState() => _OwnerEditParkingScreenState();
}

class _OwnerEditParkingScreenState extends State<OwnerEditParkingScreen> {
  late TextEditingController titleCtrl;
  late TextEditingController descCtrl;
  late TextEditingController priceCtrl;
  bool loading = false;

  @override
  void initState() {
    super.initState();
    titleCtrl = TextEditingController(text: widget.parking['title']);
    descCtrl = TextEditingController(text: widget.parking['description']);
    priceCtrl = TextEditingController(text: widget.parking['price_per_hour'].toString());
  }

  Future<void> _update() async {
    setState(() => loading = true);
    try {
      await ApiService.createParking({
        "title": titleCtrl.text,
        "description": descCtrl.text,
        "price_per_hour": double.tryParse(priceCtrl.text) ?? 0,
        "latitude": widget.parking['latitude'],
        "longitude": widget.parking['longitude'],
      });
      if (!mounted) return;
      Navigator.pop(context);
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text("Error: $e")));
    } finally {
      setState(() => loading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text("Edit Parking")),
      body: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          children: [
            TextField(controller: titleCtrl, decoration: const InputDecoration(labelText: "Title")),
            TextField(controller: descCtrl, decoration: const InputDecoration(labelText: "Description")),
            TextField(controller: priceCtrl, decoration: const InputDecoration(labelText: "Price per hour")),
            const SizedBox(height: 20),
            loading
                ? const CircularProgressIndicator()
                : ElevatedButton(onPressed: _update, child: const Text("Update")),
          ],
        ),
      ),
    );
  }
}
