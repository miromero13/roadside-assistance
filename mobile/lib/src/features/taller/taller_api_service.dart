import '../../core/services/api_client.dart';
import 'taller_models.dart';

class TallerApiService {
  TallerApiService(this._api);

  final ApiClient _api;

  List<Map<String, dynamic>> _asList(dynamic value) {
    if (value is! List) {
      return const [];
    }
    return value.whereType<Map<String, dynamic>>().toList();
  }

  Future<List<TallerOrdenItem>> listOrdenes(String token,
      {String? estado}) async {
    final query = estado == null ? '' : '?estado=$estado';
    final response = await _api.get('/ordenes/$query', token: token);
    return _asList(response['data']).map(TallerOrdenItem.fromJson).toList();
  }

  Future<TallerOrdenItem> getOrden(String token, String ordenId) async {
    final response = await _api.get('/ordenes/$ordenId', token: token);
    final data = response['data'];
    if (data is! Map<String, dynamic>) {
      throw ApiException('No se pudo cargar la orden');
    }
    return TallerOrdenItem.fromJson(data);
  }

  Future<void> aceptarOrden(
    String token,
    String ordenId, {
    required int tiempoRespuesta,
    int? tiempoLlegada,
    String? notas,
  }) async {
    await _api.put(
      '/ordenes/$ordenId/aceptar',
      token: token,
      body: {
        'tiempo_estimado_respuesta_min': tiempoRespuesta,
        'tiempo_estimado_llegada_min': tiempoLlegada,
        'notas_taller': (notas ?? '').trim(),
      },
    );
  }

  Future<void> rechazarOrden(
      String token, String ordenId, String motivo) async {
    await _api.put(
      '/ordenes/$ordenId/rechazar',
      token: token,
      body: {'motivo_rechazo': motivo.trim()},
    );
  }

  Future<List<TallerMecanicoItem>> listMecanicos(String token,
      {bool? disponible}) async {
    final query = disponible == null ? '' : '?disponible=$disponible';
    final response =
        await _api.get('/operaciones/mecanicos$query', token: token);
    return _asList(response['data']).map(TallerMecanicoItem.fromJson).toList();
  }

  Future<void> asignarMecanico(
    String token,
    String ordenId, {
    required String mecanicoId,
    String? notas,
  }) async {
    await _api.post(
      '/ordenes/$ordenId/asignar-mecanico',
      token: token,
      body: {
        'mecanico_id': mecanicoId,
        'notas': (notas ?? '').trim(),
      },
    );
  }

  Future<List<TallerAsignacionItem>> listAsignaciones(
      String token, String ordenId) async {
    final response =
        await _api.get('/ordenes/$ordenId/asignaciones', token: token);
    return _asList(response['data'])
        .map(TallerAsignacionItem.fromJson)
        .toList();
  }

  Future<List<TallerPresupuestoItem>> listPresupuestos(
      String token, String ordenId) async {
    final response =
        await _api.get('/ordenes/$ordenId/presupuestos', token: token);
    return _asList(response['data'])
        .map(TallerPresupuestoItem.fromJson)
        .toList();
  }

  Future<void> crearPresupuesto(
    String token,
    String ordenId, {
    required String descripcion,
    required double montoRepuestos,
    required double montoManoObra,
  }) async {
    await _api.post(
      '/ordenes/$ordenId/presupuestos',
      token: token,
      body: {
        'descripcion_trabajos': descripcion.trim(),
        'items_detalle': {'items': []},
        'monto_repuestos': montoRepuestos,
        'monto_mano_obra': montoManoObra,
      },
    );
  }

  Future<TallerChatItem> getChatPorOrden(String token, String ordenId) async {
    final response = await _api.get('/ordenes/$ordenId/chat', token: token);
    final data = response['data'];
    if (data is! Map<String, dynamic>) {
      throw ApiException('No se pudo obtener chat');
    }
    return TallerChatItem.fromJson(data);
  }

  Future<List<TallerMensajeItem>> listMensajes(
      String token, String chatId) async {
    final response = await _api.get('/chats/$chatId/mensajes?skip=0&limit=100',
        token: token);
    return _asList(response['data']).map(TallerMensajeItem.fromJson).toList();
  }

  Future<void> enviarMensaje(
      String token, String chatId, String contenido) async {
    await _api.post(
      '/chats/$chatId/mensajes',
      token: token,
      body: {
        'contenido': contenido.trim(),
        'tipo': 'texto',
      },
    );
  }

  Future<void> marcarChatLeido(String token, String chatId) async {
    await _api.put('/chats/$chatId/leer-todo', token: token, body: const {});
  }

  Future<int> contarNoLeidosChat(String token, String chatId) async {
    final response =
        await _api.get('/chats/$chatId/no-leidos/count', token: token);
    final data = response['data'];
    if (data is! Map<String, dynamic>) {
      return 0;
    }
    final raw = data['no_leidos'];
    if (raw is int) {
      return raw;
    }
    return int.tryParse('$raw') ?? 0;
  }

  Future<List<TallerComisionItem>> listComisionesMias(String token) async {
    final response =
        await _api.get('/comisiones/mias?skip=0&limit=100', token: token);
    return _asList(response['data']).map(TallerComisionItem.fromJson).toList();
  }

  Future<void> pagarComision(String token, String comisionId) async {
    await _api
        .post('/comisiones/$comisionId/pagar', token: token, body: const {});
  }

  Future<List<TallerNotificacionItem>> listNotificaciones(
    String token, {
    bool soloNoLeidas = false,
  }) async {
    final response = await _api.get(
      '/notificaciones/?skip=0&limit=50&solo_no_leidas=$soloNoLeidas',
      token: token,
    );
    return _asList(response['data'])
        .map(TallerNotificacionItem.fromJson)
        .toList();
  }

  Future<void> marcarNotificacionLeida(
      String token, String notificacionId) async {
    await _api.put('/notificaciones/$notificacionId/leer',
        token: token, body: const {});
  }

  Future<void> marcarTodasNotificacionesLeidas(String token) async {
    await _api.put('/notificaciones/leer-todas', token: token, body: const {});
  }
}
