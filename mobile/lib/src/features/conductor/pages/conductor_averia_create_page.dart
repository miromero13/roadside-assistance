import 'dart:async';
import 'dart:io';

import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_sound/flutter_sound.dart';
import 'package:google_maps_flutter/google_maps_flutter.dart';
import 'package:permission_handler/permission_handler.dart';

import '../../../core/services/api_client.dart';
import '../../../core/services/native_device_service.dart';
import '../../../core/services/session_controller.dart';
import '../conductor_api_service.dart';
import '../conductor_models.dart';
import 'conductor_ubicacion_mapa_page.dart';

class ConductorAveriaCreatePage extends StatefulWidget {
  const ConductorAveriaCreatePage({
    super.key,
    required this.session,
    required this.api,
  });

  final SessionController session;
  final ConductorApiService api;

  @override
  State<ConductorAveriaCreatePage> createState() =>
      _ConductorAveriaCreatePageState();
}

class _ConductorAveriaCreatePageState extends State<ConductorAveriaCreatePage> {
  final _formKey = GlobalKey<FormState>();
  final _descripcionCtrl = TextEditingController();

  final NativeDeviceService _native = NativeDeviceService();
  final FlutterSoundRecorder _recorder = FlutterSoundRecorder();

  GoogleMapController? _mapController;
  List<VehiculoItem> _vehiculos = const [];
  String? _vehiculoId;
  LatLng _ubicacionSeleccionada = const LatLng(-16.5000, -68.1500);
  String? _imagenPath;
  String? _audioPath;
  String _prioridad = 'media';
  bool _loading = false;
  bool _recorderReady = false;
  bool _grabandoAudio = false;
  Duration _duracionAudio = Duration.zero;
  Timer? _audioTimer;
  Future<String?>? _googleMapsApiKeyFuture;
  String? _error;

  @override
  void initState() {
    super.initState();
    _load();
    _prepararGrabador();
    _cargarUbicacionInicial();
    _googleMapsApiKeyFuture = _cargarGoogleMapsApiKey();
  }

