import 'package:flutter/material.dart';

import 'core/services/api_client.dart';
import 'core/services/session_controller.dart';
import 'features/auth/auth_page.dart';
import 'features/conductor/conductor_api_service.dart';
import 'features/conductor/pages/conductor_averia_detalle_page.dart';
import 'features/conductor/pages/conductor_averia_diagnostico_taller_page.dart';
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
      onGenerateRoute: _generateRoute,
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

  Route<dynamic>? _generateRoute(RouteSettings settings) {
    final conductorApi = ConductorApiService(ApiClient());

    switch (settings.name) {
      case '/conductor/averia-detalle':
        final averiaId = settings.arguments as String?;
        if (averiaId == null) return null;
        return MaterialPageRoute(
          builder: (_) => ConductorAveriaDetallePage(
            session: _session,
            api: conductorApi,
            averiaId: averiaId,
          ),
        );

      case '/conductor/averia-diagnostico-taller':
        final averia = settings.arguments as dynamic;
        if (averia == null) return null;
        return MaterialPageRoute(
          builder: (_) => ConductorAveriaDiagnosticoTallerPage(
            session: _session,
            api: conductorApi,
            averia: averia,
          ),
        );
    }
    return null;
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
