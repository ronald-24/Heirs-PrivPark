## Driver Search & Google Map Integration (Flutter + FastAPI)

This guide explains how to integrate the backend search API into a Flutter app using Google Maps. You will let drivers search parking spots by location/date/price, show results on a map and list, and open directions to a selected spot.

### Prerequisites

- Backend running FastAPI with the search route: `GET /api/parking/search`
- Google Cloud project with Maps SDK for Android/iOS enabled and API key
- Flutter 3.x

### Backend API Summary

- Endpoint: `GET /api/parking/search`
- Query parameters:
  - `lat` (float): center latitude
  - `lng` (float): center longitude
  - `radius_m` (int, default 3000, min 100, max 20000)
  - `start_time` (ISO 8601, optional) and `end_time` (ISO 8601, optional). If one is provided, both are required
  - `max_price` (float, optional)
  - `sort` ("distance" | "price", default "distance")
  - `limit` (1..100, default 50)
  - `offset` (>= 0, default 0)
- Response: JSON array of objects
  - `id` (int), `title` (string), `address` (string|null),
  - `latitude` (float), `longitude` (float),
  - `price_per_hour` (float|null), `distance_m` (float)

Example:

```http
GET /api/parking/search?lat=6.5244&lng=3.3792&radius_m=3000&start_time=2025-09-26T10:00:00Z&end_time=2025-09-26T12:00:00Z&max_price=2000&sort=distance&limit=50
```

### Flutter Setup

Add dependencies in `pubspec.yaml`:

```yaml
dependencies:
  flutter:
    sdk: flutter
  google_maps_flutter: ^2.7.0
  geolocator: ^12.0.0
  dio: ^5.5.0+1
  url_launcher: ^6.3.0
```

Android configuration:

- Add your Maps API key to `android/app/src/main/AndroidManifest.xml` inside the `<application>` tag:

```xml
<meta-data android:name="com.google.android.maps.v2.API_KEY" android:value="YOUR_API_KEY"/>
```

iOS configuration:

- In `ios/Runner/AppDelegate.swift` or `AppDelegate.m`, provide API key or use Info.plist with `GMSApiKey`.

### Data Model for Search Result

```dart
class ParkingSearchResult {
  final int id;
  final String title;
  final String? address;
  final double latitude;
  final double longitude;
  final double? pricePerHour;
  final double distanceM;

  ParkingSearchResult({
    required this.id,
    required this.title,
    this.address,
    required this.latitude,
    required this.longitude,
    this.pricePerHour,
    required this.distanceM,
  });

  factory ParkingSearchResult.fromJson(Map<String, dynamic> j) => ParkingSearchResult(
        id: j['id'],
        title: j['title'],
        address: j['address'],
        latitude: (j['latitude'] as num).toDouble(),
        longitude: (j['longitude'] as num).toDouble(),
        pricePerHour: (j['price_per_hour'] as num?)?.toDouble(),
        distanceM: (j['distance_m'] as num).toDouble(),
      );
}
```

### Calling the Backend Search API

```dart
import 'package:dio/dio.dart';

class ParkingApiClient {
  final Dio _dio;

  ParkingApiClient(String baseUrl)
      : _dio = Dio(BaseOptions(baseUrl: baseUrl));

  Future<List<ParkingSearchResult>> search({
    required double lat,
    required double lng,
    int radiusM = 3000,
    DateTime? startTime,
    DateTime? endTime,
    double? maxPrice,
    String sort = 'distance',
    int limit = 50,
    int offset = 0,
    String? bearerToken,
  }) async {
    final params = <String, dynamic>{
      'lat': lat,
      'lng': lng,
      'radius_m': radiusM,
      if (startTime != null && endTime != null) 'start_time': startTime.toUtc().toIso8601String(),
      if (startTime != null && endTime != null) 'end_time': endTime.toUtc().toIso8601String(),
      if (maxPrice != null) 'max_price': maxPrice,
      'sort': sort,
      'limit': limit,
      'offset': offset,
    };
    final headers = <String, dynamic>{
      if (bearerToken != null) 'Authorization': 'Bearer $bearerToken',
    };
    final resp = await _dio.get('/parking/search', queryParameters: params, options: Options(headers: headers));
    final data = (resp.data as List).cast<Map<String, dynamic>>();
    return data.map(ParkingSearchResult.fromJson).toList();
  }
}
```

Notes:

- For Android Emulator use `http://10.0.2.2:8000/api` as base URL if backend runs on host at `localhost:8000`.
- Ensure date pairs: both `start_time` and `end_time` must be provided together.

### Location Permission and Current Position

