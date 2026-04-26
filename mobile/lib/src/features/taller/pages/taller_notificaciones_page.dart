import 'package:flutter/material.dart';

import '../../../core/services/api_client.dart';
import '../../../core/services/session_controller.dart';
import '../taller_api_service.dart';
import '../taller_models.dart';

class TallerNotificacionesPage extends StatefulWidget {
  const TallerNotificacionesPage({
    super.key,
    required this.session,
    required this.api,
  });

  final SessionController session;
  final TallerApiService api;

  @override
  State<TallerNotificacionesPage> createState() =>
      _TallerNotificacionesPageState();
}

class _TallerNotificacionesPageState extends State<TallerNotificacionesPage> {
  bool _loading = false;
  bool _soloNoLeidas = false;
  String? _error;
  List<TallerNotificacionItem> _notificaciones = const [];

  @override
  void initState() {
    super.initState();
    _load();
  }

  @override
  Widget build(BuildContext context) {
    final noLeidas = _notificaciones.where((n) => !n.leida).length;

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
            'Notificaciones',
            style: TextStyle(fontSize: 20, fontWeight: FontWeight.w700),
          ),
          const SizedBox(height: 8),
          Text('No leídas: $noLeidas'),
          const SizedBox(height: 8),
          SwitchListTile(
            value: _soloNoLeidas,
            onChanged: (value) {
              setState(() {
                _soloNoLeidas = value;
              });
              _load();
            },
            title: const Text('Mostrar solo no leídas'),
            contentPadding: EdgeInsets.zero,
          ),
          Align(
            alignment: Alignment.centerLeft,
            child: FilledButton.tonal(
              onPressed: _loading || noLeidas == 0 ? null : _marcarTodasLeidas,
              child: const Text('Marcar todas como leídas'),
            ),
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
          if (_notificaciones.isEmpty)
            const Card(
              child: Padding(
                padding: EdgeInsets.all(16),
                child: Text('No hay notificaciones para mostrar.'),
              ),
            ),
          ..._notificaciones.map(
            (noti) => Card(
              child: ListTile(
                title: Text(noti.titulo),
                subtitle: Text('${noti.mensaje}\n${_shortDate(noti.creadoEn)}'),
                isThreeLine: true,
                trailing: noti.leida
                    ? const Icon(Icons.check_circle_outline)
                    : IconButton(
                        icon: const Icon(Icons.mark_email_read_outlined),
                        onPressed:
                            _loading ? null : () => _marcarLeida(noti.id),
                      ),
              ),
            ),
          ),
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
      final data = await widget.api
          .listNotificaciones(token, soloNoLeidas: _soloNoLeidas);
      if (!mounted) {
        return;
      }
      setState(() {
        _notificaciones = data;
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

  Future<void> _marcarLeida(String notificacionId) async {
    final token = widget.session.token;
    if (token == null || token.isEmpty) {
      return;
    }

    setState(() {
      _loading = true;
      _error = null;
    });

    try {
      await widget.api.marcarNotificacionLeida(token, notificacionId);
      await _load();
      if (!mounted) {
        return;
      }
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Notificación marcada como leída')),
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

  Future<void> _marcarTodasLeidas() async {
    final token = widget.session.token;
    if (token == null || token.isEmpty) {
      return;
    }

    setState(() {
      _loading = true;
      _error = null;
    });

    try {
      await widget.api.marcarTodasNotificacionesLeidas(token);
      await _load();
      if (!mounted) {
        return;
      }
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Notificaciones marcadas como leídas')),
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

  String _shortDate(String value) {
    if (value.length < 16) {
      return value;
    }
    return value.substring(0, 16).replaceAll('T', ' ');
  }
}
