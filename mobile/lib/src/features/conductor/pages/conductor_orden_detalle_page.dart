import 'package:flutter/material.dart';

import '../../../core/services/api_client.dart';
import '../../../core/services/session_controller.dart';
import '../conductor_api_service.dart';
import '../conductor_models.dart';

class ConductorOrdenDetallePage extends StatefulWidget {
  const ConductorOrdenDetallePage({
    super.key,
    required this.session,
    required this.api,
    required this.ordenId,
  });

  final SessionController session;
  final ConductorApiService api;
  final String ordenId;

  @override
  State<ConductorOrdenDetallePage> createState() =>
      _ConductorOrdenDetallePageState();
}

class _ConductorOrdenDetallePageState extends State<ConductorOrdenDetallePage> {
  final _motivoRechazoCtrl = TextEditingController();
  final _comentarioCalificacionCtrl = TextEditingController();
  final _mensajeCtrl = TextEditingController();

  OrdenItem? _orden;
  List<HistorialEstadoOrdenItem> _historial = const [];
  List<AsignacionOrdenItem> _asignaciones = const [];
  List<PresupuestoItem> _presupuestos = const [];
  List<CalificacionItem> _calificaciones = const [];
  List<MensajeItem> _mensajes = const [];
  FacturaItem? _factura;
  ChatItem? _chat;
  int _chatNoLeidos = 0;
  int _puntuacion = 5;
  bool _loading = false;
  String? _error;
  String? _success;

  @override
  void initState() {
    super.initState();
    _loadAll();
  }

