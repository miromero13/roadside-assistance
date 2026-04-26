import 'package:flutter/material.dart';

import '../../../core/services/api_client.dart';
import '../../../core/services/session_controller.dart';
import '../taller_api_service.dart';
import '../taller_models.dart';

class TallerOrdenDetallePage extends StatefulWidget {
  const TallerOrdenDetallePage({
    super.key,
    required this.session,
    required this.api,
    required this.ordenId,
  });

  final SessionController session;
  final TallerApiService api;
  final String ordenId;

  @override
  State<TallerOrdenDetallePage> createState() => _TallerOrdenDetallePageState();
}

class _TallerOrdenDetallePageState extends State<TallerOrdenDetallePage> {
  final _notasAsignacionCtrl = TextEditingController();
  final _descripcionPresupuestoCtrl = TextEditingController();
  final _montoRepuestosCtrl = TextEditingController();
  final _montoManoObraCtrl = TextEditingController();
  final _mensajeCtrl = TextEditingController();

  TallerOrdenItem? _orden;
  List<TallerMecanicoItem> _mecanicos = const [];
  List<TallerAsignacionItem> _asignaciones = const [];
  List<TallerPresupuestoItem> _presupuestos = const [];
  TallerChatItem? _chat;
  List<TallerMensajeItem> _mensajes = const [];
  String? _mecanicoId;
  int _chatNoLeidos = 0;
  bool _loading = false;
  String? _error;
  String? _success;

  @override
  void initState() {
    super.initState();
    _montoRepuestosCtrl.text = '0';
    _montoManoObraCtrl.text = '0';
    _loadAll();
  }

