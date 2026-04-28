import 'package:flutter/material.dart';

import '../../../core/services/api_client.dart';
import '../../../core/services/session_controller.dart';
import '../conductor_api_service.dart';
import '../conductor_models.dart';

class ConductorOrdenCreatePage extends StatefulWidget {
  const ConductorOrdenCreatePage({
    super.key,
    required this.session,
    required this.api,
  });

  final SessionController session;
  final ConductorApiService api;

  @override
  State<ConductorOrdenCreatePage> createState() =>
      _ConductorOrdenCreatePageState();
}

class _ConductorOrdenCreatePageState extends State<ConductorOrdenCreatePage> {
  final _formKey = GlobalKey<FormState>();
  final _notasCtrl = TextEditingController();

  List<AveriaItem> _averias = const [];
  List<CategoriaServicioItem> _categorias = const [];
  List<TallerCandidatoItem> _candidatos = const [];

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
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final averiaValue = _safeSelection(
      _averiaId,
      _averias.map((averia) => averia.id),
    );
    final categoriaValue = _safeSelection(
      _categoriaId,
      _categorias.map((categoria) => categoria.id),
    );
    final tallerValue = _safeSelection(
      _tallerId,
      _candidatos.map((candidato) => candidato.tallerId),
    );

    return Scaffold(
      appBar: AppBar(title: const Text('Nueva orden')),
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
              'Crear orden',
              style: TextStyle(fontSize: 20, fontWeight: FontWeight.w700),
            ),
            const SizedBox(height: 8),
            const Text('Selecciona avería, categoría y taller candidato.'),
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
            Card(
              child: Padding(
                padding: const EdgeInsets.all(12),
                child: Form(
                  key: _formKey,
                  child: Column(
                    children: [
                      DropdownButtonFormField<String>(
                        initialValue: averiaValue,
                        isExpanded: true,
                        decoration: const InputDecoration(labelText: 'Avería'),
                        items: _averias
                            .map(
                              (averia) => DropdownMenuItem<String>(
                                value: averia.id,
                                child: Text(
                                  '${averia.descripcion} (#${averia.id.substring(0, 8)})',
                                ),
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
                        initialValue: categoriaValue,
                        isExpanded: true,
                        decoration: const InputDecoration(
                          labelText: 'Categoría de servicio',
                        ),
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
                        initialValue: tallerValue,
                        isExpanded: true,
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
                          labelText: 'Notas para el taller (opcional)',
                        ),
                        maxLines: 2,
                      ),
                      if (_error != null) ...[
                        const SizedBox(height: 10),
                        Text(
                          _error!,
                          style: TextStyle(
                            color: Theme.of(context).colorScheme.error,
                          ),
                        ),
                      ],
                      const SizedBox(height: 12),
                      FilledButton(
                        onPressed:
                            _loading || _averias.isEmpty || _categorias.isEmpty
                                ? null
                                : _crearOrden,
                        child: Text(_loading ? 'Procesando...' : 'Registrar'),
                      ),
                    ],
                  ),
                ),
              ),
            ),
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
      final averias = await widget.api.listAverias(token);
      final categorias = await widget.api.listCategorias(token);

      if (!mounted) {
        return;
      }
      final averiaValue = _safeSelection(
        _averiaId,
        averias.map((averia) => averia.id),
      );
      final categoriaValue = _safeSelection(
        _categoriaId,
        categorias.map((categoria) => categoria.id),
      );
      setState(() {
        _averias = averias;
        _categorias = categorias;
        _averiaId = averiaValue ?? (averias.isNotEmpty ? averias.first.id : null);
        _categoriaId =
            categoriaValue ?? (categorias.isNotEmpty ? categorias.first.id : null);
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
            content: Text('No hay talleres candidatos para la selección actual'),
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

      if (!mounted) {
        return;
      }

      Navigator.of(context).pop('Orden creada correctamente');
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

  String? _safeSelection(String? value, Iterable<String> options) {
    if (value == null || value.isEmpty) {
      return null;
    }
    return options.contains(value) ? value : null;
  }
}
