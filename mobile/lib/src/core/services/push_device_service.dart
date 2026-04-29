import 'package:flutter/foundation.dart';
import 'package:firebase_messaging/firebase_messaging.dart';
import 'package:shared_preferences/shared_preferences.dart';

import 'api_client.dart';

class PushDeviceService {
  PushDeviceService(this._api);

  static const _pushDeviceIdKey = 'aci_mobile_push_device_id';
  static const _pushTokenKey = 'aci_mobile_push_token';

  final ApiClient _api;

  Future<void> asegurarRegistroDispositivo(String authToken, {String? tokenPush}) async {
    final prefs = await SharedPreferences.getInstance();
    final localToken = tokenPush ?? await _obtenerTokenFirebase();
    if (localToken == null || localToken.isEmpty) {
      debugPrint('PushDeviceService: no hay token FCM para registrar');
      return;
    }

    debugPrint('PushDeviceService: asegurando registro con token=${localToken.substring(0, 12)}');

    final storedToken = prefs.getString(_pushTokenKey);
    final deviceId = prefs.getString(_pushDeviceIdKey);
    if (storedToken != null && storedToken != localToken && deviceId != null && deviceId.isNotEmpty) {
      try {
        debugPrint('PushDeviceService: borrando dispositivo previo id=$deviceId');
        await _api.delete('/push/dispositivos/$deviceId', token: authToken);
      } catch (_) {
        // ignore
      }
      await prefs.remove(_pushDeviceIdKey);
    }

    final response = await _api.get('/push/dispositivos/', token: authToken);
    final data = response['data'];
    debugPrint('PushDeviceService: dispositivos remotos obtenidos');

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
      debugPrint('PushDeviceService: dispositivo ya existía id=$existenteId');
      await prefs.setString(_pushDeviceIdKey, existenteId);
      await prefs.setString(_pushTokenKey, localToken);
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
        debugPrint('PushDeviceService: dispositivo creado id=$id');
        await prefs.setString(_pushDeviceIdKey, id);
        await prefs.setString(_pushTokenKey, localToken);
      }
    }
  }

  Future<void> desactivarDispositivoActual(String authToken) async {
    final prefs = await SharedPreferences.getInstance();
    final deviceId = prefs.getString(_pushDeviceIdKey);
    if (deviceId == null || deviceId.isEmpty) {
      debugPrint('PushDeviceService: no hay dispositivo para desactivar');
      return;
    }

    debugPrint('PushDeviceService: desactivando dispositivo id=$deviceId');
    await _api.delete('/push/dispositivos/$deviceId', token: authToken);
    await prefs.remove(_pushDeviceIdKey);
    await prefs.remove(_pushTokenKey);
  }

  Future<String?> _obtenerTokenFirebase() async {
    await FirebaseMessaging.instance.requestPermission(
      alert: true,
      badge: true,
      sound: true,
      provisional: false,
    );

    final token = await FirebaseMessaging.instance.getToken();
    debugPrint('PushDeviceService: token FCM obtenido=${token?.substring(0, 12)}');
    return token;
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
