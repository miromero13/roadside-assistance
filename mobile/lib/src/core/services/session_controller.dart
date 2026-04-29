import 'dart:async';
import 'dart:convert';

import 'package:flutter/foundation.dart';
import 'package:firebase_messaging/firebase_messaging.dart';
import 'package:shared_preferences/shared_preferences.dart';

import '../models/usuario_auth.dart';
import 'api_client.dart';
import 'push_device_service.dart';

class SessionController extends ChangeNotifier {
  static const _tokenKey = 'aci_mobile_token';
  static const _usuarioKey = 'aci_mobile_usuario';

  final ApiClient _api = ApiClient();
  late final PushDeviceService _push = PushDeviceService(_api);
  StreamSubscription<String>? _pushTokenRefreshSubscription;

  String? _token;
  UsuarioAuth? _usuarioActual;

  String? get token => _token;
  UsuarioAuth? get usuarioActual => _usuarioActual;

  Future<void> bootstrap() async {
    final prefs = await SharedPreferences.getInstance();
    _token = prefs.getString(_tokenKey);

    final usuarioRaw = prefs.getString(_usuarioKey);
    if (usuarioRaw != null && usuarioRaw.isNotEmpty) {
      final decoded = jsonDecode(usuarioRaw);
      if (decoded is Map<String, dynamic>) {
        _usuarioActual = UsuarioAuth.fromJson(decoded);
      }
    }

    if (_token == null || _token!.isEmpty) {
      _clearInMemory();
      return;
    }

    try {
      await cargarPerfil();
    } catch (_) {
      await logout(revocarToken: false);
    }
  }

  Future<void> login({required String email, required String password}) async {
    final response = await _api.post(
      '/auth/login',
      body: {
        'email': email.trim(),
        'password': password,
      },
    );

    final newToken = response['access_token'] as String?;
    final usuarioJson = response['user'];

    if (newToken == null || usuarioJson is! Map<String, dynamic>) {
      throw ApiException('Respuesta inválida del servidor en login');
    }

    _token = newToken;
    _usuarioActual = UsuarioAuth.fromJson(usuarioJson);
    await _persistirSesion();
    await _registrarPushSilencioso();
    _iniciarEscuchaPush();
    notifyListeners();
  }

  Future<void> registerConductor({
    required String nombre,
    required String apellido,
    required String email,
    required String telefono,
    required String password,
  }) async {
    final response = await _api.post(
      '/auth/register',
      body: {
        'nombre': nombre.trim(),
        'apellido': apellido.trim(),
        'email': email.trim(),
        'telefono': telefono.trim(),
        'password': password,
      },
    );

    final newToken = response['access_token'] as String?;
    final usuarioJson = response['user'];

    if (newToken == null || usuarioJson is! Map<String, dynamic>) {
      throw ApiException('Respuesta inválida del servidor en registro');
    }

    _token = newToken;
    _usuarioActual = UsuarioAuth.fromJson(usuarioJson);
    await _persistirSesion();
    await _registrarPushSilencioso();
    _iniciarEscuchaPush();
    notifyListeners();
  }

  Future<void> cargarPerfil() async {
    if (_token == null || _token!.isEmpty) {
      throw ApiException('No hay sesión activa');
    }

    final response = await _api.get('/users/me', token: _token);
    final data = response['data'];
    if (data is! Map<String, dynamic>) {
      throw ApiException('No se pudo cargar el perfil');
    }

    _usuarioActual = UsuarioAuth.fromJson(data);
    await _persistirSesion();
    await _registrarPushSilencioso();
    _iniciarEscuchaPush();
    notifyListeners();
  }

  Future<void> actualizarPerfil({
    required String nombre,
    required String apellido,
    required String telefono,
    String? fotoUrl,
    String? passwordActual,
    String? passwordNueva,
  }) async {
    if (_token == null || _token!.isEmpty) {
      throw ApiException('No hay sesión activa');
    }

    final payload = <String, dynamic>{
      'nombre': nombre.trim(),
      'apellido': apellido.trim(),
      'telefono': telefono.trim(),
      'foto_url': (fotoUrl ?? '').trim(),
    };

    if ((passwordActual ?? '').isNotEmpty || (passwordNueva ?? '').isNotEmpty) {
      payload['password_actual'] = passwordActual ?? '';
      payload['password_nueva'] = passwordNueva ?? '';
    }

    final response = await _api.put('/users/me', body: payload, token: _token);
    final data = response['data'];
    if (data is! Map<String, dynamic>) {
      throw ApiException('No se pudo actualizar el perfil');
    }

    _usuarioActual = UsuarioAuth.fromJson(data);
    await _persistirSesion();
    notifyListeners();
  }

  Future<void> logout({bool revocarToken = true}) async {
    final tokenActual = _token;
    if (tokenActual != null && tokenActual.isNotEmpty) {
      try {
        await _push.desactivarDispositivoActual(tokenActual);
      } catch (_) {
        // ignore
      }
    }

    await _cancelarEscuchaPush();

    if (revocarToken && _token != null && _token!.isNotEmpty) {
      try {
        await _api.post('/auth/logout', body: const {}, token: _token);
      } catch (_) {
        // ignore
      }
    }

    final prefs = await SharedPreferences.getInstance();
    await prefs.remove(_tokenKey);
    await prefs.remove(_usuarioKey);
    _clearInMemory();
    notifyListeners();
  }

  Future<void> _persistirSesion() async {
    final prefs = await SharedPreferences.getInstance();
    if (_token != null && _token!.isNotEmpty) {
      await prefs.setString(_tokenKey, _token!);
    }
    if (_usuarioActual != null) {
      await prefs.setString(_usuarioKey, jsonEncode(_usuarioActual!.toJson()));
    }
  }

  void _clearInMemory() {
    _token = null;
    _usuarioActual = null;
  }

  Future<void> _registrarPushSilencioso() async {
    final tokenActual = _token;
    if (tokenActual == null || tokenActual.isEmpty) {
      return;
    }

    try {
      debugPrint('SessionController: registrando push para usuario=${_usuarioActual?.id}');
      await _push.asegurarRegistroDispositivo(tokenActual);
    } catch (_) {
      debugPrint('SessionController: fallo al registrar push');
    }
  }

  void _iniciarEscuchaPush() {
    final tokenActual = _token;
    if (tokenActual == null || tokenActual.isEmpty) {
      return;
    }

    _pushTokenRefreshSubscription?.cancel();
    _pushTokenRefreshSubscription = FirebaseMessaging.instance.onTokenRefresh.listen((token) async {
      debugPrint('SessionController: token FCM refrescado=${token.substring(0, 12)}');
      if (_token == null || _token != tokenActual) {
        return;
      }

      try {
        await _push.asegurarRegistroDispositivo(tokenActual, tokenPush: token);
      } catch (_) {
        // ignore
      }
    });
  }

  Future<void> _cancelarEscuchaPush() async {
    await _pushTokenRefreshSubscription?.cancel();
    _pushTokenRefreshSubscription = null;
  }

  @override
  void dispose() {
    _pushTokenRefreshSubscription?.cancel();
    super.dispose();
  }
}
