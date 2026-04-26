import 'package:flutter/material.dart';

import '../../../core/services/api_client.dart';
import '../../../core/services/session_controller.dart';
import '../taller_api_service.dart';
import '../taller_models.dart';
import 'taller_orden_detalle_page.dart';

class TallerOrdenesPage extends StatefulWidget {
  const TallerOrdenesPage({
    super.key,
    required this.session,
    required this.api,
  });

  final SessionController session;
  final TallerApiService api;

  @override
  State<TallerOrdenesPage> createState() => _TallerOrdenesPageState();
}

class _TallerOrdenesPageState extends State<TallerOrdenesPage> {
  final _motivoRechazoCtrl = TextEditingController();
  String? _filtroEstado;
  bool _loading = false;
  String? _error;
  List<TallerOrdenItem> _ordenes = const [];

  @override
  void initState() {
    super.initState();
    _load();
  }

  @override
  void dispose() {
    _motivoRechazoCtrl.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final pendientes =
        _ordenes.where((orden) => orden.pendienteRespuesta).length;

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
            'Órdenes taller',
            style: TextStyle(fontSize: 20, fontWeight: FontWeight.w700),
          ),
          const SizedBox(height: 8),
          Text(
            'Registros: ${_ordenes.length} · Pendientes: $pendientes',
            style: Theme.of(context).textTheme.bodySmall,
          ),
          const SizedBox(height: 12),
          DropdownButtonFormField<String?>(
            value: _filtroEstado,
            decoration: const InputDecoration(labelText: 'Filtrar estado'),
            items: const [
              DropdownMenuItem<String?>(value: null, child: Text('Todos')),
              DropdownMenuItem<String?>(
                  value: 'pendiente_respuesta',
                  child: Text('Pendiente respuesta')),
              DropdownMenuItem<String?>(
                  value: 'aceptada', child: Text('Aceptada')),
              DropdownMenuItem<String?>(
                  value: 'tecnico_asignado', child: Text('Técnico asignado')),
              DropdownMenuItem<String?>(
                  value: 'en_proceso', child: Text('En proceso')),
              DropdownMenuItem<String?>(
                  value: 'completada', child: Text('Completada')),
              DropdownMenuItem<String?>(
                  value: 'cancelada', child: Text('Cancelada')),
            ],
            onChanged: (value) {
              setState(() {
                _filtroEstado = value;
              });
              _load();
            },
          ),
          if (_error != null) ...[
            const SizedBox(height: 10),
            Container(
              padding: const EdgeInsets.all(10),
              decoration: BoxDecoration(
                color: Theme.of(context).colorScheme.errorContainer,
                borderRadius: BorderRadius.circular(10),
              ),
              child: Text(_error!),
            ),
          ],
          const SizedBox(height: 12),
          if (_ordenes.isEmpty)
            const Card(
              child: Padding(
                padding: EdgeInsets.all(16),
                child: Text('No hay órdenes para mostrar con ese filtro.'),
              ),
            ),
          ..._ordenes.map((orden) {
            return Card(
              child: Padding(
                padding: const EdgeInsets.all(12),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text('Orden #${orden.id.substring(0, 8)}',
                        style: const TextStyle(fontWeight: FontWeight.w700)),
                    const SizedBox(height: 4),
                    Text('Estado: ${orden.estado}'),
                    Text('Avería: ${orden.averiaId.substring(0, 8)}'),
                    if ((orden.notasConductor ?? '').isNotEmpty)
                      Text('Notas conductor: ${orden.notasConductor}'),
                    const SizedBox(height: 8),
                    Wrap(
                      spacing: 8,
                      runSpacing: 8,
                      children: [
                        if (orden.pendienteRespuesta) ...[
                          FilledButton.tonal(
                            onPressed:
                                _loading ? null : () => _aceptarOrden(orden.id),
                            child: const Text('Aceptar'),
                          ),
                          FilledButton.tonal(
                            onPressed: _loading
                                ? null
                                : () => _rechazarOrden(orden.id),
                            child: const Text('Rechazar'),
                          ),
                        ],
                        FilledButton(
                          onPressed: () {
                            Navigator.of(context)
                                .push(
                                  MaterialPageRoute<void>(
                                    builder: (_) => TallerOrdenDetallePage(
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
                  ],
                ),
              ),
            );
          }),
        ],
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
      final ordenes =
          await widget.api.listOrdenes(token, estado: _filtroEstado);
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

  Future<void> _aceptarOrden(String ordenId) async {
    final confirmed = await showDialog<bool>(
      context: context,
      builder: (context) {
        return AlertDialog(
          title: const Text('Aceptar orden'),
          content: const Text(
            'Se aceptará con 30 min de respuesta y 60 min de llegada estimada.',
          ),
          actions: [
            TextButton(
              onPressed: () => Navigator.pop(context, false),
              child: const Text('Cancelar'),
            ),
            FilledButton(
              onPressed: () => Navigator.pop(context, true),
              child: const Text('Aceptar'),
            ),
          ],
        );
      },
    );

    if (confirmed != true) {
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
      await widget.api.aceptarOrden(
        token,
        ordenId,
        tiempoRespuesta: 30,
        tiempoLlegada: 60,
        notas: 'Aceptada desde app móvil taller',
      );
      await _load();
      if (!mounted) {
        return;
      }
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Orden aceptada correctamente')),
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

  Future<void> _rechazarOrden(String ordenId) async {
    _motivoRechazoCtrl.clear();
    final confirmed = await showDialog<bool>(
      context: context,
      builder: (context) {
        return AlertDialog(
          title: const Text('Rechazar orden'),
          content: TextField(
            controller: _motivoRechazoCtrl,
            decoration: const InputDecoration(labelText: 'Motivo'),
            maxLines: 2,
          ),
          actions: [
            TextButton(
              onPressed: () => Navigator.pop(context, false),
              child: const Text('Volver'),
            ),
            FilledButton(
              onPressed: () => Navigator.pop(context, true),
              child: const Text('Rechazar'),
            ),
          ],
        );
      },
    );

    if (confirmed != true) {
      return;
    }

    final motivo = _motivoRechazoCtrl.text.trim();
    if (motivo.length < 3) {
      setState(() {
        _error = 'El motivo debe tener al menos 3 caracteres';
      });
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
      await widget.api.rechazarOrden(token, ordenId, motivo);
      await _load();
      if (!mounted) {
        return;
      }
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Orden rechazada correctamente')),
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