  @override
  void dispose() {
    _audioTimer?.cancel();
    unawaited(_recorder.closeRecorder());
    _descripcionCtrl.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Nueva avería')),
      body: RefreshIndicator(
        onRefresh: _load,
        child: ListView(
          physics: const AlwaysScrollableScrollPhysics(),
          padding: const EdgeInsets.all(16),
          children: [
            if (_loading)
              const Padding(
                padding: EdgeInsets.only(bottom: 12),
                child: LinearProgressIndicator(),
              ),
            const Text(
              'Crear avería',
              style: TextStyle(fontSize: 20, fontWeight: FontWeight.w700),
            ),
            const SizedBox(height: 8),
            const Text('Completa los datos para registrar una nueva avería.'),
            const SizedBox(height: 16),
            if (_vehiculos.isEmpty)
              Card(
                color: Theme.of(context).colorScheme.surfaceContainerHighest,
                child: const Padding(
                  padding: EdgeInsets.all(12),
                  child: Text(
                    'Primero registra un vehículo para poder crear averías.',
                  ),
                ),
              ),
            Card(
              child: Padding(
                padding: const EdgeInsets.all(12),
                child: Form(
                  key: _formKey,
                  child: Column(
                    children: [
                      DropdownButtonFormField<String>(
                        key: ValueKey(_vehiculoId),
                        initialValue: _vehiculoId,
                        decoration:
                            const InputDecoration(labelText: 'Vehículo'),
                        items: _vehiculos
                            .map(
                              (vehiculo) => DropdownMenuItem<String>(
                                value: vehiculo.id,
                                child: Text(
                                  '${vehiculo.marca} ${vehiculo.modelo} (${vehiculo.placa})',
                                ),
                              ),
                            )
                            .toList(),
                        validator: (value) {
                          if (value == null || value.isEmpty) {
                            return 'Selecciona un vehículo';
                          }
                          return null;
                        },
                        onChanged: (value) {
                          setState(() {
                            _vehiculoId = value;
                          });
                        },
                      ),
                      const SizedBox(height: 10),
                      TextFormField(
                        controller: _descripcionCtrl,
                        maxLines: 2,
                        decoration:
                            const InputDecoration(
                              labelText: 'Descripción (opcional)',
                            ),
                      ),
                      const SizedBox(height: 10),
                      _buildMapa(),
                      const SizedBox(height: 10),
                      Row(
                        children: [
                          Expanded(
                            child: FilledButton.tonalIcon(
                              onPressed: _loading ? null : _usarUbicacionActual,
                              icon: const Icon(Icons.my_location),
                              label: const Text('Usar mi ubicación'),
                            ),
                          ),
                        ],
                      ),
                      const SizedBox(height: 8),
                      Row(
                        children: [
                          Expanded(
                            child: OutlinedButton.icon(
                              onPressed: _loading ? null : _abrirMapaCompleto,
                              icon: const Icon(Icons.map_outlined),
                              label: const Text('Abrir mapa completo'),
                            ),
                          ),
                        ],
                      ),
                      const SizedBox(height: 10),
                      _buildImagenAdjunta(),
                      const SizedBox(height: 10),
                      _buildGrabadorAudio(),
                      const SizedBox(height: 8),
                      Text(
                        'Adjuntos: ${_imagenPath == null ? 'sin imagen' : 'imagen lista'} / ${_audioPath == null ? 'sin audio' : 'audio listo'}',
                        style: Theme.of(context).textTheme.bodySmall,
                      ),
                      const SizedBox(height: 10),
                      DropdownButtonFormField<String>(
                        key: ValueKey(_prioridad),
                        initialValue: _prioridad,
                        decoration:
                            const InputDecoration(labelText: 'Prioridad'),
                        items: const [
                          DropdownMenuItem(value: 'baja', child: Text('Baja')),
                          DropdownMenuItem(value: 'media', child: Text('Media')),
                          DropdownMenuItem(value: 'alta', child: Text('Alta')),
                          DropdownMenuItem(
                            value: 'critica',
                            child: Text('Crítica'),
                          ),
                        ],
                        onChanged: (value) {
                          if (value == null) {
                            return;
                          }
                          setState(() {
                            _prioridad = value;
                          });
                        },
                      ),
                      if (_error != null) ...[
                        const SizedBox(height: 10),
                        Text(
                          _error!,
                          style: TextStyle(
                            color: Theme.of(context).colorScheme.error,
                          ),
                        ),
                      ],
                      const SizedBox(height: 12),
                      FilledButton(
                        onPressed: _loading || _vehiculos.isEmpty || _grabandoAudio
                            ? null
                            : _crearAveria,
                        child: Text(_loading ? 'Guardando...' : 'Registrar'),
                      ),
                    ],
                  ),
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Future<void> _load() async {
    final token = widget.session.token;
    if (token == null || token.isEmpty) {
      return;
    }

    setState(() {
      _loading = true;
      _error = null;
    });

    try {
      final vehiculos = await widget.api.listVehiculos(token);

      if (!mounted) {
        return;
      }

      setState(() {
        _vehiculos = vehiculos;
        _vehiculoId = _vehiculoId ?? (vehiculos.isNotEmpty ? vehiculos.first.id : null);
      });
    } on ApiException catch (e) {
      if (!mounted) {
        return;
      }
      setState(() {
        _error = e.message;
      });
    } finally {
      if (mounted) {
        setState(() {
          _loading = false;
        });
      }
    }
  }

  Future<void> _prepararGrabador() async {
    try {
      await _recorder.openRecorder();
      if (!mounted) {
        return;
      }
      setState(() {
        _recorderReady = true;
      });
    } catch (e) {
      if (!mounted) {
        return;
      }
      setState(() {
        _error = 'No se pudo inicializar el micrófono: $e';
      });
    }
  }

  Future<void> _cargarUbicacionInicial() async {
    try {
      final position = await _native.obtenerUbicacionActual();
      if (!mounted) {
        return;
      }
      _actualizarUbicacion(LatLng(position.latitude, position.longitude));
    } catch (_) {
      // Se mantiene la ubicación por defecto si no hay permiso.
    }
  }

  Future<void> _crearAveria() async {
    if (!_formKey.currentState!.validate()) {
      return;
    }

    final token = widget.session.token;
    if (token == null || token.isEmpty || _vehiculoId == null) {
      return;
    }

    setState(() {
      _loading = true;
      _error = null;
    });

    var shouldClose = false;

    try {
      await widget.api.createAveria(
        token,
        vehiculoId: _vehiculoId!,
        descripcion: _descripcionCtrl.text,
        latitud: _ubicacionSeleccionada.latitude,
        longitud: _ubicacionSeleccionada.longitude,
        prioridad: _prioridad,
        direccion: _direccionSeleccionada,
        imagePath: _imagenPath,
        audioPath: _audioPath,
      );

      if (!mounted) {
        return;
      }

      shouldClose = true;
      Navigator.of(context).pop('Avería registrada correctamente');
    } on ApiException catch (e) {
      if (!mounted) {
        return;
      }
      setState(() {
        _error = e.message;
      });
    } finally {
      if (mounted && !shouldClose) {
        setState(() {
          _loading = false;
        });
      }
    }
  }

  Future<void> _usarUbicacionActual() async {
    setState(() {
      _loading = true;
      _error = null;
    });

    try {
      final position = await _native.obtenerUbicacionActual();
      if (!mounted) {
        return;
      }
      _actualizarUbicacion(LatLng(position.latitude, position.longitude));
    } catch (e) {
      if (!mounted) {
        return;
      }
      setState(() {
        _error = '$e';
      });
    } finally {
      if (mounted) {
        setState(() {
          _loading = false;
        });
      }
    }
  }

  Widget _buildMapa() {
    return FutureBuilder<String?>(
      future: _googleMapsApiKeyFuture,
      builder: (context, snapshot) {
        if (snapshot.connectionState != ConnectionState.done) {
          return const SizedBox(
            height: 260,
            child: Center(child: CircularProgressIndicator()),
          );
        }

        if ((snapshot.data ?? '').isEmpty) {
          return Card(
            color: Theme.of(context).colorScheme.errorContainer,
            child: const Padding(
              padding: EdgeInsets.all(12),
              child: Text(
                'Falta configurar GOOGLE_MAPS_API_KEY en Android. Agrega la clave en `mobile/android/local.properties`.',
              ),
            ),
          );
        }

        return ClipRRect(
          borderRadius: BorderRadius.circular(12),
          child: SizedBox(
            height: 260,
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
                  markerId: const MarkerId('averia'),
                  position: _ubicacionSeleccionada,
                ),
              },
              myLocationButtonEnabled: false,
              myLocationEnabled: false,
              zoomControlsEnabled: false,
              onTap: _actualizarUbicacion,
            ),
          ),
        );
      },
    );
  }

  Widget _buildGrabadorAudio() {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(12),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              _grabandoAudio ? 'Grabando audio en vivo' : 'Audio en vivo',
              style: const TextStyle(fontWeight: FontWeight.w600),
            ),
            const SizedBox(height: 6),
            Text(
              _grabandoAudio
                  ? 'Duración: ${_formatearDuracion(_duracionAudio)}'
                  : (_audioPath == null ? 'Aún no grabaste audio.' : 'Audio listo para enviar.'),
              style: Theme.of(context).textTheme.bodySmall,
            ),
            const SizedBox(height: 10),
            Row(
              children: [
                Expanded(
                  child: FilledButton.icon(
                    onPressed: _loading || !_recorderReady ? null : _alternarGrabacion,
                    icon: Icon(_grabandoAudio ? Icons.stop : Icons.mic),
                    label: Text(_grabandoAudio ? 'Detener grabación' : 'Grabar audio'),
                  ),
                ),
                const SizedBox(width: 8),
                Expanded(
                  child: OutlinedButton.icon(
                    onPressed: _loading || _grabandoAudio || _audioPath == null
                        ? null
                        : _limpiarAudio,
                    icon: const Icon(Icons.delete_outline),
                    label: const Text('Borrar audio'),
                  ),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildImagenAdjunta() {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(12),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              'Imagen para diagnóstico',
              style: TextStyle(fontWeight: FontWeight.w600),
            ),
            const SizedBox(height: 6),
            Text(
              _imagenPath == null
                  ? 'Adjunta una foto para ayudar a la IA con el diagnóstico.'
                  : 'Imagen lista para enviar.',
              style: Theme.of(context).textTheme.bodySmall,
            ),
            if (_imagenPath != null) ...[
              const SizedBox(height: 10),
              ClipRRect(
                borderRadius: BorderRadius.circular(12),
                child: Image.file(
                  File(_imagenPath!),
                  height: 180,
                  width: double.infinity,
                  fit: BoxFit.cover,
                ),
              ),
            ],
            const SizedBox(height: 10),
            Row(
              children: [
                Expanded(
                  child: FilledButton.icon(
                    onPressed: _loading ? null : _tomarImagen,
                    icon: const Icon(Icons.photo_camera_outlined),
                    label: const Text('Tomar foto'),
                  ),
                ),
                const SizedBox(width: 8),
                Expanded(
                  child: OutlinedButton.icon(
                    onPressed: _loading ? null : _elegirImagen,
                    icon: const Icon(Icons.photo_library_outlined),
                    label: const Text('Galería'),
                  ),
                ),
                const SizedBox(width: 8),
                IconButton(
                  onPressed: _loading || _imagenPath == null ? null : _limpiarImagen,
                  icon: const Icon(Icons.delete_outline),
                  tooltip: 'Quitar imagen',
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }

  Future<void> _alternarGrabacion() async {
    if (_grabandoAudio) {
      await _detenerGrabacion();
      return;
    }

    final permiso = await Permission.microphone.request();
    if (!permiso.isGranted) {
      if (!mounted) {
        return;
      }
      setState(() {
        _error = 'Necesitamos permiso de micrófono para grabar el audio';
      });
      return;
    }

    final ruta = '${Directory.systemTemp.path}/averia_${DateTime.now().millisecondsSinceEpoch}.m4a';

    try {
      await _recorder.startRecorder(
        toFile: ruta,
        codec: Codec.aacMP4,
        bitRate: 128000,
        sampleRate: 44100,
      );
      _audioTimer?.cancel();
      if (!mounted) {
        return;
      }
      setState(() {
        _grabandoAudio = true;
        _audioPath = ruta;
        _duracionAudio = Duration.zero;
      });
      _audioTimer = Timer.periodic(const Duration(seconds: 1), (_) {
        if (!mounted) {
          return;
        }
        setState(() {
          _duracionAudio += const Duration(seconds: 1);
        });
      });
    } catch (e) {
      if (!mounted) {
        return;
      }
      setState(() {
        _error = 'No se pudo iniciar la grabación: $e';
      });
    }
  }

  Future<void> _detenerGrabacion() async {
    try {
      final path = await _recorder.stopRecorder();
      _audioTimer?.cancel();
      if (!mounted) {
        return;
      }
      setState(() {
        _grabandoAudio = false;
        if (path != null && path.isNotEmpty) {
          _audioPath = path;
        }
      });
    } catch (e) {
      if (!mounted) {
        return;
      }
      setState(() {
        _grabandoAudio = false;
        _error = 'No se pudo detener la grabación: $e';
      });
    }
  }

  void _limpiarAudio() {
    setState(() {
      _audioPath = null;
      _duracionAudio = Duration.zero;
    });
  }

  Future<void> _tomarImagen() async {
    try {
      final imagen = await _native.tomarImagen();
      if (!mounted || imagen == null) {
        return;
      }
      setState(() {
        _imagenPath = imagen.path;
      });
    } catch (e) {
      if (!mounted) {
        return;
      }
      setState(() {
        _error = 'No se pudo tomar la foto: $e';
      });
    }
  }

  Future<void> _elegirImagen() async {
    try {
      final imagen = await _native.elegirImagenGaleria();
      if (!mounted || imagen == null) {
        return;
      }
      setState(() {
        _imagenPath = imagen.path;
      });
    } catch (e) {
      if (!mounted) {
        return;
      }
      setState(() {
        _error = 'No se pudo elegir la foto: $e';
      });
    }
  }

  void _limpiarImagen() {
    setState(() {
      _imagenPath = null;
    });
  }

  Future<void> _abrirMapaCompleto() async {
    final nuevaUbicacion = await Navigator.of(context).push<LatLng>(
      MaterialPageRoute(
        builder: (_) => ConductorUbicacionMapaPage(
          ubicacionInicial: _ubicacionSeleccionada,
        ),
      ),
    );

    if (!mounted || nuevaUbicacion == null) {
      return;
    }

    _actualizarUbicacion(nuevaUbicacion);
  }

  void _actualizarUbicacion(LatLng ubicacion) {
    setState(() {
      _ubicacionSeleccionada = ubicacion;
    });

    unawaited(
      _mapController?.animateCamera(
        CameraUpdate.newLatLng(ubicacion),
      ),
    );
  }

  String get _direccionSeleccionada {
    return 'Lat ${_ubicacionSeleccionada.latitude.toStringAsFixed(6)}, '
        'Lng ${_ubicacionSeleccionada.longitude.toStringAsFixed(6)}';
  }

  String _formatearDuracion(Duration duration) {
    final minutes = duration.inMinutes.remainder(60).toString().padLeft(2, '0');
    final seconds = duration.inSeconds.remainder(60).toString().padLeft(2, '0');
    return '$minutes:$seconds';
  }

  Future<String?> _cargarGoogleMapsApiKey() async {
    try {
      const channel = MethodChannel('app/google_maps_config');
      final key = await channel.invokeMethod<String>('getGoogleMapsApiKey');
      return key;
    } on PlatformException {
      return null;
    }
  }
}