  @override
  void dispose() {
    _notasAsignacionCtrl.dispose();
    _descripcionPresupuestoCtrl.dispose();
    _montoRepuestosCtrl.dispose();
    _montoManoObraCtrl.dispose();
    _mensajeCtrl.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Detalle orden taller')),
      body: RefreshIndicator(
        onRefresh: _loadAll,
        child: ListView(
          padding: const EdgeInsets.all(16),
          children: [
            if (_loading) const LinearProgressIndicator(),
            if (_loading) const SizedBox(height: 12),
            if (_orden == null && !_loading)
              Card(
                child: Padding(
                  padding: const EdgeInsets.all(16),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      const Text('No se pudo cargar la orden.'),
                      const SizedBox(height: 8),
                      FilledButton.tonal(
                        onPressed: _loadAll,
                        child: const Text('Reintentar'),
                      ),
                    ],
                  ),
                ),
              ),
            if (_orden != null) ...[
              _buildResumen(),
              const SizedBox(height: 12),
              _buildAsignacion(),
              const SizedBox(height: 12),
              _buildPresupuestos(),
              const SizedBox(height: 12),
              _buildChat(),
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
      child: ListTile(
        title: Text('Orden #${orden.id.substring(0, 8)}'),
        subtitle: Text(
            'Estado: ${orden.estado}\nAvería: ${orden.averiaId.substring(0, 8)}'),
        isThreeLine: true,
      ),
    );
  }

  Widget _buildAsignacion() {
    return Card(
      child: ExpansionTile(
        title: const Text('Asignación de mecánico'),
        subtitle: Text(
            'Mecánicos: ${_mecanicos.length} · Asignaciones: ${_asignaciones.length}'),
        children: [
          Padding(
            padding: const EdgeInsets.all(12),
            child: Column(
              children: [
                DropdownButtonFormField<String>(
                  value: _mecanicoId,
                  decoration: const InputDecoration(labelText: 'Mecánico'),
                  items: _mecanicos
                      .map(
                        (m) => DropdownMenuItem<String>(
                          value: m.id,
                          child: Text(
                              '${m.id.substring(0, 8)} · ${m.especialidad ?? 'General'}'),
                        ),
                      )
                      .toList(),
                  onChanged: (value) {
                    setState(() {
                      _mecanicoId = value;
                    });
                  },
                ),
                const SizedBox(height: 8),
                TextField(
                  controller: _notasAsignacionCtrl,
                  decoration: const InputDecoration(labelText: 'Notas'),
                ),
                const SizedBox(height: 8),
                FilledButton(
                  onPressed:
                      _loading || _mecanicos.isEmpty ? null : _asignarMecanico,
                  child: const Text('Asignar mecánico'),
                ),
              ],
            ),
          ),
          if (_mecanicos.isEmpty)
            const ListTile(
              title: Text('No hay mecánicos disponibles'),
              subtitle:
                  Text('Activa disponibilidad desde operaciones para asignar.'),
            ),
          if (_asignaciones.isEmpty)
            const ListTile(title: Text('Sin asignaciones registradas')),
          ..._asignaciones.map(
            (a) => ListTile(
              title: Text(
                  'Mecánico ${a.mecanicoId.substring(0, 8)} · ${a.estado}'),
              subtitle: Text(a.notas ?? ''),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildPresupuestos() {
    return Card(
      child: ExpansionTile(
        title: const Text('Presupuestos'),
        subtitle: Text('${_presupuestos.length} versiones'),
        children: [
          Padding(
            padding: const EdgeInsets.all(12),
            child: Column(
              children: [
                TextField(
                  controller: _descripcionPresupuestoCtrl,
                  decoration: const InputDecoration(
                      labelText: 'Descripción de trabajos'),
                  maxLines: 2,
                ),
                const SizedBox(height: 8),
                Row(
                  children: [
                    Expanded(
                      child: TextField(
                        controller: _montoRepuestosCtrl,
                        keyboardType: const TextInputType.numberWithOptions(
                            decimal: true),
                        decoration:
                            const InputDecoration(labelText: 'Repuestos'),
                      ),
                    ),
                    const SizedBox(width: 8),
                    Expanded(
                      child: TextField(
                        controller: _montoManoObraCtrl,
                        keyboardType: const TextInputType.numberWithOptions(
                            decimal: true),
                        decoration:
                            const InputDecoration(labelText: 'Mano de obra'),
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 8),
                FilledButton(
                  onPressed: _loading ? null : _crearPresupuesto,
                  child: const Text('Crear presupuesto'),
                ),
              ],
            ),
          ),
          if (_presupuestos.isEmpty)
            const ListTile(title: Text('Sin presupuestos aún')),
          ..._presupuestos.map(
            (p) => ListTile(
              title: Text('v${p.version} · ${p.estado}'),
              subtitle: Text(
                  '${p.descripcionTrabajos}\nTotal: Bs ${p.montoTotal.toStringAsFixed(2)}'),
              isThreeLine: true,
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
            const ListTile(title: Text('No se pudo inicializar el chat')),
          if (_chat != null) ...[
            Padding(
              padding: const EdgeInsets.all(12),
              child: Column(
                children: [
                  TextField(
                    controller: _mensajeCtrl,
                    decoration: const InputDecoration(labelText: 'Mensaje'),
                  ),
                  const SizedBox(height: 8),
                  Row(
                    children: [
                      FilledButton(
                        onPressed: _loading ? null : _enviarMensaje,
                        child: const Text('Enviar'),
                      ),
                      const SizedBox(width: 8),
                      FilledButton.tonal(
                        onPressed: _loading ? null : _marcarChatLeido,
                        child: const Text('Marcar leído'),
                      ),
                    ],
                  ),
                ],
              ),
            ),
            if (_mensajes.isEmpty)
              const ListTile(title: Text('Sin mensajes aún')),
            ..._mensajes.map(
              (m) => ListTile(
                dense: true,
                title: Text(m.contenido ?? '(sin contenido)'),
                subtitle: Text(
                    '${m.remitenteId.substring(0, 8)} · ${_shortDate(m.enviadoEn)}'),
              ),
            ),
          ],
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
      final mecanicos = await widget.api.listMecanicos(token, disponible: true);
      final asignaciones =
          await widget.api.listAsignaciones(token, widget.ordenId);
      final presupuestos =
          await widget.api.listPresupuestos(token, widget.ordenId);
      final chat = await widget.api.getChatPorOrden(token, widget.ordenId);
      final mensajes = await widget.api.listMensajes(token, chat.id);
      await widget.api.marcarChatLeido(token, chat.id);
      final noLeidos = await widget.api.contarNoLeidosChat(token, chat.id);

      if (!mounted) {
        return;
      }

      setState(() {
        _orden = orden;
        _mecanicos = mecanicos;
        _asignaciones = asignaciones;
        _presupuestos = presupuestos;
        _chat = chat;
        _mensajes = mensajes;
        _chatNoLeidos = noLeidos;
        _mecanicoId =
            _mecanicoId ?? (mecanicos.isNotEmpty ? mecanicos.first.id : null);
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

  Future<void> _asignarMecanico() async {
    final token = widget.session.token;
    final mecanicoId = _mecanicoId;
    if (token == null || token.isEmpty || mecanicoId == null) {
      return;
    }

    setState(() {
      _loading = true;
      _error = null;
      _success = null;
    });

    try {
      await widget.api.asignarMecanico(
        token,
        widget.ordenId,
        mecanicoId: mecanicoId,
        notas: _notasAsignacionCtrl.text,
      );
      _notasAsignacionCtrl.clear();
      await _loadAll();
      if (!mounted) {
        return;
      }
      setState(() {
        _success = 'Mecánico asignado correctamente';
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

  Future<void> _crearPresupuesto() async {
    final token = widget.session.token;
    if (token == null || token.isEmpty) {
      return;
    }

    final descripcion = _descripcionPresupuestoCtrl.text.trim();
    final repuestos = double.tryParse(_montoRepuestosCtrl.text);
    final manoObra = double.tryParse(_montoManoObraCtrl.text);

    if (descripcion.length < 3 ||
        repuestos == null ||
        manoObra == null ||
        repuestos < 0 ||
        manoObra < 0 ||
        (repuestos + manoObra) <= 0) {
      setState(() {
        _error = 'Completa descripción y montos válidos (total mayor a 0)';
      });
      return;
    }

    setState(() {
      _loading = true;
      _error = null;
      _success = null;
    });

    try {
      await widget.api.crearPresupuesto(
        token,
        widget.ordenId,
        descripcion: descripcion,
        montoRepuestos: repuestos,
        montoManoObra: manoObra,
      );
      _descripcionPresupuestoCtrl.clear();
      _montoRepuestosCtrl.text = '0';
      _montoManoObraCtrl.text = '0';
      await _loadAll();
      if (!mounted) {
        return;
      }
      setState(() {
        _success = 'Presupuesto creado correctamente';
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
      _success = null;
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

  Future<void> _marcarChatLeido() async {
    final token = widget.session.token;
    final chat = _chat;
    if (token == null || token.isEmpty || chat == null) {
      return;
    }

    setState(() {
      _loading = true;
      _error = null;
      _success = null;
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