  @override
  void dispose() {
    _motivoRechazoCtrl.dispose();
    _comentarioCalificacionCtrl.dispose();
    _mensajeCtrl.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Detalle de orden')),
      body: RefreshIndicator(
        onRefresh: _loadAll,
        child: ListView(
          padding: const EdgeInsets.all(16),
          children: [
            if (_loading) const LinearProgressIndicator(),
            if (_loading) const SizedBox(height: 12),
            if (_orden == null && _loading)
              const Center(child: CircularProgressIndicator())
            else if (_orden == null)
              Card(
                child: Padding(
                  padding: const EdgeInsets.all(16),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      const Text('No se pudo cargar el detalle de la orden.'),
                      const SizedBox(height: 8),
                      FilledButton.tonal(
                        onPressed: _loading ? null : _loadAll,
                        child: const Text('Reintentar'),
                      ),
                    ],
                  ),
                ),
              )
            else if (_orden != null) ...[
              _buildResumen(),
              const SizedBox(height: 12),
              _buildPresupuestos(),
              const SizedBox(height: 12),
              _buildPagoFactura(),
              const SizedBox(height: 12),
              _buildCalificacion(),
              const SizedBox(height: 12),
              _buildChat(),
              const SizedBox(height: 12),
              _buildHistorial(),
              const SizedBox(height: 12),
              _buildAsignaciones(),
            ],
            if (_error != null) ...[
              const SizedBox(height: 12),
              Container(
                padding: const EdgeInsets.all(10),
                decoration: BoxDecoration(
                  color: Theme.of(context).colorScheme.errorContainer,
                  borderRadius: BorderRadius.circular(10),
                ),
                child: Text(_error!),
              ),
            ],
            if (_success != null) ...[
              const SizedBox(height: 12),
              Container(
                padding: const EdgeInsets.all(10),
                decoration: BoxDecoration(
                  color: Theme.of(context).colorScheme.primaryContainer,
                  borderRadius: BorderRadius.circular(10),
                ),
                child: Text(_success!),
              ),
            ],
          ],
        ),
      ),
    );
  }

  Widget _buildResumen() {
    final orden = _orden!;
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(12),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text('Orden #${orden.id.substring(0, 8)}',
                style: const TextStyle(fontWeight: FontWeight.w700)),
            const SizedBox(height: 6),
            Text('Estado: ${orden.estado}'),
            Text('Taller: ${orden.tallerId.substring(0, 8)}'),
            Text('Avería: ${orden.averiaId.substring(0, 8)}'),
            if ((orden.notasConductor ?? '').isNotEmpty)
              Text('Notas: ${orden.notasConductor}'),
            if ((orden.motivoCancelacion ?? '').isNotEmpty)
              Text('Motivo cancelación: ${orden.motivoCancelacion}'),
          ],
        ),
      ),
    );
  }

  Widget _buildPresupuestos() {
    return Card(
      child: ExpansionTile(
        initiallyExpanded: true,
        title: const Text('Presupuestos'),
        subtitle: Text('${_presupuestos.length} registros'),
        children: [
          if (_presupuestos.isEmpty)
            const ListTile(title: Text('No hay presupuestos aún')),
          ..._presupuestos.map((presupuesto) {
            return ListTile(
              title: Text('v${presupuesto.version} · ${presupuesto.estado}'),
              subtitle: Text(
                '${presupuesto.descripcionTrabajos}\nTotal: Bs ${presupuesto.montoTotal.toStringAsFixed(2)}',
              ),
              isThreeLine: true,
              trailing: presupuesto.aprobable
                  ? PopupMenuButton<String>(
                      onSelected: (value) {
                        if (value == 'aprobar') {
                          _aprobarPresupuesto(presupuesto.id);
                        } else {
                          _rechazarPresupuesto(presupuesto.id);
                        }
                      },
                      itemBuilder: (_) => const [
                        PopupMenuItem(value: 'aprobar', child: Text('Aprobar')),
                        PopupMenuItem(
                            value: 'rechazar', child: Text('Rechazar')),
                      ],
                    )
                  : null,
            );
          }),
        ],
      ),
    );
  }

  Widget _buildPagoFactura() {
    final aprobado =
        _presupuestos.where((p) => p.estado == 'aprobado').toList();

    return Card(
      child: ExpansionTile(
        title: const Text('Pago y factura'),
        children: [
          if (aprobado.isEmpty)
            const ListTile(
                title: Text('No hay presupuesto aprobado para pagar')),
          ...aprobado.map(
            (presupuesto) => ListTile(
              title: Text('Presupuesto v${presupuesto.version} aprobado'),
              subtitle: Text(
                  'Total a pagar: Bs ${presupuesto.montoTotal.toStringAsFixed(2)}'),
              trailing: PopupMenuButton<String>(
                onSelected: (metodo) => _crearPago(presupuesto, metodo),
                itemBuilder: (_) => const [
                  PopupMenuItem(
                      value: 'efectivo', child: Text('Pagar en efectivo')),
                  PopupMenuItem(
                      value: 'tarjeta', child: Text('Pagar con tarjeta')),
                  PopupMenuItem(value: 'qr', child: Text('Pagar con QR')),
                ],
              ),
            ),
          ),
          const Divider(height: 1),
          ListTile(
            title: const Text('Factura'),
            subtitle: Text(
              _factura == null
                  ? 'Aún no se encontró factura para esta orden'
                  : 'Nro: ${_factura!.numeroFactura}\nTotal: Bs ${_factura!.total.toStringAsFixed(2)}',
            ),
            isThreeLine: _factura != null,
            trailing: IconButton(
              icon: const Icon(Icons.refresh),
              onPressed: _loading ? null : _cargarFactura,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildCalificacion() {
    return Card(
      child: ExpansionTile(
        title: const Text('Calificación'),
        subtitle: Text(
            _calificaciones.isEmpty ? 'Sin calificación' : 'Ya calificada'),
        children: [
          if (_calificaciones.isNotEmpty)
            ..._calificaciones.map(
              (c) => ListTile(
                title: Text('Puntuación: ${c.puntuacion}/5'),
                subtitle: Text(c.comentario ?? ''),
              ),
            ),
          if (_calificaciones.isEmpty)
            Padding(
              padding: const EdgeInsets.all(12),
              child: Column(
                children: [
                  DropdownButtonFormField<int>(
                    value: _puntuacion,
                    decoration: const InputDecoration(labelText: 'Puntuación'),
                    items: const [
                      DropdownMenuItem(value: 1, child: Text('1')),
                      DropdownMenuItem(value: 2, child: Text('2')),
                      DropdownMenuItem(value: 3, child: Text('3')),
                      DropdownMenuItem(value: 4, child: Text('4')),
                      DropdownMenuItem(value: 5, child: Text('5')),
                    ],
                    onChanged: (value) {
                      if (value == null) {
                        return;
                      }
                      setState(() {
                        _puntuacion = value;
                      });
                    },
                  ),
                  const SizedBox(height: 10),
                  TextField(
                    controller: _comentarioCalificacionCtrl,
                    decoration: const InputDecoration(labelText: 'Comentario'),
                    maxLines: 2,
                  ),
                  const SizedBox(height: 10),
                  FilledButton(
                    onPressed: _loading ? null : _crearCalificacion,
                    child: const Text('Enviar calificación'),
                  ),
                ],
              ),
            ),
        ],
      ),
    );
  }

  Widget _buildChat() {
    return Card(
      child: ExpansionTile(
        title: const Text('Chat'),
        subtitle:
            Text(_chat == null ? 'No disponible' : 'No leídos: $_chatNoLeidos'),
        children: [
          if (_chat == null)
            const ListTile(
                title: Text('No se pudo abrir chat para esta orden')),
          if (_chat != null) ...[
            ListTile(
              title: const Text('Acciones'),
              subtitle: Row(
                children: [
                  FilledButton.tonal(
                    onPressed: _loading ? null : _marcarChatLeido,
                    child: const Text('Marcar leído'),
                  ),
                ],
              ),
            ),
            Padding(
              padding: const EdgeInsets.symmetric(horizontal: 12),
              child: TextField(
                controller: _mensajeCtrl,
                decoration: const InputDecoration(labelText: 'Mensaje'),
              ),
            ),
            const SizedBox(height: 8),
            Padding(
              padding: const EdgeInsets.only(left: 12, right: 12, bottom: 12),
              child: Row(
                children: [
                  FilledButton(
                    onPressed: _loading ? null : _enviarMensaje,
                    child: const Text('Enviar'),
                  ),
                ],
              ),
            ),
            ..._mensajes.map(
              (m) => ListTile(
                dense: true,
                title: Text(m.contenido ?? '(sin contenido)'),
                subtitle: Text(
                    '${m.remitenteId.substring(0, 8)} · ${_shortDate(m.enviadoEn)}'),
                trailing: !m.leido
                    ? IconButton(
                        icon: const Icon(Icons.done_all, size: 18),
                        onPressed:
                            _loading ? null : () => _marcarMensajeLeido(m.id),
                      )
                    : const Icon(Icons.check, size: 16),
              ),
            ),
            if (_mensajes.isEmpty)
              const ListTile(
                title: Text('Sin mensajes todavía'),
                subtitle: Text('Envía un mensaje para iniciar el chat.'),
              ),
          ],
        ],
      ),
    );
  }

  Widget _buildHistorial() {
    return Card(
      child: ExpansionTile(
        title: const Text('Historial de estados'),
        subtitle: Text('${_historial.length} eventos'),
        children: [
          if (_historial.isEmpty) const ListTile(title: Text('Sin historial')),
          ..._historial.map(
            (h) => ListTile(
              title: Text('${h.estadoAnterior ?? '-'} -> ${h.estadoNuevo}'),
              subtitle:
                  Text('${h.observacion ?? ''}\n${_shortDate(h.creadoEn)}'),
              isThreeLine: true,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildAsignaciones() {
    return Card(
      child: ExpansionTile(
        title: const Text('Asignaciones de mecánico'),
        subtitle: Text('${_asignaciones.length} registros'),
        children: [
          if (_asignaciones.isEmpty)
            const ListTile(title: Text('Aún no hay asignaciones')),
          ..._asignaciones.map(
            (a) => ListTile(
              title: Text(
                  'Mecánico ${a.mecanicoId.substring(0, 8)} · ${a.estado}'),
              subtitle: Text('${a.notas ?? ''}\n${_shortDate(a.asignadoEn)}'),
              isThreeLine: true,
            ),
          ),
        ],
      ),
    );
  }

  Future<void> _loadAll() async {
    final token = widget.session.token;
    if (token == null || token.isEmpty) {
      return;
    }

    setState(() {
      _loading = true;
      _error = null;
      _success = null;
    });

    try {
      final orden = await widget.api.getOrden(token, widget.ordenId);
      final historial =
          await widget.api.getHistorialOrden(token, widget.ordenId);
      final asignaciones =
          await widget.api.getAsignacionesOrden(token, widget.ordenId);
      final presupuestos =
          await widget.api.getPresupuestosOrden(token, widget.ordenId);
      final calificaciones =
          await widget.api.listCalificaciones(token, widget.ordenId);
      final chat = await widget.api.getChatPorOrden(token, widget.ordenId);
      final mensajes = await widget.api.listMensajes(token, chat.id);
      await widget.api.marcarChatLeido(token, chat.id);
      final noLeidos = await widget.api.contarNoLeidosChat(token, chat.id);
      final factura =
          await widget.api.getFacturaPorOrden(token, widget.ordenId);

      if (!mounted) {
        return;
      }

      setState(() {
        _orden = orden;
        _historial = historial;
        _asignaciones = asignaciones;
        _presupuestos = presupuestos;
        _calificaciones = calificaciones;
        _chat = chat;
        _mensajes = mensajes;
        _chatNoLeidos = noLeidos;
        _factura = factura;
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

  Future<void> _aprobarPresupuesto(String presupuestoId) async {
    final token = widget.session.token;
    if (token == null || token.isEmpty) {
      return;
    }

    setState(() {
      _loading = true;
      _error = null;
      _success = null;
    });

    try {
      await widget.api.aprobarPresupuesto(token, presupuestoId);
      await _loadAll();
      if (!mounted) {
        return;
      }
      setState(() {
        _success = 'Presupuesto aprobado';
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

  Future<void> _rechazarPresupuesto(String presupuestoId) async {
    _motivoRechazoCtrl.clear();
    final confirmed = await showDialog<bool>(
      context: context,
      builder: (context) {
        return AlertDialog(
          title: const Text('Rechazar presupuesto'),
          content: TextField(
            controller: _motivoRechazoCtrl,
            decoration: const InputDecoration(labelText: 'Motivo'),
            maxLines: 2,
          ),
          actions: [
            TextButton(
              onPressed: () => Navigator.pop(context, false),
              child: const Text('Cancelar'),
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
      _success = null;
    });

    try {
      await widget.api.rechazarPresupuesto(token, presupuestoId, motivo);
      await _loadAll();
      if (!mounted) {
        return;
      }
      setState(() {
        _success = 'Presupuesto rechazado';
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

  Future<void> _crearPago(PresupuestoItem presupuesto, String metodo) async {
    final token = widget.session.token;
    final orden = _orden;
    if (token == null || token.isEmpty || orden == null) {
      return;
    }

    setState(() {
      _loading = true;
      _error = null;
      _success = null;
    });

    try {
      final pago = await widget.api.crearPago(
        token,
        ordenId: orden.id,
        presupuestoId: presupuesto.id,
        metodo: metodo,
        monto: presupuesto.montoTotal,
      );
      try {
        _factura = await widget.api.generarFacturaPorPago(token, pago.id);
      } on ApiException {
        // no-op
      }
      await _loadAll();
      if (!mounted) {
        return;
      }
      setState(() {
        _success = 'Pago creado (${pago.estado}).';
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

  Future<void> _cargarFactura() async {
    final token = widget.session.token;
    if (token == null || token.isEmpty) {
      return;
    }

    setState(() {
      _loading = true;
      _error = null;
      _success = null;
    });

    try {
      final factura =
          await widget.api.getFacturaPorOrden(token, widget.ordenId);
      if (!mounted) {
        return;
      }
      setState(() {
        _factura = factura;
      });
    } finally {
      if (mounted) {
        setState(() {
          _loading = false;
        });
      }
    }
  }

  Future<void> _crearCalificacion() async {
    final token = widget.session.token;
    if (token == null || token.isEmpty) {
      return;
    }

    setState(() {
      _loading = true;
      _error = null;
      _success = null;
    });

    try {
      await widget.api.crearCalificacion(
        token,
        ordenId: widget.ordenId,
        puntuacion: _puntuacion,
        comentario: _comentarioCalificacionCtrl.text,
      );
      _comentarioCalificacionCtrl.clear();
      await _loadAll();
      if (!mounted) {
        return;
      }
      setState(() {
        _success = 'Calificación enviada';
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

  Future<void> _enviarMensaje() async {
    final token = widget.session.token;
    final chat = _chat;
    if (token == null || token.isEmpty || chat == null) {
      return;
    }

    final contenido = _mensajeCtrl.text.trim();
    if (contenido.isEmpty) {
      return;
    }

    setState(() {
      _loading = true;
      _error = null;
    });

    try {
      await widget.api.enviarMensaje(token, chat.id, contenido);
      _mensajeCtrl.clear();
      final mensajes = await widget.api.listMensajes(token, chat.id);
      final noLeidos = await widget.api.contarNoLeidosChat(token, chat.id);
      if (!mounted) {
        return;
      }
      setState(() {
        _mensajes = mensajes;
        _chatNoLeidos = noLeidos;
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

  Future<void> _marcarMensajeLeido(String mensajeId) async {
    final token = widget.session.token;
    final chat = _chat;
    if (token == null || token.isEmpty || chat == null) {
      return;
    }

    setState(() {
      _loading = true;
      _error = null;
    });

    try {
      await widget.api.marcarMensajeLeido(token, chat.id, mensajeId);
      final mensajes = await widget.api.listMensajes(token, chat.id);
      final noLeidos = await widget.api.contarNoLeidosChat(token, chat.id);
      if (!mounted) {
        return;
      }
      setState(() {
        _mensajes = mensajes;
        _chatNoLeidos = noLeidos;
      });
    } finally {
      if (mounted) {
        setState(() {
          _loading = false;
        });
      }
    }
  }

  Future<void> _marcarChatLeido() async {
    final token = widget.session.token;
    final chat = _chat;
    if (token == null || token.isEmpty || chat == null) {
      return;
    }

    setState(() {
      _loading = true;
      _error = null;
    });

    try {
      await widget.api.marcarChatLeido(token, chat.id);
      final mensajes = await widget.api.listMensajes(token, chat.id);
      final noLeidos = await widget.api.contarNoLeidosChat(token, chat.id);
      if (!mounted) {
        return;
      }
      setState(() {
        _mensajes = mensajes;
        _chatNoLeidos = noLeidos;
      });
    } finally {
      if (mounted) {
        setState(() {
          _loading = false;
        });
      }
    }
  }

  String _shortDate(String value) {
    if (value.length < 16) {
      return value;
    }
    return value.substring(0, 16).replaceAll('T', ' ');
  }
}
