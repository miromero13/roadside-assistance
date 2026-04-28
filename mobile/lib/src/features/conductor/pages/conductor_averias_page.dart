import 'package:flutter/material.dart';

import '../../../core/services/api_client.dart';
import '../../../core/services/session_controller.dart';
import '../conductor_api_service.dart';
import '../conductor_models.dart';
import 'conductor_averia_create_page.dart';

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
  List<VehiculoItem> _vehiculos = const [];
  List<AveriaItem> _averias = const [];
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
        onPressed: _abrirCrearAveria,
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
              Card(
                color: Theme.of(context).colorScheme.surfaceContainerHighest,
                child: const Padding(
                  padding: EdgeInsets.all(12),
                  child: Text(
                    'Primero registra un vehículo para poder crear averías.',
                  ),
                ),
              ),
            const SizedBox(height: 12),
            if (_averias.isEmpty)
              const Card(
                child: Padding(
                  padding: EdgeInsets.all(16),
                  child: Text('No tienes averías registradas.'),
                ),
              ),
            ..._averias.map(
              (averia) => Card(
                child: ListTile(
                  title: Text(averia.descripcion),
                  subtitle: Text('${averia.estado} · ${averia.prioridad}'),
                  trailing: Text('#${averia.id.substring(0, 8)}'),
                ),
              ),
            ),
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
      final vehiculos = await widget.api.listVehiculos(token);
      final averias = await widget.api.listAverias(token);

      if (!mounted) {
        return;
      }

      setState(() {
        _vehiculos = vehiculos;
        _averias = averias;
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

  Future<void> _abrirCrearAveria() async {
    final messenger = ScaffoldMessenger.of(context);
    final mensaje = await Navigator.of(context).push<String?>(
      MaterialPageRoute(
        builder: (_) => ConductorAveriaCreatePage(
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
}
