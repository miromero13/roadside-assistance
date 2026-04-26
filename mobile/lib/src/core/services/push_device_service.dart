import 'dart:math';

import 'package:flutter/foundation.dart';
import 'package:shared_preferences/shared_preferences.dart';

import 'api_client.dart';

class PushDeviceService {
  PushDeviceService(this._api);

  static const _pushDeviceIdKey = 'aci_mobile_push_device_id';
  static const _pushTokenKey = 'aci_mobile_push_token';

  final ApiClient _api;

  Future<void> asegurarRegistroDispositivo(String authToken) async {
    final prefs = await SharedPreferences.getInstance();
    final localToken = await _obtenerOTokenLocal(prefs);
    final response = await _api.get('/push/dispositivos/', token: authToken);
    final data = response['data'];

    String? existenteId;
    if (data is List) {
      for (final item in data.whereType<Map<String, dynamic>>()) {
        final tokenPush = item['token_push'] as String?;
        final activo = item['activo'] as bool? ?? false;
        if (tokenPush == localToken && activo) {
          existenteId = item['id'] as String?;
          break;
        }
      }
    }

    if (existenteId != null && existenteId.isNotEmpty) {
      await prefs.setString(_pushDeviceIdKey, existenteId);
      return;
    }

    final create = await _api.post(
      '/push/dispositivos/',
      token: authToken,
      body: {
        'plataforma': _plataforma,
        'token_push': localToken,
      },
    );

    final created = create['data'];
    if (created is Map<String, dynamic>) {
      final id = created['id'] as String?;
      if (id != null && id.isNotEmpty) {
        await prefs.setString(_pushDeviceIdKey, id);
      }
    }
  }

  Future<void> desactivarDispositivoActual(String authToken) async {
    final prefs = await SharedPreferences.getInstance();
    final deviceId = prefs.getString(_pushDeviceIdKey);
    if (deviceId == null || deviceId.isEmpty) {
      return;
    }

    await _api.delete('/push/dispositivos/$deviceId', token: authToken);
    await prefs.remove(_pushDeviceIdKey);
  }

  Future<String> _obtenerOTokenLocal(SharedPreferences prefs) async {
    final existing = prefs.getString(_pushTokenKey);
    if (existing != null && existing.length >= 10) {
      return existing;
    }

    final seed = DateTime.now().microsecondsSinceEpoch;
    final random = Random().nextInt(999999);
    final generated = 'mobile-$_plataforma-$seed-$random';
    await prefs.setString(_pushTokenKey, generated);
    return generated;
  }

  String get _plataforma {
    switch (defaultTargetPlatform) {
      case TargetPlatform.android:
        return 'android';
      case TargetPlatform.iOS:
        return 'ios';
      default:
        return 'web';
    }
  }
}
