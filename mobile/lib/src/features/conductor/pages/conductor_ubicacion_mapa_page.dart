import 'dart:async';

import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:google_maps_flutter/google_maps_flutter.dart';

class ConductorUbicacionMapaPage extends StatefulWidget {
  const ConductorUbicacionMapaPage({
    super.key,
    required this.ubicacionInicial,
  });

  final LatLng ubicacionInicial;

  @override
  State<ConductorUbicacionMapaPage> createState() =>
      _ConductorUbicacionMapaPageState();
}

class _ConductorUbicacionMapaPageState extends State<ConductorUbicacionMapaPage> {
  GoogleMapController? _mapController;
  late LatLng _ubicacionSeleccionada;
  Future<String?>? _googleMapsApiKeyFuture;

  @override
  void initState() {
    super.initState();
    _ubicacionSeleccionada = widget.ubicacionInicial;
    _googleMapsApiKeyFuture = _cargarGoogleMapsApiKey();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Seleccionar ubicación')),
      body: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            Expanded(child: _buildMapa()),
            const SizedBox(height: 12),
            Text(
              'Lat ${_ubicacionSeleccionada.latitude.toStringAsFixed(6)} · '
              'Lng ${_ubicacionSeleccionada.longitude.toStringAsFixed(6)}',
              textAlign: TextAlign.center,
            ),
            const SizedBox(height: 12),
            FilledButton.icon(
              onPressed: () => Navigator.of(context).pop(_ubicacionSeleccionada),
              icon: const Icon(Icons.check),
              label: const Text('Usar esta ubicación'),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildMapa() {
    return FutureBuilder<String?>(
      future: _googleMapsApiKeyFuture,
      builder: (context, snapshot) {
        if (snapshot.connectionState != ConnectionState.done) {
          return const Center(child: CircularProgressIndicator());
        }

        if ((snapshot.data ?? '').isEmpty) {
          return Card(
            color: Theme.of(context).colorScheme.errorContainer,
            child: const Padding(
              padding: EdgeInsets.all(12),
              child: Text(
                'Falta configurar GOOGLE_MAPS_API_KEY en Android.',
              ),
            ),
          );
        }

        return ClipRRect(
          borderRadius: BorderRadius.circular(16),
          child: GoogleMap(
            initialCameraPosition: CameraPosition(
              target: _ubicacionSeleccionada,
              zoom: 15,
            ),
            onMapCreated: (controller) {
              _mapController = controller;
              unawaited(
                controller.animateCamera(
                  CameraUpdate.newLatLngZoom(_ubicacionSeleccionada, 15),
                ),
              );
            },
            markers: {
              Marker(
                markerId: const MarkerId('seleccion'),
                position: _ubicacionSeleccionada,
              ),
            },
            myLocationButtonEnabled: false,
            myLocationEnabled: false,
            zoomControlsEnabled: false,
            onTap: _actualizarUbicacion,
          ),
        );
      },
    );
  }

  void _actualizarUbicacion(LatLng ubicacion) {
    setState(() {
      _ubicacionSeleccionada = ubicacion;
    });

    unawaited(
      _mapController?.animateCamera(CameraUpdate.newLatLng(ubicacion)),
    );
  }

  Future<String?> _cargarGoogleMapsApiKey() async {
    try {
      const channel = MethodChannel('app/google_maps_config');
      return await channel.invokeMethod<String>('getGoogleMapsApiKey');
    } on PlatformException {
      return null;
    }
  }
}
