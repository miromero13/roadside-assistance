import 'package:flutter/material.dart';

import '../../core/services/api_client.dart';
import '../../core/services/session_controller.dart';
import '../conductor/conductor_api_service.dart';
import '../conductor/pages/conductor_averias_page.dart';
import '../conductor/pages/conductor_ordenes_page.dart';
import '../conductor/pages/conductor_vehiculos_page.dart';
import '../profile/profile_page.dart';
import '../taller/pages/taller_comisiones_page.dart';
import '../taller/pages/taller_notificaciones_page.dart';
import '../taller/pages/taller_ordenes_page.dart';
import '../taller/taller_api_service.dart';

class HomePage extends StatefulWidget {
  const HomePage({super.key, required this.session});

  final SessionController session;

  @override
  State<HomePage> createState() => _HomePageState();
}

class _HomePageState extends State<HomePage> {
  int _index = 0;
  final ConductorApiService _conductorApi = ConductorApiService(ApiClient());
  final TallerApiService _tallerApi = TallerApiService(ApiClient());

  @override
  Widget build(BuildContext context) {
    final usuario = widget.session.usuarioActual;

    if (usuario == null) {
      return const Scaffold(body: Center(child: CircularProgressIndicator()));
    }

    final bool esConductor = usuario.rol == 'conductor';
    final bool esTaller = usuario.rol == 'taller';
    final pages = esConductor
        ? [
            _InicioPanel(usuarioRol: usuario.rol),
            ConductorVehiculosPage(session: widget.session, api: _conductorApi),
            ConductorAveriasPage(session: widget.session, api: _conductorApi),
            ConductorOrdenesPage(session: widget.session, api: _conductorApi),
            ProfilePage(session: widget.session),
          ]
        : esTaller
            ? [
                _InicioPanel(usuarioRol: usuario.rol),
                TallerOrdenesPage(session: widget.session, api: _tallerApi),
                TallerComisionesPage(session: widget.session, api: _tallerApi),
                TallerNotificacionesPage(
                    session: widget.session, api: _tallerApi),
                ProfilePage(session: widget.session),
              ]
            : [
                _InicioPanel(usuarioRol: usuario.rol),
                ProfilePage(session: widget.session),
              ];

    final destinations = esConductor
        ? const [
            NavigationDestination(
              icon: Icon(Icons.home_outlined),
              label: 'Inicio',
            ),
            NavigationDestination(
              icon: Icon(Icons.directions_car_outlined),
              label: 'Vehículos',
            ),
            NavigationDestination(
              icon: Icon(Icons.build_circle_outlined),
              label: 'Averías',
            ),
            NavigationDestination(
              icon: Icon(Icons.list_alt_outlined),
              label: 'Órdenes',
            ),
            NavigationDestination(
              icon: Icon(Icons.person_outline),
              label: 'Perfil',
            ),
          ]
        : esTaller
            ? const [
                NavigationDestination(
                  icon: Icon(Icons.home_outlined),
                  label: 'Inicio',
                ),
                NavigationDestination(
                  icon: Icon(Icons.list_alt_outlined),
                  label: 'Órdenes',
                ),
                NavigationDestination(
                  icon: Icon(Icons.payments_outlined),
                  label: 'Comisiones',
                ),
                NavigationDestination(
                  icon: Icon(Icons.notifications_none),
                  label: 'Notifs',
                ),
                NavigationDestination(
                  icon: Icon(Icons.person_outline),
                  label: 'Perfil',
                ),
              ]
            : const [
                NavigationDestination(
                  icon: Icon(Icons.home_outlined),
                  label: 'Inicio',
                ),
                NavigationDestination(
                  icon: Icon(Icons.person_outline),
                  label: 'Perfil',
                ),
              ];

    if (_index >= pages.length) {
      _index = 0;
    }

    return Scaffold(
      appBar: AppBar(
        title: const Text('ACI Mobile'),
        actions: [
          IconButton(
            onPressed: () => widget.session.logout(),
            icon: const Icon(Icons.logout),
            tooltip: 'Cerrar sesión',
          ),
        ],
      ),
      body: SafeArea(child: pages[_index]),
      bottomNavigationBar: NavigationBar(
        selectedIndex: _index,
        destinations: destinations,
        onDestinationSelected: (value) {
          setState(() {
            _index = value;
          });
        },
      ),
    );
  }
}

class _InicioPanel extends StatelessWidget {
  const _InicioPanel({required this.usuarioRol});

  final String usuarioRol;

  @override
  Widget build(BuildContext context) {
    return ListView(
      padding: const EdgeInsets.all(16),
      children: [
        Card(
          child: Padding(
            padding: const EdgeInsets.all(16),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Text(
                  'Mobile en progreso',
                  style: TextStyle(fontSize: 18, fontWeight: FontWeight.w700),
                ),
                const SizedBox(height: 8),
                Text('Rol actual: $usuarioRol'),
                const SizedBox(height: 8),
                Text(
                  usuarioRol == 'conductor'
                      ? 'Sprint 4: flujo conductor con ubicación y captura de foto para averías.'
                      : usuarioRol == 'taller'
                          ? 'Sprint 3 listo: opera órdenes, comisiones y notificaciones desde mobile.'
                          : 'Este rol tendrá módulos mobile en próximos sprints.',
                ),
              ],
            ),
          ),
        ),
      ],
    );
  }
}
