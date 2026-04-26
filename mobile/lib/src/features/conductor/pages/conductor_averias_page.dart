import 'package:flutter/material.dart';
import 'dart:io';

import '../../../core/services/api_client.dart';
import '../../../core/services/native_device_service.dart';
import '../../../core/services/session_controller.dart';
import '../conductor_api_service.dart';
import '../conductor_models.dart';

class ConductorAveriasPage extends StatefulWidget {
  const ConductorAveriasPage({
    super.key,
    required this.session,
    required this.api,
  });

  final SessionController session;
  final ConductorApiService api;

  @override
  State<ConductorAveriasPage> createState() => _ConductorAveriasPageState();
}

class _ConductorAveriasPageState extends State<ConductorAveriasPage> {
  final _formKey = GlobalKey<FormState>();
  final _descripcionCtrl = TextEditingController();
  final _latitudCtrl = TextEditingController();
  final _longitudCtrl = TextEditingController();
  final _direccionCtrl = TextEditingController();

  final NativeDeviceService _native = NativeDeviceService();

  List<VehiculoItem> _vehiculos = const [];
  List<AveriaItem> _averias = const [];
  String? _vehiculoId;
  String? _fotoPath;
  String? _audioPath;
  String _prioridad = 'media';
  bool _loading = false;
  String? _error;

  @override
  void initState() {
    super.initState();
    _latitudCtrl.text = '-16.5000';
    _longitudCtrl.text = '-68.1500';
    _load();
  }

