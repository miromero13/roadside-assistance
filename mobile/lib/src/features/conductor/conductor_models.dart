class VehiculoItem {
  VehiculoItem({
    required this.id,
    required this.marca,
    required this.modelo,
    required this.anio,
    required this.placa,
    required this.color,
    required this.tipoCombustible,
  });

  final String id;
  final String marca;
  final String modelo;
  final int anio;
  final String placa;
  final String? color;
  final String tipoCombustible;

  factory VehiculoItem.fromJson(Map<String, dynamic> json) {
    return VehiculoItem(
      id: json['id'] as String? ?? '',
      marca: json['marca'] as String? ?? '',
      modelo: json['modelo'] as String? ?? '',
      anio: json['anio'] as int? ?? 0,
      placa: json['placa'] as String? ?? '',
      color: json['color'] as String?,
      tipoCombustible: json['tipo_combustible'] as String? ?? 'gasolina',
    );
  }
}

class AveriaItem {
  AveriaItem({
    required this.id,
    required this.vehiculoId,
    required this.descripcion,
    required this.prioridad,
    required this.estado,
    required this.latitud,
    required this.longitud,
    required this.direccion,
    this.imagenPrincipalUrl,
    this.medios = const [],
    this.diagnostico,
    this.talleresDisponibles = const [],
  });

  final String id;
  final String vehiculoId;
  final String descripcion;
  final String prioridad;
  final String estado;
  final double latitud;
  final double longitud;
  final String? direccion;
  final String? imagenPrincipalUrl;
  final List<MedioAveriaItem> medios;
  final DiagnosticoIAItem? diagnostico;
  final List<TallerOpcionItem> talleresDisponibles;

  factory AveriaItem.fromJson(Map<String, dynamic> json) {
    double toDouble(dynamic value) {
      if (value is num) {
        return value.toDouble();
      }
      return double.tryParse('$value') ?? 0;
    }

    final medios = json['medios'] as List?;
    final diagnostico = json['diagnostico_ia'];
    final talleres = json['talleres_disponibles'] as List?;
    return AveriaItem(
      id: json['id'] as String? ?? '',
      vehiculoId: json['vehiculo_id'] as String? ?? '',
      descripcion: json['descripcion_conductor'] as String? ?? '',
      prioridad: json['prioridad'] as String? ?? 'media',
      estado: json['estado'] as String? ?? 'registrada',
      latitud: toDouble(json['latitud_averia']),
      longitud: toDouble(json['longitud_averia']),
      direccion: json['direccion_averia'] as String?,
      imagenPrincipalUrl: json['imagen_principal_url'] as String?,
      medios: medios != null
          ? medios.whereType<Map<String, dynamic>>().map(MedioAveriaItem.fromJson).toList()
          : [],
      diagnostico: diagnostico is Map<String, dynamic>
          ? DiagnosticoIAItem.fromJson(diagnostico)
          : null,
      talleresDisponibles: talleres != null
          ? talleres.whereType<Map<String, dynamic>>().map(TallerOpcionItem.fromJson).toList()
          : [],
    );
  }
}

class MedioAveriaItem {
  MedioAveriaItem({
    required this.id,
    required this.tipo,
    required this.url,
    required this.orden,
  });

  final String id;
  final String tipo;
  final String url;
  final int orden;

  factory MedioAveriaItem.fromJson(Map<String, dynamic> json) {
    return MedioAveriaItem(
      id: json['id'] as String? ?? '',
      tipo: json['tipo'] as String? ?? '',
      url: json['url'] as String? ?? '',
      orden: json['orden_visualizacion'] as int? ?? 1,
    );
  }
}

class DiagnosticoIAItem {
  DiagnosticoIAItem({
    required this.categoriaId,
    required this.categoria,
    required this.confianza,
    required this.diagnostico,
    required this.notasTaller,
    required this.urgencia,
    required this.danosVisibles,
    required this.costoMin,
    required this.costoMax,
    required this.requiereRevisionManual,
    required this.resumen,
  });

  final String? categoriaId;
  final String categoria;
  final double confianza;
  final String diagnostico;
  final String notasTaller;
  final String urgencia;
  final String? danosVisibles;
  final double? costoMin;
  final double? costoMax;
  final bool requiereRevisionManual;
  final String? resumen;

