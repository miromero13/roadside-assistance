import 'package:flutter/material.dart';

import '../../../core/config/app_config.dart';
import '../../../core/services/api_client.dart';
import '../../../core/services/session_controller.dart';
import '../conductor_api_service.dart';
import '../conductor_models.dart';

class ConductorAveriaDetallePage extends StatefulWidget {
  const ConductorAveriaDetallePage({
    super.key,
    required this.session,
    required this.api,
    required this.averiaId,
  });

  final SessionController session;
  final ConductorApiService api;
  final String averiaId;

  @override
  State<ConductorAveriaDetallePage> createState() =>
      _ConductorAveriaDetallePageState();
}

class _ConductorAveriaDetallePageState extends State<ConductorAveriaDetallePage> {
  AveriaItem? _averia;
  OrdenItem? _orden;
  bool _loading = false;
  String? _error;
  bool _creandoOrden = false;

  @override
  void initState() {
    super.initState();
    _load();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Detalles de Avería'),
        leading: IconButton(
          icon: const Icon(Icons.arrow_back),
          onPressed: () => Navigator.of(context).pop(),
        ),
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
            if (_error != null) ...[
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
              const SizedBox(height: 12),
            ],
            if (_averia != null) ...[
              _buildAveriaCard(),
              const SizedBox(height: 16),
              _buildDiagnosticoCard(),
              const SizedBox(height: 16),
              _buildTalleresCard(),
              const SizedBox(height: 16),
              if (_orden != null) _buildOrdenCard(),
            ],
          ],
        ),
      ),
    );
  }

  Widget _buildAveriaCard() {
    final averia = _averia!;
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Text(
                  'Avería',
                  style: Theme.of(context).textTheme.titleLarge,
                ),
                _buildEstadoBadge(averia.estado),
              ],
            ),
            const SizedBox(height: 12),
            _buildInfoRow('Descripción:', averia.descripcion),
            const SizedBox(height: 8),
            _buildInfoRow('Ubicación:', averia.direccion ?? 'Lat: ${averia.latitud}, Lng: ${averia.longitud}'),
            const SizedBox(height: 8),
            _buildInfoRow('Prioridad:', averia.prioridad.toUpperCase()),
            const SizedBox(height: 8),
            _buildInfoRow('Medios adjuntos:', '${averia.medios.length} archivos'),
            if (averia.imagenPrincipalUrl != null) ...[
              const SizedBox(height: 12),
              ClipRRect(
                borderRadius: BorderRadius.circular(12),
                child: Image.network(
                  Uri.parse(AppConfig.apiBaseUrl)
                      .replace(path: averia.imagenPrincipalUrl)
                      .toString(),
                  height: 200,
                  width: double.infinity,
                  fit: BoxFit.cover,
                  errorBuilder: (_, __, ___) => const SizedBox.shrink(),
                ),
              ),
            ],
            if (averia.medios.isNotEmpty) ...[
              const SizedBox(height: 12),
              SizedBox(
                height: 80,
                child: ListView.builder(
                  scrollDirection: Axis.horizontal,
                  itemCount: averia.medios.length,
                  itemBuilder: (context, index) {
                    final medio = averia.medios[index];
                    return Padding(
                      padding: const EdgeInsets.only(right: 8),
                      child: Chip(
                        label: Text('${medio.tipo} ${index + 1}'),
                        avatar: Icon(
                          medio.tipo == 'foto'
                              ? Icons.image
                              : medio.tipo == 'audio'
                                  ? Icons.audio_file
                                  : Icons.video_file,
                        ),
                      ),
                    );
                  },
                ),
              ),
            ],
          ],
        ),
      ),
    );
  }

  Widget _buildDiagnosticoCard() {
    final diagnostico = _averia?.diagnostico;

    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              'Diagnóstico IA',
              style: Theme.of(context).textTheme.titleLarge,
            ),
            const SizedBox(height: 12),
            if (diagnostico == null) ...[
              const Text('Aún estamos generando el diagnóstico de esta avería.'),
            ] else ...[
              _buildInfoRow('Categoría:', diagnostico.categoria),
              const SizedBox(height: 8),
              _buildInfoRow('Confianza:', '${(diagnostico.confianza * 100).toStringAsFixed(0)}%'),
              const SizedBox(height: 8),
              _buildInfoRow('Urgencia:', diagnostico.urgencia.toUpperCase()),
              if (diagnostico.resumen != null && diagnostico.resumen!.isNotEmpty) ...[
                const SizedBox(height: 8),
                _buildInfoRow('Resumen:', diagnostico.resumen!),
              ],
              if (diagnostico.diagnostico.isNotEmpty) ...[
                const SizedBox(height: 8),
                _buildInfoRow('Análisis:', diagnostico.diagnostico),
              ],
              if (diagnostico.notasTaller.isNotEmpty) ...[
                const SizedBox(height: 8),
                _buildInfoRow('Notas para taller:', diagnostico.notasTaller),
              ],
            ],
          ],
        ),
      ),
    );
  }

  Widget _buildTalleresCard() {
    final talleres = _averia?.talleresDisponibles ?? const [];
    final diagnostico = _averia?.diagnostico;

    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              'Talleres disponibles',
              style: Theme.of(context).textTheme.titleLarge,
            ),
            const SizedBox(height: 8),
            Text(
              diagnostico?.categoriaId == null
                  ? 'El diagnóstico todavía no asigna una categoría, así que la orden no puede crearse desde aquí.'
                  : '${talleres.length} opción(es) disponibles para crear la orden.',
            ),
            const SizedBox(height: 12),
            if (talleres.isEmpty)
              const Text('No hay talleres disponibles para esta avería.')
            else
              Column(
                children: talleres
                    .map(
                      (taller) => Padding(
                        padding: const EdgeInsets.only(bottom: 12),
                        child: _buildTallerOptionCard(taller),
                      ),
                    )
                    .toList(),
              ),
          ],
        ),
      ),
    );
  }

  Widget _buildTallerOptionCard(TallerOpcionItem taller) {
    final categoriaId = _averia?.diagnostico?.categoriaId;
    final puedeCrearOrden = categoriaId != null && !_creandoOrden;

    return Container(
      decoration: BoxDecoration(
        border: Border.all(color: Theme.of(context).dividerColor),
        borderRadius: BorderRadius.circular(12),
      ),
      padding: const EdgeInsets.all(12),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Expanded(
                child: Text(
                  taller.nombre,
                  style: const TextStyle(fontWeight: FontWeight.w600),
                ),
              ),
              Text('${taller.distanciaKm.toStringAsFixed(1)} km'),
            ],
          ),
          const SizedBox(height: 6),
          Text('Calificación: ${taller.calificacionPromedio.toStringAsFixed(1)}'),
          const SizedBox(height: 4),
          Text('Atiende domicilio: ${taller.aceptaDomicilio ? 'Sí' : 'No'}'),
          const SizedBox(height: 8),
          SizedBox(
            width: double.infinity,
            child: FilledButton(
              onPressed: puedeCrearOrden ? () => _crearOrden(taller) : null,
              child: Text(
                _creandoOrden ? 'Creando orden...' : 'Crear orden aquí',
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildOrdenCard() {
    final orden = _orden!;
    return Card(
      color: Theme.of(context).colorScheme.primaryContainer,
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Text(
                  'Orden de Servicio',
                  style: Theme.of(context).textTheme.titleLarge,
                ),
                _buildEstadoBadge(orden.estado),
              ],
            ),
            const SizedBox(height: 12),
            _buildInfoRow('Orden ID:', orden.id, isCode: true),
            const SizedBox(height: 8),
            _buildInfoRow('Estado:', orden.estado),
            const SizedBox(height: 8),
            _buildInfoRow('Creado:', orden.creadoEn),
            if (orden.notasConductor != null) ...[
              const SizedBox(height: 8),
              _buildInfoRow('Notas:', orden.notasConductor!),
            ],
            const SizedBox(height: 12),
            SizedBox(
              width: double.infinity,
              child: FilledButton(
                onPressed: () {
                  // Navegar a detalles de la orden
                  Navigator.of(context).pushNamed(
                    '/conductor/orden-detalle',
                    arguments: orden.id,
                  );
                },
                child: const Text('Ver detalles de orden'),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildEstadoBadge(String estado) {
    Color color;
    IconData icon;

    switch (estado) {
      case 'registrada':
        color = Colors.grey;
        icon = Icons.pending;
        break;
      case 'analizando':
      case 'pendiente_respuesta':
        color = Colors.orange;
        icon = Icons.pending_actions;
        break;
      case 'clasificada':
      case 'aceptada':
        color = Colors.blue;
        icon = Icons.check_circle;
        break;
      case 'en_proceso':
        color = Colors.purple;
        icon = Icons.construction;
        break;
      case 'completada':
        color = Colors.green;
        icon = Icons.done;
        break;
      case 'cancelada':
        color = Colors.red;
        icon = Icons.cancel;
        break;
      default:
        color = Colors.grey;
        icon = Icons.help;
    }

    return Chip(
      avatar: Icon(icon, color: Colors.white),
      label: Text(estado),
      backgroundColor: color,
      labelStyle: const TextStyle(color: Colors.white),
    );
  }

  Widget _buildInfoRow(String label, String value, {bool isCode = false}) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          label,
          style: Theme.of(context).textTheme.labelMedium,
        ),
        const SizedBox(height: 4),
        Text(
          value,
          style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                fontFamily: isCode ? 'monospace' : null,
              ),
        ),
      ],
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
      final averia = await widget.api.getAveria(token, widget.averiaId);

      if (!mounted) {
        return;
      }

      // Intentar obtener la orden de la avería
      OrdenItem? orden;
      try {
        // Listar órdenes y filtrar por avería
        final ordenes = await widget.api.listOrdenes(token);
        orden = ordenes.firstWhere(
          (o) => o.averiaId == averia.id,
          orElse: () => throw Exception('No encontrada'),
        );
      } catch (_) {
        orden = null;
      }

      setState(() {
        _averia = averia;
        _orden = orden;
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

  Future<void> _crearOrden(TallerOpcionItem taller) async {
    if (_creandoOrden) return;

    final token = widget.session.token;
    final categoriaId = _averia?.diagnostico?.categoriaId;
    if (token == null || token.isEmpty || categoriaId == null || categoriaId.isEmpty) {
      setState(() {
        _error = 'Todavía no hay una categoría de diagnóstico para crear la orden.';
      });
      return;
    }

    setState(() {
      _creandoOrden = true;
      _error = null;
    });

    try {
      await widget.api.createOrden(
        token,
        averiaId: widget.averiaId,
        tallerId: taller.tallerId,
        categoriaId: categoriaId,
        esDomicilio: taller.aceptaDomicilio,
      );

      if (!mounted) {
        return;
      }

      await _load();
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('Orden creada correctamente')),
        );
      }
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
          _creandoOrden = false;
        });
      }
    }
  }
}