  @override
  void dispose() {
    _descripcionCtrl.dispose();
    _latitudCtrl.dispose();
    _longitudCtrl.dispose();
    _direccionCtrl.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return RefreshIndicator(
      onRefresh: _load,
      child: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          if (_loading)
            const Padding(
              padding: EdgeInsets.only(bottom: 12),
              child: LinearProgressIndicator(),
            ),
          const Text(
            'Averías',
            style: TextStyle(fontSize: 20, fontWeight: FontWeight.w700),
          ),
          const SizedBox(height: 8),
          const Text('Registra una avería asociada a uno de tus vehículos.'),
          const SizedBox(height: 8),
          Text(
            'Vehículos: ${_vehiculos.length} · Averías: ${_averias.length}',
            style: Theme.of(context).textTheme.bodySmall,
          ),
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
          if (_vehiculos.isEmpty) const SizedBox(height: 12),
          Card(
            child: Padding(
              padding: const EdgeInsets.all(12),
              child: Form(
                key: _formKey,
                child: Column(
                  children: [
                    DropdownButtonFormField<String>(
                      value: _vehiculoId,
                      decoration: const InputDecoration(labelText: 'Vehículo'),
                      items: _vehiculos
                          .map(
                            (vehiculo) => DropdownMenuItem<String>(
                              value: vehiculo.id,
                              child: Text(
                                  '${vehiculo.marca} ${vehiculo.modelo} (${vehiculo.placa})'),
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
                          const InputDecoration(labelText: 'Descripción'),
                      validator: _required,
                    ),
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
                    const SizedBox(height: 10),
                    Row(
                      children: [
                        Expanded(
                          child: OutlinedButton.icon(
                            onPressed: _loading ? null : _tomarFoto,
                            icon: const Icon(Icons.photo_camera_outlined),
                            label: const Text('Tomar foto'),
                          ),
                        ),
                        const SizedBox(width: 8),
                        Expanded(
                          child: OutlinedButton.icon(
                            onPressed: _loading ? null : _elegirFotoGaleria,
                            icon: const Icon(Icons.photo_library_outlined),
                            label: const Text('Galería'),
                          ),
                        ),
                      ],
                    ),
                    const SizedBox(height: 8),
                    Row(
                      children: [
                        Expanded(
                          child: OutlinedButton.icon(
                            onPressed: _loading ? null : _elegirAudio,
                            icon: const Icon(Icons.audio_file_outlined),
                            label: const Text('Adjuntar audio'),
                          ),
                        ),
                        const SizedBox(width: 8),
                        Expanded(
                          child: OutlinedButton.icon(
                            onPressed: _loading ||
                                    (_fotoPath == null && _audioPath == null)
                                ? null
                                : _limpiarAdjuntos,
                            icon: const Icon(Icons.delete_outline),
                            label: const Text('Limpiar adjuntos'),
                          ),
                        ),
                      ],
                    ),
                    if (_fotoPath != null) ...[
                      const SizedBox(height: 10),
                      ClipRRect(
                        borderRadius: BorderRadius.circular(8),
                        child: Image.file(
                          File(_fotoPath!),
                          height: 120,
                          fit: BoxFit.cover,
                        ),
                      ),
                      const SizedBox(height: 6),
                      Text(
                        'Foto lista para anexar en la avería',
                        style: Theme.of(context).textTheme.bodySmall,
                      ),
                    ],
                    if (_audioPath != null) ...[
                      const SizedBox(height: 6),
                      Text(
                        'Audio listo para anexar: ${_audioPath!.split(Platform.pathSeparator).last}',
                        style: Theme.of(context).textTheme.bodySmall,
                      ),
                    ],
                    Row(
                      children: [
                        Expanded(
                          child: TextFormField(
                            controller: _latitudCtrl,
                            keyboardType: const TextInputType.numberWithOptions(
                                decimal: true),
                            decoration:
                                const InputDecoration(labelText: 'Latitud'),
                            validator: _required,
                          ),
                        ),
                        const SizedBox(width: 10),
                        Expanded(
                          child: TextFormField(
                            controller: _longitudCtrl,
                            keyboardType: const TextInputType.numberWithOptions(
                                decimal: true),
                            decoration:
                                const InputDecoration(labelText: 'Longitud'),
                            validator: _required,
                          ),
                        ),
                      ],
                    ),
                    const SizedBox(height: 10),
                    TextFormField(
                      controller: _direccionCtrl,
                      decoration: const InputDecoration(
                          labelText: 'Dirección (opcional)'),
                    ),
                    const SizedBox(height: 10),
                    DropdownButtonFormField<String>(
                      value: _prioridad,
                      decoration: const InputDecoration(labelText: 'Prioridad'),
                      items: const [
                        DropdownMenuItem(value: 'baja', child: Text('Baja')),
                        DropdownMenuItem(value: 'media', child: Text('Media')),
                        DropdownMenuItem(value: 'alta', child: Text('Alta')),
                        DropdownMenuItem(
                            value: 'critica', child: Text('Critica')),
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
                      Text(_error!,
                          style: TextStyle(
                              color: Theme.of(context).colorScheme.error)),
                    ],
                    const SizedBox(height: 12),
                    FilledButton(
                      onPressed:
                          _loading || _vehiculos.isEmpty ? null : _crearAveria,
                      child:
                          Text(_loading ? 'Guardando...' : 'Registrar avería'),
                    ),
                  ],
                ),
              ),
            ),
          ),
          const SizedBox(height: 16),
          if (_averias.isEmpty)
            const Card(
              child: Padding(
                padding: EdgeInsets.all(16),
                child: Text('No tienes averías registradas.'),
              ),
            ),
          ..._averias.map((averia) {
            return Card(
              child: ListTile(
                title: Text(averia.descripcion),
                subtitle: Text('${averia.estado} · ${averia.prioridad}'),
                trailing: Text('#${averia.id.substring(0, 8)}'),
              ),
            );
          }),
        ],
      ),
    );
  }

  String? _required(String? value) {
    if (value == null || value.trim().isEmpty) {
      return 'Campo requerido';
    }
    return null;
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
      final averias = await widget.api.listAverias(token);

      if (!mounted) {
        return;
      }
      setState(() {
        _vehiculos = vehiculos;
        _averias = averias;
        _vehiculoId =
            _vehiculoId ?? (vehiculos.isNotEmpty ? vehiculos.first.id : null);
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

  Future<void> _crearAveria() async {
    if (!_formKey.currentState!.validate()) {
      return;
    }

    final token = widget.session.token;
    if (token == null || token.isEmpty || _vehiculoId == null) {
      return;
    }

    final latitud = double.tryParse(_latitudCtrl.text);
    final longitud = double.tryParse(_longitudCtrl.text);
    if (latitud == null || longitud == null) {
      setState(() {
        _error = 'Latitud o longitud inválida';
      });
      return;
    }

    setState(() {
      _loading = true;
      _error = null;
    });

    try {
      final averia = await widget.api.createAveria(
        token,
        vehiculoId: _vehiculoId!,
        descripcion: _descripcionCtrl.text,
        latitud: latitud,
        longitud: longitud,
        prioridad: _prioridad,
        direccion: _direccionCtrl.text,
      );

      final erroresAdjuntos = await _subirAdjuntos(token, averia.id);

      _descripcionCtrl.clear();
      _direccionCtrl.clear();
      _fotoPath = null;
      _audioPath = null;
      await _load();
      if (!mounted) {
        return;
      }
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text(
            erroresAdjuntos == 0
                ? 'Avería registrada correctamente'
                : 'Avería registrada, pero $erroresAdjuntos adjunto(s) no se pudieron enviar',
          ),
        ),
      );
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
      setState(() {
        _latitudCtrl.text = position.latitude.toStringAsFixed(6);
        _longitudCtrl.text = position.longitude.toStringAsFixed(6);
      });
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

  Future<void> _tomarFoto() async {
    try {
      final file = await _native.tomarFoto();
      if (file == null || !mounted) {
        return;
      }
      setState(() {
        _fotoPath = file.path;
      });
    } catch (e) {
      if (!mounted) {
        return;
      }
      setState(() {
        _error = '$e';
      });
    }
  }

  Future<void> _elegirFotoGaleria() async {
    try {
      final file = await _native.elegirFotoGaleria();
      if (file == null || !mounted) {
        return;
      }
      setState(() {
        _fotoPath = file.path;
      });
    } catch (e) {
      if (!mounted) {
        return;
      }
      setState(() {
        _error = '$e';
      });
    }
  }

  Future<void> _elegirAudio() async {
    try {
      final path = await _native.elegirAudio();
      if (path == null || !mounted) {
        return;
      }
      setState(() {
        _audioPath = path;
      });
    } catch (e) {
      if (!mounted) {
        return;
      }
      setState(() {
        _error = '$e';
      });
    }
  }

  void _limpiarAdjuntos() {
    setState(() {
      _fotoPath = null;
      _audioPath = null;
    });
  }

  Future<int> _subirAdjuntos(String token, String averiaId) async {
    var errores = 0;
    var orden = 1;

    if (_fotoPath != null && _fotoPath!.isNotEmpty) {
      try {
        await widget.api.agregarMedioAveria(
          token,
          averiaId: averiaId,
          tipo: 'foto',
          url: _fotoPath!,
          ordenVisualizacion: orden,
        );
      } catch (_) {
        errores += 1;
      }
      orden += 1;
    }

    if (_audioPath != null && _audioPath!.isNotEmpty) {
      try {
        await widget.api.agregarMedioAveria(
          token,
          averiaId: averiaId,
          tipo: 'audio',
          url: _audioPath!,
          ordenVisualizacion: orden,
        );
      } catch (_) {
        errores += 1;
      }
    }

    return errores;
  }
}
