import 'package:http/http.dart' as http;

import '../../core/services/api_client.dart';
import 'conductor_models.dart';

class ConductorApiService {
  ConductorApiService(this._api);

  final ApiClient _api;

  List<Map<String, dynamic>> _asList(dynamic value) {
    if (value is! List) {
      return const [];
    }
    return value.whereType<Map<String, dynamic>>().toList();
  }

  Future<List<VehiculoItem>> listVehiculos(String token) async {
    final response = await _api.get('/vehiculos/', token: token);
    return _asList(response['data']).map(VehiculoItem.fromJson).toList();
  }

  Future<void> createVehiculo(
    String token, {
    required String marca,
    required String modelo,
    required int anio,
    required String placa,
    required String tipoCombustible,
    String? color,
  }) async {
    await _api.post(
      '/vehiculos/',
      token: token,
      body: {
        'marca': marca.trim(),
        'modelo': modelo.trim(),
        'anio': anio,
        'placa': placa.trim(),
        'color': (color ?? '').trim(),
        'tipo_combustible': tipoCombustible,
      },
    );
  }

  Future<void> deleteVehiculo(String token, String vehiculoId) async {
    await _api.delete('/vehiculos/$vehiculoId', token: token);
  }

  Future<List<AveriaItem>> listAverias(String token) async {
    final response = await _api.get('/averias/', token: token);
    return _asList(response['data']).map(AveriaItem.fromJson).toList();
  }

  Future<AveriaItem> createAveria(
    String token, {
    required String vehiculoId,
    required String descripcion,
    required double latitud,
    required double longitud,
    required String prioridad,
    String? direccion,
    String? imagePath,
    String? audioPath,
  }) async {
    final fields = <String, String>{
      'vehiculo_id': vehiculoId,
      'descripcion_conductor': descripcion.trim(),
      'latitud_averia': latitud.toString(),
      'longitud_averia': longitud.toString(),
      'direccion_averia': (direccion ?? '').trim(),
      'prioridad': prioridad,
    };

    final files = <http.MultipartFile>[];
    if (imagePath != null && imagePath.isNotEmpty) {
      files.add(await http.MultipartFile.fromPath('archivos', imagePath));
    }
    if (audioPath != null && audioPath.isNotEmpty) {
      files.add(await http.MultipartFile.fromPath('archivos', audioPath));
    }

    final response = await _api.postMultipart(
      '/averias/',
      token: token,
      fields: fields,
      files: files,
    );

    final data = response['data'];
    if (data is! Map<String, dynamic>) {
      throw ApiException('No se pudo crear la avería');
    }
    return AveriaItem.fromJson(data);
  }

  Future<void> agregarMedioAveria(
    String token, {
    required String averiaId,
    required String tipo,
    required String url,
    int ordenVisualizacion = 1,
  }) async {
    await _api.post(
      '/averias/$averiaId/medios',
      token: token,
      body: {
        'tipo': tipo,
        'url': url,
        'orden_visualizacion': ordenVisualizacion,
      },
    );
  }

  Future<AveriaItem> getAveria(String token, String averiaId) async {
    final response = await _api.get('/averias/$averiaId', token: token);
    final data = response['data'];
    if (data is! Map<String, dynamic>) {
      throw ApiException('No se pudo cargar la avería');
    }
    return AveriaItem.fromJson(data);
  }

  Future<DiagnosticoIAItem?> getDiagnosticoAveria(String token, String averiaId) async {
    try {
      return (await getAveria(token, averiaId)).diagnostico;
    } catch (_) {
      return null;
    }
  }

  Future<List<TallerOpcionItem>> getTalleresDisponibles(
    String token, {
    required String averiaId,
    String? categoriaId,
  }) async {
    final url = '/averias/$averiaId/talleres-disponibles'
        '${categoriaId != null ? '?categoria_id=$categoriaId' : ''}';
    final response = await _api.get(url, token: token);
    return _asList(response['data']).map(TallerOpcionItem.fromJson).toList();
  }

  Future<List<CategoriaServicioItem>> listCategoriasServicio(String token) async {
    final response = await _api.get('/categorias-servicio', token: token);
    return _asList(response['data'])
        .map(CategoriaServicioItem.fromJson)
        .toList();
  }

  Future<List<TallerCandidatoItem>> listTalleresCandidatos(
    String token, {
    required String averiaId,
    required String categoriaId,
  }) async {
    final response = await _api.get(
      '/talleres/candidatos?averia_id=$averiaId&categoria_id=$categoriaId',
      token: token,
    );
    return _asList(response['data']).map(TallerCandidatoItem.fromJson).toList();
  }

  Future<OrdenItem> createOrden(
    String token, {
    required String averiaId,
    required String tallerId,
    required String categoriaId,
    required bool esDomicilio,
    String? notasConductor,
  }) async {
    final response = await _api.post(
      '/ordenes/',
      token: token,
      body: {
        'averia_id': averiaId,
        'taller_id': tallerId,
        'categoria_id': categoriaId,
        'es_domicilio': esDomicilio,
        'notas_conductor': (notasConductor ?? '').trim(),
      },
    );
    final data = response['data'];
    if (data is! Map<String, dynamic>) {
      throw ApiException('No se pudo crear la orden');
    }
    return OrdenItem.fromJson(data);
  }

  Future<List<OrdenItem>> listOrdenes(String token) async {
    final response = await _api.get('/ordenes/', token: token);
    return _asList(response['data']).map(OrdenItem.fromJson).toList();
  }

