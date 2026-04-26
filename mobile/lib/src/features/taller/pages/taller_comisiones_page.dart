import 'package:flutter/material.dart';

import '../../../core/services/api_client.dart';
import '../../../core/services/session_controller.dart';
import '../taller_api_service.dart';
import '../taller_models.dart';

class TallerComisionesPage extends StatefulWidget {
  const TallerComisionesPage({
    super.key,
    required this.session,
    required this.api,
  });

  final SessionController session;
  final TallerApiService api;

  @override
  State<TallerComisionesPage> createState() => _TallerComisionesPageState();
}

class _TallerComisionesPageState extends State<TallerComisionesPage> {
  bool _loading = false;
  String? _error;
  List<TallerComisionItem> _comisiones = const [];

  @override
  void initState() {
    super.initState();
    _load();
  }

  @override
  Widget build(BuildContext context) {
    final totalPendiente = _comisiones
        .where((c) => c.pendiente)
        .fold<double>(0, (sum, item) => sum + item.montoComision);
    final pendientesCount = _comisiones.where((c) => c.pendiente).length;

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
            'Comisiones',
            style: TextStyle(fontSize: 20, fontWeight: FontWeight.w700),
          ),
          const SizedBox(height: 8),
          Text(
              'Pendientes: $pendientesCount · Total: Bs ${totalPendiente.toStringAsFixed(2)}'),
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
          if (_comisiones.isEmpty)
            const Card(
              child: Padding(
                padding: EdgeInsets.all(16),
                child: Text('No hay comisiones para mostrar.'),
              ),
            ),
          ..._comisiones.map(
            (comision) => Card(
              child: ListTile(
                title: Text('Comisión #${comision.id.substring(0, 8)}'),
                subtitle: Text(
                    'Estado: ${comision.estado}\nMonto: Bs ${comision.montoComision.toStringAsFixed(2)}'),
                isThreeLine: true,
                trailing: comision.pendiente
                    ? FilledButton.tonal(
                        onPressed:
                            _loading ? null : () => _pagarComision(comision.id),
                        child: const Text('Pagar'),
                      )
                    : const Icon(Icons.check_circle_outline),
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
      final comisiones = await widget.api.listComisionesMias(token);
      if (!mounted) {
        return;
      }
      setState(() {
        _comisiones = comisiones;
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

  Future<void> _pagarComision(String comisionId) async {
    final confirmed = await showDialog<bool>(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Pagar comisión'),
        content: const Text('Se marcará esta comisión como pagada.'),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context, false),
            child: const Text('Cancelar'),
          ),
          FilledButton(
            onPressed: () => Navigator.pop(context, true),
            child: const Text('Pagar'),
          ),
        ],
      ),
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
      await widget.api.pagarComision(token, comisionId);
      await _load();
      if (!mounted) {
        return;
      }
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Comisión pagada correctamente')),
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