  factory DiagnosticoIAItem.fromJson(Map<String, dynamic> json) {
    double toDouble(dynamic value) {
      if (value is num) {
        return value.toDouble();
      }
      return double.tryParse('$value') ?? 0;
    }

    String categoria = 'incierto';
    final categoriaValue = json['categoria'];
    if (categoriaValue is Map<String, dynamic>) {
      categoria = categoriaValue['nombre'] as String? ?? categoria;
    } else if (categoriaValue is String && categoriaValue.isNotEmpty) {
      categoria = categoriaValue;
    }

    return DiagnosticoIAItem(
      categoriaId: json['categoria_id'] as String?,
      categoria: categoria,
      confianza: toDouble(json['confianza_categoria'] ?? json['nivel_confianza']),
      diagnostico: (json['diagnostico'] ?? json['analisis']) as String? ?? '',
      notasTaller: (json['notas_taller'] ?? json['recomendacion']) as String? ?? '',
      urgencia: json['urgencia'] as String? ?? 'media',
      danosVisibles: json['danos_visibles'] as String?,
      costoMin: json['costo_estimado_min'] != null ? toDouble(json['costo_estimado_min']) : null,
      costoMax: json['costo_estimado_max'] != null ? toDouble(json['costo_estimado_max']) : null,
      requiereRevisionManual: json['requiere_revision_manual'] as bool? ?? false,
      resumen: json['resumen_automatico'] as String?,
    );
  }
}

class CategoriaServicioItem {
  CategoriaServicioItem({
    required this.id,
    required this.nombre,
  });

  final String id;
  final String nombre;

  factory CategoriaServicioItem.fromJson(Map<String, dynamic> json) {
    return CategoriaServicioItem(
      id: json['id'] as String? ?? '',
      nombre: json['nombre'] as String? ?? '',
    );
  }
}

class TallerOpcionItem {
  TallerOpcionItem({
    required this.tallerId,
    required this.nombre,
    required this.distanciaKm,
    required this.tiempoAproximadoMin,
    required this.radioCobertura,
    required this.calificacionPromedio,
    required this.aceptaDomicilio,
  });

  final String tallerId;
  final String nombre;
  final double distanciaKm;
  final int? tiempoAproximadoMin;
  final double radioCobertura;
  final double calificacionPromedio;
  final bool aceptaDomicilio;

  factory TallerOpcionItem.fromJson(Map<String, dynamic> json) {
    double toDouble(dynamic value) {
      if (value is num) {
        return value.toDouble();
      }
      return double.tryParse('$value') ?? 0;
    }

    return TallerOpcionItem(
      tallerId: json['taller_id'] as String? ?? '',
      nombre: json['nombre'] as String? ?? 'Taller',
      distanciaKm: toDouble(json['distancia_km']),
      tiempoAproximadoMin: json['tiempo_aproximado_min'] as int?,
      radioCobertura: toDouble(json['radio_cobertura_km']),
      calificacionPromedio: toDouble(json['calificacion_promedio']),
      aceptaDomicilio: json['acepta_domicilio'] as bool? ?? false,
    );
  }
}

class TallerCandidatoItem {
  TallerCandidatoItem({
    required this.tallerId,
    required this.nombre,
    required this.distanciaKm,
    required this.calificacionPromedio,
  });

  final String tallerId;
  final String nombre;
  final double distanciaKm;
  final double calificacionPromedio;

  factory TallerCandidatoItem.fromJson(Map<String, dynamic> json) {
    double toDouble(dynamic value) {
      if (value is num) {
        return value.toDouble();
      }
      return double.tryParse('$value') ?? 0;
    }

    return TallerCandidatoItem(
      tallerId: json['taller_id'] as String? ?? '',
      nombre: json['nombre'] as String? ?? 'Taller',
      distanciaKm: toDouble(json['distancia_km']),
      calificacionPromedio: toDouble(json['calificacion_promedio']),
    );
  }
}

class OrdenItem {
  OrdenItem({
    required this.id,
    required this.averiaId,
    required this.tallerId,
    required this.estado,
    required this.creadoEn,
    required this.notasConductor,
    required this.motivoCancelacion,
  });

  final String id;
  final String averiaId;
  final String tallerId;
  final String estado;
  final String creadoEn;
  final String? notasConductor;
  final String? motivoCancelacion;

  factory OrdenItem.fromJson(Map<String, dynamic> json) {
    return OrdenItem(
      id: json['id'] as String? ?? '',
      averiaId: json['averia_id'] as String? ?? '',
      tallerId: json['taller_id'] as String? ?? '',
      estado: json['estado'] as String? ?? '',
      creadoEn: json['creado_en'] as String? ?? '',
      notasConductor: json['notas_conductor'] as String?,
      motivoCancelacion: json['motivo_cancelacion'] as String?,
    );
  }
}

class HistorialEstadoOrdenItem {
  HistorialEstadoOrdenItem({
    required this.id,
    required this.estadoAnterior,
    required this.estadoNuevo,
    required this.observacion,
    required this.creadoEn,
  });

  final String id;
  final String? estadoAnterior;
  final String estadoNuevo;
  final String? observacion;
  final String creadoEn;

  factory HistorialEstadoOrdenItem.fromJson(Map<String, dynamic> json) {
    return HistorialEstadoOrdenItem(
      id: json['id'] as String? ?? '',
      estadoAnterior: json['estado_anterior'] as String?,
      estadoNuevo: json['estado_nuevo'] as String? ?? '',
      observacion: json['observacion'] as String?,
      creadoEn: json['creado_en'] as String? ?? '',
    );
  }
}

