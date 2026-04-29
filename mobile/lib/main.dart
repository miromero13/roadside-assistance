import 'package:flutter/material.dart';
import 'package:flutter/foundation.dart';
import 'package:firebase_core/firebase_core.dart';
import 'package:firebase_messaging/firebase_messaging.dart';
import 'package:permission_handler/permission_handler.dart';

import 'src/app.dart';

Future<void> _solicitarPermisoNotificaciones() async {
  if (kIsWeb) {
    return;
  }

  switch (defaultTargetPlatform) {
    case TargetPlatform.android:
    case TargetPlatform.iOS:
      final status = await Permission.notification.request();
      debugPrint('FCM permiso notificaciones: $status');
      break;
    default:
      break;
  }
}

@pragma('vm:entry-point')
Future<void> _firebaseMessagingBackgroundHandler(RemoteMessage message) async {
  await Firebase.initializeApp();
}

Future<void> main() async {
  WidgetsFlutterBinding.ensureInitialized();
  await _solicitarPermisoNotificaciones();
  await Firebase.initializeApp();
  final token = await FirebaseMessaging.instance.getToken();
  debugPrint('FCM token inicial: $token');
  await FirebaseMessaging.instance.setForegroundNotificationPresentationOptions(
    alert: true,
    badge: true,
    sound: true,
  );
  FirebaseMessaging.onMessage.listen((message) {
    debugPrint(
      'FCM onMessage title=${message.notification?.title} body=${message.notification?.body} data=${message.data}',
    );
  });
  FirebaseMessaging.onMessageOpenedApp.listen((message) {
    debugPrint(
      'FCM onMessageOpenedApp title=${message.notification?.title} body=${message.notification?.body} data=${message.data}',
    );
  });
  FirebaseMessaging.onBackgroundMessage(_firebaseMessagingBackgroundHandler);
  runApp(const AciMobileApp());
}
