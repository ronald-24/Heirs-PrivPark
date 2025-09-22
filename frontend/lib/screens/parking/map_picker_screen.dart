import 'package:flutter/material.dart';
import 'package:google_maps_flutter/google_maps_flutter.dart';

class MapPickerScreen extends StatefulWidget {
  const MapPickerScreen({super.key});

  @override
  State<MapPickerScreen> createState() => _MapPickerScreenState();
}

class _MapPickerScreenState extends State<MapPickerScreen> {
  LatLng? pickedLocation;

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text("Pick Location")),
      body: GoogleMap(
        initialCameraPosition: const CameraPosition(
          target: LatLng(48.8566, 2.3522), // Paris par défaut
          zoom: 12,
        ),
        onTap: (pos) {
          setState(() {
            pickedLocation = pos;
          });
        },
        markers: pickedLocation != null
            ? {
                Marker(markerId: const MarkerId("picked"), position: pickedLocation!)
              }
            : {},
      ),
      floatingActionButton: FloatingActionButton(
        onPressed: () {
          if (pickedLocation != null) {
            Navigator.pop(context, pickedLocation);
          }
        },
        child: const Icon(Icons.check),
      ),
    );
  }
}