class AsignacionOrdenItem {
  AsignacionOrdenItem({
    required this.id,
    required this.mecanicoId,
    required this.estado,
    required this.notas,
    required this.asignadoEn,
  });

  final String id;
  final String mecanicoId;
  final String estado;
  final String? notas;
  final String asignadoEn;

  factory AsignacionOrdenItem.fromJson(Map<String, dynamic> json) {
    return AsignacionOrdenItem(
      id: json['id'] as String? ?? '',
      mecanicoId: json['mecanico_id'] as String? ?? '',
      estado: json['estado'] as String? ?? '',
      notas: json['notas'] as String?,
      asignadoEn: json['asignado_en'] as String? ?? '',
    );
  }
}

class PresupuestoItem {
  PresupuestoItem({
    required this.id,
    required this.version,
    required this.estado,
    required this.descripcionTrabajos,
    required this.montoTotal,
    required this.montoRepuestos,
    required this.montoManoObra,
    required this.motivoRechazo,
  });

  final String id;
  final int version;
  final String estado;
  final String descripcionTrabajos;
  final double montoTotal;
  final double montoRepuestos;
  final double montoManoObra;
  final String? motivoRechazo;

  bool get aprobable => estado == 'enviado';
  bool get pagable => estado == 'aprobado';

  factory PresupuestoItem.fromJson(Map<String, dynamic> json) {
    return PresupuestoItem(
      id: json['id'] as String? ?? '',
      version: json['version'] as int? ?? 0,
      estado: json['estado'] as String? ?? '',
      descripcionTrabajos: json['descripcion_trabajos'] as String? ?? '',
      montoTotal: _toDouble(json['monto_total']),
      montoRepuestos: _toDouble(json['monto_repuestos']),
      montoManoObra: _toDouble(json['monto_mano_obra']),
      motivoRechazo: json['motivo_rechazo'] as String?,
    );
  }
}

class PagoItem {
  PagoItem({
    required this.id,
    required this.estado,
    required this.metodo,
    required this.monto,
  });

  final String id;
  final String estado;
  final String metodo;
  final double monto;

  factory PagoItem.fromJson(Map<String, dynamic> json) {
    return PagoItem(
      id: json['id'] as String? ?? '',
      estado: json['estado'] as String? ?? '',
      metodo: json['metodo'] as String? ?? '',
      monto: _toDouble(json['monto']),
    );
  }
}

class FacturaItem {
  FacturaItem({
    required this.id,
    required this.numeroFactura,
    required this.total,
    required this.emitidaEn,
    required this.pdfUrl,
  });

  final String id;
  final String numeroFactura;
  final double total;
  final String emitidaEn;
  final String? pdfUrl;

  factory FacturaItem.fromJson(Map<String, dynamic> json) {
    return FacturaItem(
      id: json['id'] as String? ?? '',
      numeroFactura: json['numero_factura'] as String? ?? '',
      total: _toDouble(json['total']),
      emitidaEn: json['emitida_en'] as String? ?? '',
      pdfUrl: json['pdf_url'] as String?,
    );
  }
}

class CalificacionItem {
  CalificacionItem({
    required this.id,
    required this.puntuacion,
    required this.comentario,
    required this.creadoEn,
  });

  final String id;
  final int puntuacion;
  final String? comentario;
  final String creadoEn;

  factory CalificacionItem.fromJson(Map<String, dynamic> json) {
    return CalificacionItem(
      id: json['id'] as String? ?? '',
      puntuacion: json['puntuacion'] as int? ?? 0,
      comentario: json['comentario'] as String?,
      creadoEn: json['creado_en'] as String? ?? '',
    );
  }
}

class ChatItem {
  ChatItem({
    required this.id,
    required this.ordenId,
  });

  final String id;
  final String ordenId;

  factory ChatItem.fromJson(Map<String, dynamic> json) {
    return ChatItem(
      id: json['id'] as String? ?? '',
      ordenId: json['orden_id'] as String? ?? '',
    );
  }
}

class MensajeItem {
  MensajeItem({
    required this.id,
    required this.chatId,
    required this.remitenteId,
    required this.contenido,
    required this.leido,
    required this.enviadoEn,
  });

  final String id;
  final String chatId;
  final String remitenteId;
  final String? contenido;
  final bool leido;
  final String enviadoEn;

  factory MensajeItem.fromJson(Map<String, dynamic> json) {
    return MensajeItem(
      id: json['id'] as String? ?? '',
      chatId: json['chat_id'] as String? ?? '',
      remitenteId: json['remitente_id'] as String? ?? '',
      contenido: json['contenido'] as String?,
      leido: json['leido'] as bool? ?? false,
      enviadoEn: json['enviado_en'] as String? ?? '',
    );
  }
}

double _toDouble(dynamic value) {
  if (value is num) {
    return value.toDouble();
  }
  return double.tryParse('$value') ?? 0;
}
