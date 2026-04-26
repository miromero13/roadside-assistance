import 'package:flutter/material.dart';

import 'core/services/session_controller.dart';
import 'features/auth/auth_page.dart';
import 'features/home/home_page.dart';

class AciMobileApp extends StatefulWidget {
  const AciMobileApp({super.key});

  @override
  State<AciMobileApp> createState() => _AciMobileAppState();
}

class _AciMobileAppState extends State<AciMobileApp> {
  final SessionController _session = SessionController();
  late final Future<void> _bootstrapFuture;

  @override
  void initState() {
    super.initState();
    _bootstrapFuture = _session.bootstrap();
  }

  @override
  void dispose() {
    _session.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'ACI Mobile',
      debugShowCheckedModeBanner: false,
      theme: ThemeData(
        colorScheme: ColorScheme.fromSeed(seedColor: const Color(0xFF0D9488)),
        scaffoldBackgroundColor: const Color(0xFFF4F6F9),
        useMaterial3: true,
      ),
      home: FutureBuilder<void>(
        future: _bootstrapFuture,
        builder: (context, snapshot) {
          if (snapshot.connectionState != ConnectionState.done) {
            return const _SplashPage();
          }

          return AnimatedBuilder(
            animation: _session,
            builder: (context, _) {
              if (_session.usuarioActual == null || _session.token == null) {
                return AuthPage(session: _session);
              }
              return HomePage(session: _session);
            },
          );
        },
      ),
    );
  }
}

class _SplashPage extends StatelessWidget {
  const _SplashPage();

  @override
  Widget build(BuildContext context) {
    return const Scaffold(
      body: Center(
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            CircularProgressIndicator(),
            SizedBox(height: 12),
            Text('Inicializando ACI Mobile...'),
          ],
        ),
      ),
    );
  }
}
