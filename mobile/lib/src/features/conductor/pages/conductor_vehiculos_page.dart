import 'package:flutter/material.dart';

import '../../../core/services/api_client.dart';
import '../../../core/services/session_controller.dart';
import '../conductor_api_service.dart';
import '../conductor_models.dart';
import 'conductor_vehiculo_create_page.dart';

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
  List<VehiculoItem> _vehiculos = const [];
  bool _loading = false;
  String? _error;

  @override
  void initState() {
    super.initState();
    _load();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      floatingActionButton: FloatingActionButton(
        onPressed: _abrirCrearVehiculo,
        child: const Icon(Icons.add),
      ),
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
              'Vehículos',
              style: TextStyle(fontSize: 20, fontWeight: FontWeight.w700),
            ),
            const SizedBox(height: 8),
            const Text('Registra y administra tus vehículos.'),
            const SizedBox(height: 8),
            Text(
              'Registrados: ${_vehiculos.length}',
              style: Theme.of(context).textTheme.bodySmall,
            ),
            if (_error != null) ...[
              const SizedBox(height: 12),
              Card(
                color: Theme.of(context).colorScheme.errorContainer,
                child: Padding(
                  padding: const EdgeInsets.all(12),
                  child: Text(
                    _error!,
                    style: TextStyle(
                      color: Theme.of(context).colorScheme.onErrorContainer,
                    ),
                  ),
                ),
              ),
            ],
            const SizedBox(height: 16),
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
                    '${vehiculo.marca} ${vehiculo.modelo} (${vehiculo.anio})',
                  ),
                  subtitle:
                      Text('${vehiculo.placa} · ${vehiculo.tipoCombustible}'),
                  trailing: IconButton(
                    icon: const Icon(Icons.delete_outline),
                    onPressed:
                        _loading ? null : () => _confirmarEliminarVehiculo(vehiculo.id),
                  ),
                ),
              );
            }),
            const SizedBox(height: 72),
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

  Future<void> _abrirCrearVehiculo() async {
    final messenger = ScaffoldMessenger.of(context);
    final mensaje = await Navigator.of(context).push<String?>(
      MaterialPageRoute(
        builder: (_) => ConductorVehiculoCreatePage(
          session: widget.session,
          api: widget.api,
        ),
      ),
    );

    if (!mounted) {
      return;
    }

    if (mensaje != null) {
      await _load();
      messenger.showSnackBar(SnackBar(content: Text(mensaje)));
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