  Future<OrdenItem> getOrden(String token, String ordenId) async {
    final response = await _api.get('/ordenes/$ordenId', token: token);
    final data = response['data'];
    if (data is! Map<String, dynamic>) {
      throw ApiException('No se pudo cargar la orden');
    }
    return OrdenItem.fromJson(data);
  }

  Future<List<HistorialEstadoOrdenItem>> getHistorialOrden(
    String token,
    String ordenId,
  ) async {
    final response =
        await _api.get('/ordenes/$ordenId/historial-estados', token: token);
    return _asList(response['data'])
        .map(HistorialEstadoOrdenItem.fromJson)
        .toList();
  }

  Future<List<AsignacionOrdenItem>> getAsignacionesOrden(
    String token,
    String ordenId,
  ) async {
    final response =
        await _api.get('/ordenes/$ordenId/asignaciones', token: token);
    return _asList(response['data']).map(AsignacionOrdenItem.fromJson).toList();
  }

  Future<List<PresupuestoItem>> getPresupuestosOrden(
    String token,
    String ordenId,
  ) async {
    final response =
        await _api.get('/ordenes/$ordenId/presupuestos', token: token);
    return _asList(response['data']).map(PresupuestoItem.fromJson).toList();
  }

  Future<PresupuestoItem> aprobarPresupuesto(
      String token, String presupuestoId) async {
    final response = await _api.put('/presupuestos/$presupuestoId/aprobar',
        token: token, body: const {});
    final data = response['data'];
    if (data is! Map<String, dynamic>) {
      throw ApiException('No se pudo aprobar el presupuesto');
    }
    return PresupuestoItem.fromJson(data);
  }

  Future<PresupuestoItem> rechazarPresupuesto(
    String token,
    String presupuestoId,
    String motivo,
  ) async {
    final response = await _api.put(
      '/presupuestos/$presupuestoId/rechazar',
      token: token,
      body: {'motivo_rechazo': motivo.trim()},
    );
    final data = response['data'];
    if (data is! Map<String, dynamic>) {
      throw ApiException('No se pudo rechazar el presupuesto');
    }
    return PresupuestoItem.fromJson(data);
  }

  Future<PagoItem> crearPago(
    String token, {
    required String ordenId,
    required String presupuestoId,
    required String metodo,
    required double monto,
  }) async {
    final response = await _api.post(
      '/pagos/',
      token: token,
      body: {
        'orden_id': ordenId,
        'presupuesto_id': presupuestoId,
        'metodo': metodo,
        'monto': monto,
      },
    );
    final data = response['data'];
    if (data is! Map<String, dynamic>) {
      throw ApiException('No se pudo crear el pago');
    }
    return PagoItem.fromJson(data);
  }

  Future<FacturaItem> generarFacturaPorPago(String token, String pagoId) async {
    final response =
        await _api.post('/pagos/$pagoId/factura', token: token, body: const {});
    final data = response['data'];
    if (data is! Map<String, dynamic>) {
      throw ApiException('No se pudo generar la factura');
    }
    return FacturaItem.fromJson(data);
  }

  Future<FacturaItem?> getFacturaPorOrden(String token, String ordenId) async {
    try {
      final response =
          await _api.get('/ordenes/$ordenId/factura', token: token);
      final data = response['data'];
      if (data is! Map<String, dynamic>) {
        return null;
      }
      return FacturaItem.fromJson(data);
    } on ApiException {
      return null;
    }
  }

  Future<CalificacionItem> crearCalificacion(
    String token, {
    required String ordenId,
    required int puntuacion,
    required String comentario,
  }) async {
    final response = await _api.post(
      '/ordenes/$ordenId/calificaciones',
      token: token,
      body: {
        'puntuacion': puntuacion,
        'comentario': comentario.trim(),
      },
    );
    final data = response['data'];
    if (data is! Map<String, dynamic>) {
      throw ApiException('No se pudo crear la calificación');
    }
    return CalificacionItem.fromJson(data);
  }

  Future<List<CalificacionItem>> listCalificaciones(
    String token,
    String ordenId,
  ) async {
    final response =
        await _api.get('/ordenes/$ordenId/calificaciones', token: token);
    return _asList(response['data']).map(CalificacionItem.fromJson).toList();
  }

  Future<ChatItem> getChatPorOrden(String token, String ordenId) async {
    final response = await _api.get('/ordenes/$ordenId/chat', token: token);
    final data = response['data'];
    if (data is! Map<String, dynamic>) {
      throw ApiException('No se pudo cargar el chat');
    }
    return ChatItem.fromJson(data);
  }

  Future<List<MensajeItem>> listMensajes(String token, String chatId) async {
    final response = await _api.get('/chats/$chatId/mensajes?skip=0&limit=100',
        token: token);
    return _asList(response['data']).map(MensajeItem.fromJson).toList();
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

  Future<void> marcarMensajeLeido(
      String token, String chatId, String mensajeId) async {
    await _api.put('/chats/$chatId/mensajes/$mensajeId/leer',
        token: token, body: const {});
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
    final noLeidos = data['no_leidos'];
    if (noLeidos is int) {
      return noLeidos;
    }
    return int.tryParse('$noLeidos') ?? 0;
  }

  Future<void> cancelarOrden(
    String token, {
    required String ordenId,
    required String motivo,
  }) async {
    await _api.put(
      '/ordenes/$ordenId/cancelar',
      token: token,
      body: {
        'motivo_cancelacion': motivo.trim(),
      },
    );
  }
}
