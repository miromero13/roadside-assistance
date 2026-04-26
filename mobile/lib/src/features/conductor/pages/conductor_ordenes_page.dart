import 'package:flutter/material.dart';

import '../../../core/services/api_client.dart';
import '../../../core/services/session_controller.dart';
import '../conductor_api_service.dart';
import '../conductor_models.dart';
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
  final _formKey = GlobalKey<FormState>();
  final _notasCtrl = TextEditingController();
  final _motivoCancelacionCtrl = TextEditingController();

  List<AveriaItem> _averias = const [];
  List<CategoriaServicioItem> _categorias = const [];
  List<TallerCandidatoItem> _candidatos = const [];
  List<OrdenItem> _ordenes = const [];

  String? _averiaId;
  String? _categoriaId;
  String? _tallerId;
  bool _esDomicilio = false;
  bool _loading = false;
  String? _error;

  @override
  void initState() {
    super.initState();
    _load();
  }

  @override
  void dispose() {
    _notasCtrl.dispose();
    _motivoCancelacionCtrl.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
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
            'Órdenes',
            style: TextStyle(fontSize: 20, fontWeight: FontWeight.w700),
          ),
          const SizedBox(height: 8),
          const Text(
              'Crea una orden seleccionando avería, categoría y taller candidato.'),
          const SizedBox(height: 8),
          Text(
            'Averías: ${_averias.length} · Categorías: ${_categorias.length} · Órdenes: ${_ordenes.length}',
            style: Theme.of(context).textTheme.bodySmall,
          ),
          const SizedBox(height: 16),
          if (_averias.isEmpty)
            Card(
              color: Theme.of(context).colorScheme.surfaceContainerHighest,
              child: const Padding(
                padding: EdgeInsets.all(12),
                child:
                    Text('Necesitas al menos una avería para crear una orden.'),
              ),
            ),
          if (_categorias.isEmpty)
            Card(
              color: Theme.of(context).colorScheme.surfaceContainerHighest,
              child: const Padding(
                padding: EdgeInsets.all(12),
                child: Text('No hay categorías de servicio disponibles.'),
              ),
            ),
          if (_averias.isEmpty || _categorias.isEmpty)
            const SizedBox(height: 12),
          Card(
            child: Padding(
              padding: const EdgeInsets.all(12),
              child: Form(
                key: _formKey,
                child: Column(
                  children: [
                    DropdownButtonFormField<String>(
                      value: _averiaId,
                      decoration: const InputDecoration(labelText: 'Avería'),
                      items: _averias
                          .map(
                            (averia) => DropdownMenuItem<String>(
                              value: averia.id,
                              child: Text(
                                  '${averia.descripcion} (#${averia.id.substring(0, 8)})'),
                            ),
                          )
                          .toList(),
                      validator: (value) {
                        if (value == null || value.isEmpty) {
                          return 'Selecciona una avería';
                        }
                        return null;
                      },
                      onChanged: (value) {
                        setState(() {
                          _averiaId = value;
                          _candidatos = const [];
                          _tallerId = null;
                        });
                      },
                    ),
                    const SizedBox(height: 10),
                    DropdownButtonFormField<String>(
                      value: _categoriaId,
                      decoration: const InputDecoration(
                          labelText: 'Categoría de servicio'),
                      items: _categorias
                          .map(
                            (categoria) => DropdownMenuItem<String>(
                              value: categoria.id,
                              child: Text(categoria.nombre),
                            ),
                          )
                          .toList(),
                      validator: (value) {
                        if (value == null || value.isEmpty) {
                          return 'Selecciona una categoría';
                        }
                        return null;
                      },
                      onChanged: (value) {
                        setState(() {
                          _categoriaId = value;
                          _candidatos = const [];
                          _tallerId = null;
                        });
                      },
                    ),
                    const SizedBox(height: 10),
                    OutlinedButton.icon(
                      onPressed: _loading ? null : _buscarCandidatos,
                      icon: const Icon(Icons.search),
                      label: const Text('Buscar talleres candidatos'),
                    ),
                    if (_candidatos.isNotEmpty) ...[
                      const SizedBox(height: 8),
                      Text(
                        'Se encontraron ${_candidatos.length} talleres candidatos.',
                        style: Theme.of(context).textTheme.bodySmall,
                      ),
                    ],
                    const SizedBox(height: 10),
                    DropdownButtonFormField<String>(
                      value: _tallerId,
                      decoration:
                          const InputDecoration(labelText: 'Taller candidato'),
                      items: _candidatos
                          .map(
                            (candidato) => DropdownMenuItem<String>(
                              value: candidato.tallerId,
                              child: Text(
                                '${candidato.nombre} · ${candidato.distanciaKm.toStringAsFixed(1)} km · ${candidato.calificacionPromedio.toStringAsFixed(1)}',
                              ),
                            ),
                          )
                          .toList(),
                      validator: (value) {
                        if (value == null || value.isEmpty) {
                          return 'Selecciona un taller';
                        }
                        return null;
                      },
                      onChanged: (value) {
                        setState(() {
                          _tallerId = value;
                        });
                      },
                    ),
                    const SizedBox(height: 10),
                    SwitchListTile(
                      value: _esDomicilio,
                      onChanged: _loading
                          ? null
                          : (value) {
                              setState(() {
                                _esDomicilio = value;
                              });
                            },
                      title: const Text('Solicitar servicio a domicilio'),
                      contentPadding: EdgeInsets.zero,
                    ),
                    TextFormField(
                      controller: _notasCtrl,
                      decoration: const InputDecoration(
                          labelText: 'Notas para el taller (opcional)'),
                      maxLines: 2,
                    ),
                    if (_error != null) ...[
                      const SizedBox(height: 10),
                      Text(_error!,
                          style: TextStyle(
                              color: Theme.of(context).colorScheme.error)),
                    ],
                    const SizedBox(height: 12),
                    FilledButton(
                      onPressed:
                          _loading || _averias.isEmpty || _categorias.isEmpty
                              ? null
                              : _crearOrden,
                      child: Text(_loading ? 'Procesando...' : 'Crear orden'),
                    ),
                  ],
                ),
              ),
            ),
          ),
          const SizedBox(height: 16),
          const Text(
            'Mis órdenes',
            style: TextStyle(fontSize: 18, fontWeight: FontWeight.w700),
          ),
          const SizedBox(height: 8),
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
                    Text('Orden #${orden.id.substring(0, 8)}',
                        style: const TextStyle(fontWeight: FontWeight.w700)),
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
      final averias = await widget.api.listAverias(token);
      final categorias = await widget.api.listCategorias(token);
      final ordenes = await widget.api.listOrdenes(token);

      if (!mounted) {
        return;
      }
      setState(() {
        _averias = averias;
        _categorias = categorias;
        _ordenes = ordenes;
        _averiaId = _averiaId ?? (averias.isNotEmpty ? averias.first.id : null);
        _categoriaId = _categoriaId ??
            (categorias.isNotEmpty ? categorias.first.id : null);
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

  Future<void> _buscarCandidatos() async {
    final token = widget.session.token;
    if (token == null ||
        token.isEmpty ||
        _averiaId == null ||
        _categoriaId == null) {
      return;
    }

    setState(() {
      _loading = true;
      _error = null;
      _candidatos = const [];
      _tallerId = null;
    });

    try {
      final candidatos = await widget.api.listTalleresCandidatos(
        token,
        averiaId: _averiaId!,
        categoriaId: _categoriaId!,
      );

      if (!mounted) {
        return;
      }
      setState(() {
        _candidatos = candidatos;
        _tallerId = candidatos.isNotEmpty ? candidatos.first.tallerId : null;
      });
      if (candidatos.isEmpty && mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content:
                Text('No hay talleres candidatos para la selección actual'),
          ),
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
          _loading = false;
        });
      }
    }
  }

  Future<void> _crearOrden() async {
    if (!_formKey.currentState!.validate()) {
      return;
    }

    final token = widget.session.token;
    if (token == null ||
        token.isEmpty ||
        _averiaId == null ||
        _categoriaId == null ||
        _tallerId == null) {
      return;
    }

    setState(() {
      _loading = true;
      _error = null;
    });

    try {
      await widget.api.createOrden(
        token,
        averiaId: _averiaId!,
        tallerId: _tallerId!,
        categoriaId: _categoriaId!,
        esDomicilio: _esDomicilio,
        notasConductor: _notasCtrl.text,
      );
      _notasCtrl.clear();
      await _load();
      if (!mounted) {
        return;
      }
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Orden creada correctamente')),
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
