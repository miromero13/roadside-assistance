import 'package:flutter/material.dart';

import '../../../core/services/api_client.dart';
import '../../../core/services/session_controller.dart';
import '../conductor_api_service.dart';
import '../conductor_models.dart';

class ConductorAveriaDiagnosticoTallerPage extends StatefulWidget {
  const ConductorAveriaDiagnosticoTallerPage({
    super.key,
    required this.session,
    required this.api,
    required this.averia,
  });

  final SessionController session;
  final ConductorApiService api;
  final AveriaItem averia;

  @override
  State<ConductorAveriaDiagnosticoTallerPage> createState() =>
      _ConductorAveriaDiagnosticoTallerPageState();
}

class _ConductorAveriaDiagnosticoTallerPageState
    extends State<ConductorAveriaDiagnosticoTallerPage> {
  List<TallerOpcionItem> _talleres = const [];
  String? _tallerSeleccionado;
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
        title: const Text('Diagnóstico y Talleres'),
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
              'Diagnóstico de IA',
              style: TextStyle(fontSize: 18, fontWeight: FontWeight.w700),
            ),
            const SizedBox(height: 12),
            _buildDiagnostico(),
            const SizedBox(height: 24),
            const Text(
              'Talleres Disponibles',
              style: TextStyle(fontSize: 18, fontWeight: FontWeight.w700),
            ),
            const SizedBox(height: 8),
            Text(
              '${_talleres.length} taller(es) disponible(s) en tu zona',
              style: Theme.of(context).textTheme.bodySmall,
            ),
            const SizedBox(height: 12),
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
            ..._buildTalleres(),
            const SizedBox(height: 24),
          ],
        ),
      ),
    );
  }

  Widget _buildDiagnostico() {
    // Mostrar diagnóstico placeholders - el backend lo enviará
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Icon(Icons.info_outline, color: Theme.of(context).colorScheme.primary),
                const SizedBox(width: 8),
                Expanded(
                  child: Text(
                    'La IA está analizando tu avería...',
                    style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                          fontWeight: FontWeight.w600,
                        ),
                  ),
                ),
              ],
            ),
            const SizedBox(height: 12),
            Text(
              'Descripción: ${widget.averia.descripcion}',
              style: Theme.of(context).textTheme.bodySmall,
            ),
            const SizedBox(height: 8),
            Text(
              'Ubicación: ${widget.averia.direccion ?? "Coordenadas: ${widget.averia.latitud}, ${widget.averia.longitud}"}',
              style: Theme.of(context).textTheme.bodySmall,
            ),
            const SizedBox(height: 8),
            Text(
              'Prioridad: ${widget.averia.prioridad.toUpperCase()}',
              style: Theme.of(context).textTheme.bodySmall,
            ),
          ],
        ),
      ),
    );
  }

  List<Widget> _buildTalleres() {
    if (_talleres.isEmpty) {
      return [
        Card(
          color: Theme.of(context).colorScheme.surfaceContainerHighest,
          child: const Padding(
            padding: EdgeInsets.all(16),
            child: Text('No hay talleres disponibles en tu zona'),
          ),
        ),
      ];
    }

    return [
      ..._talleres.map((taller) {
        final seleccionado = _tallerSeleccionado == taller.tallerId;
        return Card(
          child: InkWell(
            onTap: _creandoOrden ? null : () => _seleccionarTaller(taller.tallerId),
            child: Padding(
              padding: const EdgeInsets.all(12),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    children: [
                      Radio<String>(
                        value: taller.tallerId,
                        groupValue: _tallerSeleccionado,
                        onChanged: _creandoOrden ? null : (value) => _seleccionarTaller(value!),
                      ),
                      Expanded(
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text(
                              taller.nombre,
                              style: const TextStyle(fontWeight: FontWeight.w600),
                            ),
                            const SizedBox(height: 4),
                            Row(
                              children: [
                                Icon(
                                  Icons.star,
                                  size: 16,
                                  color: Colors.amber,
                                ),
                                const SizedBox(width: 4),
                                Text(
                                  '${taller.calificacionPromedio.toStringAsFixed(1)} • ${taller.distanciaKm.toStringAsFixed(1)} km',
                                  style: Theme.of(context).textTheme.bodySmall,
                                ),
                              ],
                            ),
                          ],
                        ),
                      ),
                    ],
                  ),
                  if (seleccionado) ...[
                    const SizedBox(height: 12),
                    SizedBox(
                      width: double.infinity,
                      child: FilledButton(
                        onPressed: _creandoOrden ? null : () => _crearOrden(taller),
                        child: Text(_creandoOrden ? 'Creando orden...' : 'Seleccionar este taller'),
                      ),
                    ),
                  ],
                ],
              ),
            ),
          ),
        );
      }),
    ];
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
      final talleres = await widget.api.getTalleresDisponibles(
        token,
        averiaId: widget.averia.id,
      );

      if (!mounted) {
        return;
      }

      setState(() {
        _talleres = talleres;
        _tallerSeleccionado = talleres.isNotEmpty ? talleres.first.tallerId : null;
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

  void _seleccionarTaller(String tallerId) {
    setState(() {
      _tallerSeleccionado = tallerId;
    });
  }

  Future<void> _crearOrden(TallerOpcionItem taller) async {
    if (_creandoOrden) return;

    final token = widget.session.token;
    if (token == null || token.isEmpty) {
      return;
    }

    setState(() {
      _creandoOrden = true;
      _error = null;
    });

    try {
      final orden = await widget.api.createOrden(
        token,
        averiaId: widget.averia.id,
        tallerId: taller.tallerId,
        categoriaId: '', // La IA ya detectó la categoría, se incluye en backend
        esDomicilio: taller.aceptaDomicilio,
      );

      if (!mounted) {
        return;
      }

      // Navegar a la vista de detalles de la avería
      Navigator.of(context).pushReplacementNamed(
        '/conductor/averia-detalle',
        arguments: widget.averia.id,
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
          _creandoOrden = false;
        });
      }
    }
  }
}
