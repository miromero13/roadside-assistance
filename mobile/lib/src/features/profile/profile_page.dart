import 'package:flutter/material.dart';

import '../../core/services/api_client.dart';
import '../../core/services/session_controller.dart';

class ProfilePage extends StatefulWidget {
  const ProfilePage({super.key, required this.session});

  final SessionController session;

  @override
  State<ProfilePage> createState() => _ProfilePageState();
}

class _ProfilePageState extends State<ProfilePage> {
  final _formKey = GlobalKey<FormState>();
  final _nombreCtrl = TextEditingController();
  final _apellidoCtrl = TextEditingController();
  final _telefonoCtrl = TextEditingController();
  final _fotoUrlCtrl = TextEditingController();
  final _passwordActualCtrl = TextEditingController();
  final _passwordNuevaCtrl = TextEditingController();

  bool _saving = false;
  String? _error;
  String? _success;

  @override
  void initState() {
    super.initState();
    _loadFromSession();
    widget.session.addListener(_loadFromSession);
  }

  @override
  void dispose() {
    widget.session.removeListener(_loadFromSession);
    _nombreCtrl.dispose();
    _apellidoCtrl.dispose();
    _telefonoCtrl.dispose();
    _fotoUrlCtrl.dispose();
    _passwordActualCtrl.dispose();
    _passwordNuevaCtrl.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final usuario = widget.session.usuarioActual;

    if (usuario == null) {
      return const Center(child: CircularProgressIndicator());
    }

    return ListView(
      padding: const EdgeInsets.all(16),
      children: [
        Text(
          usuario.nombreCompleto,
          style: const TextStyle(fontSize: 20, fontWeight: FontWeight.w700),
        ),
        const SizedBox(height: 4),
        Text(usuario.email),
        const SizedBox(height: 16),
        Form(
          key: _formKey,
          child: Column(
            children: [
              TextFormField(
                controller: _nombreCtrl,
                decoration: const InputDecoration(labelText: 'Nombre'),
                validator: _required,
              ),
              const SizedBox(height: 12),
              TextFormField(
                controller: _apellidoCtrl,
                decoration: const InputDecoration(labelText: 'Apellido'),
                validator: _required,
              ),
              const SizedBox(height: 12),
              TextFormField(
                controller: _telefonoCtrl,
                decoration: const InputDecoration(labelText: 'Teléfono'),
                validator: _required,
              ),
              const SizedBox(height: 12),
              TextFormField(
                controller: _fotoUrlCtrl,
                decoration:
                    const InputDecoration(labelText: 'Foto URL (opcional)'),
              ),
              const SizedBox(height: 12),
              TextFormField(
                controller: _passwordActualCtrl,
                obscureText: true,
                decoration: const InputDecoration(
                    labelText: 'Contraseña actual (opcional)'),
              ),
              const SizedBox(height: 12),
              TextFormField(
                controller: _passwordNuevaCtrl,
                obscureText: true,
                decoration: const InputDecoration(
                    labelText: 'Nueva contraseña (opcional)'),
              ),
              if (_error != null) ...[
                const SizedBox(height: 12),
                Text(_error!,
                    style:
                        TextStyle(color: Theme.of(context).colorScheme.error)),
              ],
              if (_success != null) ...[
                const SizedBox(height: 12),
                Text(_success!,
                    style: TextStyle(
                        color: Theme.of(context).colorScheme.primary)),
              ],
              const SizedBox(height: 20),
              FilledButton(
                onPressed: _saving ? null : _submit,
                child: Text(_saving ? 'Guardando...' : 'Guardar perfil'),
              ),
            ],
          ),
        ),
      ],
    );
  }

  String? _required(String? value) {
    if (value == null || value.trim().isEmpty) {
      return 'Campo requerido';
    }
    return null;
  }

  void _loadFromSession() {
    final usuario = widget.session.usuarioActual;
    if (!mounted || usuario == null) {
      return;
    }
    _nombreCtrl.text = usuario.nombre;
    _apellidoCtrl.text = usuario.apellido;
    _telefonoCtrl.text = usuario.telefono;
  }

  Future<void> _submit() async {
    if (!_formKey.currentState!.validate()) {
      return;
    }

    setState(() {
      _saving = true;
      _error = null;
      _success = null;
    });

    try {
      await widget.session.actualizarPerfil(
        nombre: _nombreCtrl.text,
        apellido: _apellidoCtrl.text,
        telefono: _telefonoCtrl.text,
        fotoUrl: _fotoUrlCtrl.text,
        passwordActual: _passwordActualCtrl.text,
        passwordNueva: _passwordNuevaCtrl.text,
      );
      _passwordActualCtrl.clear();
      _passwordNuevaCtrl.clear();
      setState(() {
        _success = 'Perfil actualizado correctamente';
      });
    } on ApiException catch (e) {
      setState(() {
        _error = e.message;
      });
    } catch (_) {
      setState(() {
        _error = 'No se pudo actualizar el perfil';
      });
    } finally {
      if (mounted) {
        setState(() {
          _saving = false;
        });
      }
    }
  }
}
