import 'package:flutter/material.dart';

import '../../../core/services/api_client.dart';
import '../../../core/services/session_controller.dart';
import '../conductor_api_service.dart';
import '../conductor_models.dart';

class ConductorVehiculosPage extends StatefulWidget {
  const ConductorVehiculosPage({
    super.key,
    required this.session,
    required this.api,
  });

  final SessionController session;
  final ConductorApiService api;

  @override
  State<ConductorVehiculosPage> createState() => _ConductorVehiculosPageState();
}

class _ConductorVehiculosPageState extends State<ConductorVehiculosPage> {
  final _formKey = GlobalKey<FormState>();
  final _marcaCtrl = TextEditingController();
  final _modeloCtrl = TextEditingController();
  final _anioCtrl = TextEditingController();
  final _placaCtrl = TextEditingController();
  final _colorCtrl = TextEditingController();

  List<VehiculoItem> _vehiculos = const [];
  String _tipoCombustible = 'gasolina';
  bool _loading = false;
  String? _error;

  @override
  void initState() {
    super.initState();
    _anioCtrl.text = '2020';
    _load();
  }

  @override
  void dispose() {
    _marcaCtrl.dispose();
    _modeloCtrl.dispose();
    _anioCtrl.dispose();
    _placaCtrl.dispose();
    _colorCtrl.dispose();
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
            'Vehículos',
            style: TextStyle(fontSize: 20, fontWeight: FontWeight.w700),
          ),
          const SizedBox(height: 8),
          const Text(
              'Registra y administra tus vehículos para solicitar asistencia.'),
          const SizedBox(height: 16),
          Card(
            child: Padding(
              padding: const EdgeInsets.all(12),
              child: Form(
                key: _formKey,
                child: Column(
                  children: [
                    TextFormField(
                      controller: _marcaCtrl,
                      decoration: const InputDecoration(labelText: 'Marca'),
                      validator: _required,
                    ),
                    const SizedBox(height: 10),
                    TextFormField(
                      controller: _modeloCtrl,
                      decoration: const InputDecoration(labelText: 'Modelo'),
                      validator: _required,
                    ),
                    const SizedBox(height: 10),
                    TextFormField(
                      controller: _anioCtrl,
                      keyboardType: TextInputType.number,
                      decoration: const InputDecoration(labelText: 'Año'),
                      validator: (value) {
                        if (value == null || value.trim().isEmpty) {
                          return 'Campo requerido';
                        }
                        if (int.tryParse(value) == null) {
                          return 'Ingresa un año válido';
                        }
                        return null;
                      },
                    ),
                    const SizedBox(height: 10),
                    TextFormField(
                      controller: _placaCtrl,
                      decoration: const InputDecoration(labelText: 'Placa'),
                      validator: _required,
                    ),
                    const SizedBox(height: 10),
                    TextFormField(
                      controller: _colorCtrl,
                      decoration:
                          const InputDecoration(labelText: 'Color (opcional)'),
                    ),
                    const SizedBox(height: 10),
                    DropdownButtonFormField<String>(
                      value: _tipoCombustible,
                      decoration:
                          const InputDecoration(labelText: 'Combustible'),
                      items: const [
                        DropdownMenuItem(
                            value: 'gasolina', child: Text('Gasolina')),
                        DropdownMenuItem(
                            value: 'diesel', child: Text('Diesel')),
                        DropdownMenuItem(
                            value: 'electrico', child: Text('Electrico')),
                        DropdownMenuItem(
                            value: 'hibrido', child: Text('Hibrido')),
                        DropdownMenuItem(value: 'gas', child: Text('Gas')),
                      ],
                      onChanged: (value) {
                        if (value == null) {
                          return;
                        }
                        setState(() {
                          _tipoCombustible = value;
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
                      onPressed: _loading ? null : _crearVehiculo,
                      child:
                          Text(_loading ? 'Guardando...' : 'Agregar vehículo'),
                    ),
                  ],
                ),
              ),
            ),
          ),
          const SizedBox(height: 16),
          Text(
            'Registrados: ${_vehiculos.length}',
            style: Theme.of(context).textTheme.bodySmall,
          ),
          const SizedBox(height: 8),
          if (_vehiculos.isEmpty)
            const Card(
              child: Padding(
                padding: EdgeInsets.all(16),
                child: Text('No tienes vehículos registrados.'),
              ),
            ),
          ..._vehiculos.map((vehiculo) {
            return Card(
              child: ListTile(
                title: Text(
                    '${vehiculo.marca} ${vehiculo.modelo} (${vehiculo.anio})'),
                subtitle:
                    Text('${vehiculo.placa} · ${vehiculo.tipoCombustible}'),
                trailing: IconButton(
                  icon: const Icon(Icons.delete_outline),
                  onPressed: _loading
                      ? null
                      : () => _confirmarEliminarVehiculo(vehiculo.id),
                ),
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
      final data = await widget.api.listVehiculos(token);
      if (!mounted) {
        return;
      }
      setState(() {
        _vehiculos = data;
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

  Future<void> _crearVehiculo() async {
    if (!_formKey.currentState!.validate()) {
      return;
    }

    final token = widget.session.token;
    if (token == null || token.isEmpty) {
      return;
    }

    setState(() {
      _loading = true;
      _error = null;
    });

    try {
      await widget.api.createVehiculo(
        token,
        marca: _marcaCtrl.text,
        modelo: _modeloCtrl.text,
        anio: int.parse(_anioCtrl.text),
        placa: _placaCtrl.text,
        color: _colorCtrl.text,
        tipoCombustible: _tipoCombustible,
      );
      _marcaCtrl.clear();
      _modeloCtrl.clear();
      _anioCtrl.text = '2020';
      _placaCtrl.clear();
      _colorCtrl.clear();
      await _load();
      if (!mounted) {
        return;
      }
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Vehículo agregado correctamente')),
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

  Future<void> _confirmarEliminarVehiculo(String vehiculoId) async {
    final confirmed = await showDialog<bool>(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Eliminar vehículo'),
        content: const Text('Esta acción no se puede deshacer.'),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context, false),
            child: const Text('Cancelar'),
          ),
          FilledButton(
            onPressed: () => Navigator.pop(context, true),
            child: const Text('Eliminar'),
          ),
        ],
      ),
    );

    if (confirmed == true) {
      await _eliminarVehiculo(vehiculoId);
    }
  }

  Future<void> _eliminarVehiculo(String vehiculoId) async {
    final token = widget.session.token;
    if (token == null || token.isEmpty) {
      return;
    }

    setState(() {
      _loading = true;
      _error = null;
    });

    try {
      await widget.api.deleteVehiculo(token, vehiculoId);
      await _load();
      if (!mounted) {
        return;
      }
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Vehículo eliminado')),
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
}