```dart
import 'package:geolocator/geolocator.dart';

Future<Position?> getCurrentPosition() async {
  final perm = await Geolocator.requestPermission();
  if (perm == LocationPermission.denied || perm == LocationPermission.deniedForever) {
    return null;
  }
  return Geolocator.getCurrentPosition();
}
```

### Rendering Google Map and Markers

```dart
import 'package:flutter/material.dart';
import 'package:google_maps_flutter/google_maps_flutter.dart';
import 'package:url_launcher/url_launcher.dart';

class SearchMapView extends StatefulWidget {
  final ParkingApiClient api;
  const SearchMapView({super.key, required this.api});

  @override
  State<SearchMapView> createState() => _SearchMapViewState();
}

class _SearchMapViewState extends State<SearchMapView> {
  GoogleMapController? _controller;
  LatLng _center = const LatLng(6.5244, 3.3792); // default center
  Set<Marker> _markers = {};
  List<ParkingSearchResult> _results = [];

  @override
  void initState() {
    super.initState();
    _bootstrap();
  }

  Future<void> _bootstrap() async {
    final pos = await getCurrentPosition();
    if (pos != null) {
      setState(() {
        _center = LatLng(pos.latitude, pos.longitude);
      });
    }
    await _search();
  }

  Future<void> _search() async {
    final items = await widget.api.search(lat: _center.latitude, lng: _center.longitude, radiusM: 3000);
    setState(() {
      _results = items;
      _markers = items
          .map((r) => Marker(
                markerId: MarkerId('p_${r.id}'),
                position: LatLng(r.latitude, r.longitude),
                infoWindow: InfoWindow(
                  title: r.title,
                  snippet: '${(r.distanceM / 1000).toStringAsFixed(1)} km • \\${r.pricePerHour ?? '-'}',
                ),
                onTap: () => _animateTo(r.latitude, r.longitude),
              ))
          .toSet();
    });
  }

  Future<void> _animateTo(double lat, double lng) async {
    await _controller?.animateCamera(CameraUpdate.newLatLngZoom(LatLng(lat, lng), 15));
  }

  Future<void> _openDirections(ParkingSearchResult r) async {
    final uri = Uri.parse('google.navigation:q=${r.latitude},${r.longitude}');
    if (await canLaunchUrl(uri)) {
      await launchUrl(uri);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Search Parking'), actions: [
        IconButton(onPressed: _search, icon: const Icon(Icons.refresh)),
      ]),
      body: Stack(children: [
        GoogleMap(
          initialCameraPosition: CameraPosition(target: _center, zoom: 13),
          onMapCreated: (c) => _controller = c,
          markers: _markers,
          myLocationEnabled: true,
        ),
        Positioned(
          left: 8,
          right: 8,
          bottom: 12,
          child: SizedBox(
            height: 140,
            child: Card(
              child: ListView.builder(
                scrollDirection: Axis.horizontal,
                itemCount: _results.length,
                itemBuilder: (context, i) {
                  final r = _results[i];
                  return InkWell(
                    onTap: () => _animateTo(r.latitude, r.longitude),
                    child: Container(
                      width: 240,
                      padding: const EdgeInsets.all(12),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(r.title, maxLines: 1, overflow: TextOverflow.ellipsis),
                          const SizedBox(height: 4),
                          Text(r.address ?? ''),
                          const Spacer(),
                          Row(
                            mainAxisAlignment: MainAxisAlignment.spaceBetween,
                            children: [
                              Text('${(r.distanceM/1000).toStringAsFixed(1)} km'),
                              Text(r.pricePerHour != null ? '\\${r.pricePerHour} /h' : '-'),
                              IconButton(icon: const Icon(Icons.directions), onPressed: () => _openDirections(r)),
                            ],
                          )
                        ],
                      ),
                    ),
                  );
                },
              ),
            ),
          ),
        ),
      ]),
      floatingActionButton: FloatingActionButton.extended(
        onPressed: _search,
        icon: const Icon(Icons.search),
        label: const Text('Search'),
      ),
    );
  }
}
```

### Tips and Best Practices

- Synchronize map and list: on camera movement, re-run search with new center and radius based on viewport
- Debounce searches (e.g., 300–500 ms) to avoid excessive calls while panning
- Use pagination with `limit`/`offset` for dense urban areas
- Cache last results for current viewport and filters to improve UX
- Secure calls with Authorization header when needed; avoid exposing owner PII before reservation

### Troubleshooting

- If no markers appear: verify base URL and emulator networking; check that backend returns 200 with data
- If dates are rejected: send ISO 8601 with timezone, e.g., `2025-09-26T10:00:00Z`
- If map is blank on Android: ensure a valid Google Maps API key is configured in `AndroidManifest.xml`
