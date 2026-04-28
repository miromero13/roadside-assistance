import 'package:flutter/material.dart';

import '../../../core/services/api_client.dart';
import '../../../core/services/session_controller.dart';
import '../conductor_api_service.dart';

class ConductorVehiculoCreatePage extends StatefulWidget {
  const ConductorVehiculoCreatePage({
    super.key,
    required this.session,
    required this.api,
  });

  final SessionController session;
  final ConductorApiService api;

  @override
  State<ConductorVehiculoCreatePage> createState() =>
      _ConductorVehiculoCreatePageState();
}

class _ConductorVehiculoCreatePageState
    extends State<ConductorVehiculoCreatePage> {
  final _formKey = GlobalKey<FormState>();
  final _marcaCtrl = TextEditingController();
  final _modeloCtrl = TextEditingController();
  final _anioCtrl = TextEditingController();
  final _placaCtrl = TextEditingController();
  final _colorCtrl = TextEditingController();

  String _tipoCombustible = 'gasolina';
  bool _loading = false;
  String? _error;

  @override
  void initState() {
    super.initState();
    _anioCtrl.text = '2020';
  }

  @override
  void dispose() {
    _marcaCtrl.dispose();
    _modeloCtrl.dispose();
    _anioCtrl.dispose();
    _placaCtrl.dispose();
    _colorCtrl.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Nuevo vehículo')),
      body: ListView(
        physics: const AlwaysScrollableScrollPhysics(),
        padding: const EdgeInsets.all(16),
        children: [
          if (_loading)
            const Padding(
              padding: EdgeInsets.only(bottom: 12),
              child: LinearProgressIndicator(),
            ),
          const Text(
            'Crear vehículo',
            style: TextStyle(fontSize: 20, fontWeight: FontWeight.w700),
          ),
          const SizedBox(height: 8),
          const Text('Completa los datos para registrar un vehículo.'),
          const SizedBox(height: 16),
          Card(
            child: Padding(
              padding: const EdgeInsets.all(12),
              child: Form(
                key: _formKey,
                child: Column(
                  children: [
                    TextFormField(
                      controller: _marcaCtrl,
                      decoration: const InputDecoration(labelText: 'Marca'),
                      validator: _required,
                    ),
                    const SizedBox(height: 10),
                    TextFormField(
                      controller: _modeloCtrl,
                      decoration: const InputDecoration(labelText: 'Modelo'),
                      validator: _required,
                    ),
                    const SizedBox(height: 10),
                    TextFormField(
                      controller: _anioCtrl,
                      keyboardType: TextInputType.number,
                      decoration: const InputDecoration(labelText: 'Año'),
                      validator: (value) {
                        if (value == null || value.trim().isEmpty) {
                          return 'Campo requerido';
                        }
                        if (int.tryParse(value) == null) {
                          return 'Ingresa un año válido';
                        }
                        return null;
                      },
                    ),
                    const SizedBox(height: 10),
                    TextFormField(
                      controller: _placaCtrl,
                      decoration: const InputDecoration(labelText: 'Placa'),
                      validator: _required,
                    ),
                    const SizedBox(height: 10),
                    TextFormField(
                      controller: _colorCtrl,
                      decoration:
                          const InputDecoration(labelText: 'Color (opcional)'),
                    ),
                    const SizedBox(height: 10),
                    DropdownButtonFormField<String>(
                      initialValue: _tipoCombustible,
                      isExpanded: true,
                      decoration:
                          const InputDecoration(labelText: 'Combustible'),
                      items: const [
                        DropdownMenuItem(
                            value: 'gasolina', child: Text('Gasolina')),
                        DropdownMenuItem(
                            value: 'diesel', child: Text('Diesel')),
                        DropdownMenuItem(
                            value: 'electrico', child: Text('Eléctrico')),
                        DropdownMenuItem(
                            value: 'hibrido', child: Text('Híbrido')),
                        DropdownMenuItem(value: 'gas', child: Text('Gas')),
                      ],
                      onChanged: (value) {
                        if (value == null) {
                          return;
                        }
                        setState(() {
                          _tipoCombustible = value;
                        });
                      },
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
                      onPressed: _loading ? null : _crearVehiculo,
                      child: Text(_loading ? 'Guardando...' : 'Registrar'),
                    ),
                  ],
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }

  String? _required(String? value) {
    if (value == null || value.trim().isEmpty) {
      return 'Campo requerido';
    }
    return null;
  }

  Future<void> _crearVehiculo() async {
    if (!_formKey.currentState!.validate()) {
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
      await widget.api.createVehiculo(
        token,
        marca: _marcaCtrl.text,
        modelo: _modeloCtrl.text,
        anio: int.parse(_anioCtrl.text),
        placa: _placaCtrl.text,
        color: _colorCtrl.text,
        tipoCombustible: _tipoCombustible,
      );

      if (!mounted) {
        return;
      }

      Navigator.of(context).pop('Vehículo agregado correctamente');
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
