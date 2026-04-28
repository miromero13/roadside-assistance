import 'package:flutter/material.dart';

import '../../../core/services/api_client.dart';
import '../../../core/services/session_controller.dart';
import '../conductor_api_service.dart';
import '../conductor_models.dart';
import 'conductor_orden_create_page.dart';
import 'conductor_orden_detalle_page.dart';

class ConductorOrdenesPage extends StatefulWidget {
  const ConductorOrdenesPage({
    super.key,
    required this.session,
    required this.api,
  });

  final SessionController session;
  final ConductorApiService api;

  @override
  State<ConductorOrdenesPage> createState() => _ConductorOrdenesPageState();
}

class _ConductorOrdenesPageState extends State<ConductorOrdenesPage> {
  final _motivoCancelacionCtrl = TextEditingController();

  List<OrdenItem> _ordenes = const [];
  bool _loading = false;
  String? _error;

  @override
  void initState() {
    super.initState();
    _load();
  }

  @override
  void dispose() {
    _motivoCancelacionCtrl.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      floatingActionButton: FloatingActionButton(
        onPressed: _abrirCrearOrden,
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
              'Órdenes',
              style: TextStyle(fontSize: 20, fontWeight: FontWeight.w700),
            ),
            const SizedBox(height: 8),
            const Text('Consulta tus órdenes y administra su estado.'),
            const SizedBox(height: 8),
            Text(
              'Órdenes: ${_ordenes.length}',
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
            if (_ordenes.isEmpty)
              const Card(
                child: Padding(
                  padding: EdgeInsets.all(16),
                  child: Text('Aún no tienes órdenes creadas.'),
                ),
              ),
            ..._ordenes.map((orden) {
              final cancelable = orden.estado == 'pendiente_respuesta' ||
                  orden.estado == 'aceptada' ||
                  orden.estado == 'tecnico_asignado';
              return Card(
                child: Padding(
                  padding: const EdgeInsets.all(12),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        'Orden #${orden.id.substring(0, 8)}',
                        style: const TextStyle(fontWeight: FontWeight.w700),
                      ),
                      const SizedBox(height: 4),
                      Text('Estado: ${orden.estado}'),
                      Text('Avería: ${orden.averiaId.substring(0, 8)}'),
                      Text('Taller: ${orden.tallerId.substring(0, 8)}'),
                      if ((orden.notasConductor ?? '').isNotEmpty)
                        Text('Notas: ${orden.notasConductor}'),
                      const SizedBox(height: 8),
                      if (cancelable)
                        FilledButton.tonal(
                          onPressed:
                              _loading ? null : () => _cancelarOrden(orden.id),
                          child: const Text('Cancelar orden'),
                        ),
                      const SizedBox(height: 8),
                      FilledButton(
                        onPressed: () {
                          Navigator.of(context)
                              .push(
                                MaterialPageRoute<void>(
                                  builder: (_) => ConductorOrdenDetallePage(
                                    session: widget.session,
                                    api: widget.api,
                                    ordenId: orden.id,
                                  ),
                                ),
                              )
                              .then((_) => _load());
                        },
                        child: const Text('Ver detalle'),
                      ),
                    ],
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
      final ordenes = await widget.api.listOrdenes(token);

      if (!mounted) {
        return;
      }
      setState(() {
        _ordenes = ordenes;
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

  Future<void> _abrirCrearOrden() async {
    final messenger = ScaffoldMessenger.of(context);
    final mensaje = await Navigator.of(context).push<String?>(
      MaterialPageRoute(
        builder: (_) => ConductorOrdenCreatePage(
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

  Future<void> _cancelarOrden(String ordenId) async {
    final token = widget.session.token;
    if (token == null || token.isEmpty) {
      return;
    }

    _motivoCancelacionCtrl.clear();
    final confirmed = await showDialog<bool>(
      context: context,
      builder: (context) {
        return AlertDialog(
          title: const Text('Cancelar orden'),
          content: TextField(
            controller: _motivoCancelacionCtrl,
            decoration:
                const InputDecoration(labelText: 'Motivo de cancelación'),
          ),
          actions: [
            TextButton(
              onPressed: () => Navigator.pop(context, false),
              child: const Text('Volver'),
            ),
            FilledButton(
              onPressed: () => Navigator.pop(context, true),
              child: const Text('Cancelar orden'),
            ),
          ],
        );
      },
    );

    if (confirmed != true) {
      return;
    }

    final motivo = _motivoCancelacionCtrl.text.trim();
    if (motivo.length < 3) {
      setState(() {
        _error = 'El motivo debe tener al menos 3 caracteres';
      });
      return;
    }

    setState(() {
      _loading = true;
      _error = null;
    });

    try {
      await widget.api.cancelarOrden(token, ordenId: ordenId, motivo: motivo);
      await _load();
      if (!mounted) {
        return;
      }
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Orden cancelada correctamente')),
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
