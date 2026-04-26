class TallerOrdenItem {
  TallerOrdenItem({
    required this.id,
    required this.averiaId,
    required this.tallerId,
    required this.estado,
    required this.creadoEn,
    required this.notasConductor,
  });

  final String id;
  final String averiaId;
  final String tallerId;
  final String estado;
  final String creadoEn;
  final String? notasConductor;

  bool get pendienteRespuesta => estado == 'pendiente_respuesta';

  factory TallerOrdenItem.fromJson(Map<String, dynamic> json) {
    return TallerOrdenItem(
      id: json['id'] as String? ?? '',
      averiaId: json['averia_id'] as String? ?? '',
      tallerId: json['taller_id'] as String? ?? '',
      estado: json['estado'] as String? ?? '',
      creadoEn: json['creado_en'] as String? ?? '',
      notasConductor: json['notas_conductor'] as String?,
    );
  }
}

class TallerMecanicoItem {
  TallerMecanicoItem({
    required this.id,
    required this.especialidad,
    required this.disponible,
    required this.activo,
  });

  final String id;
  final String? especialidad;
  final bool disponible;
  final bool activo;

  factory TallerMecanicoItem.fromJson(Map<String, dynamic> json) {
    return TallerMecanicoItem(
      id: json['id'] as String? ?? '',
      especialidad: json['especialidad'] as String?,
      disponible: json['disponible'] as bool? ?? false,
      activo: json['activo'] as bool? ?? false,
    );
  }
}

class TallerAsignacionItem {
  TallerAsignacionItem({
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

  factory TallerAsignacionItem.fromJson(Map<String, dynamic> json) {
    return TallerAsignacionItem(
      id: json['id'] as String? ?? '',
      mecanicoId: json['mecanico_id'] as String? ?? '',
      estado: json['estado'] as String? ?? '',
      notas: json['notas'] as String?,
      asignadoEn: json['asignado_en'] as String? ?? '',
    );
  }
}

class TallerPresupuestoItem {
  TallerPresupuestoItem({
    required this.id,
    required this.version,
    required this.estado,
    required this.descripcionTrabajos,
    required this.montoTotal,
  });

  final String id;
  final int version;
  final String estado;
  final String descripcionTrabajos;
  final double montoTotal;

  factory TallerPresupuestoItem.fromJson(Map<String, dynamic> json) {
    return TallerPresupuestoItem(
      id: json['id'] as String? ?? '',
      version: json['version'] as int? ?? 0,
      estado: json['estado'] as String? ?? '',
      descripcionTrabajos: json['descripcion_trabajos'] as String? ?? '',
      montoTotal: _toDouble(json['monto_total']),
    );
  }
}

class TallerComisionItem {
  TallerComisionItem({
    required this.id,
    required this.estado,
    required this.montoComision,
    required this.creadoEn,
  });

  final String id;
  final String estado;
  final double montoComision;
  final String creadoEn;

  bool get pendiente => estado == 'pendiente';

  factory TallerComisionItem.fromJson(Map<String, dynamic> json) {
    return TallerComisionItem(
      id: json['id'] as String? ?? '',
      estado: json['estado'] as String? ?? '',
      montoComision: _toDouble(json['monto_comision']),
      creadoEn: json['creado_en'] as String? ?? '',
    );
  }
}

class TallerNotificacionItem {
  TallerNotificacionItem({
    required this.id,
    required this.titulo,
    required this.mensaje,
    required this.tipo,
    required this.leida,
    required this.creadoEn,
  });

  final String id;
  final String titulo;
  final String mensaje;
  final String tipo;
  final bool leida;
  final String creadoEn;

  factory TallerNotificacionItem.fromJson(Map<String, dynamic> json) {
    return TallerNotificacionItem(
      id: json['id'] as String? ?? '',
      titulo: json['titulo'] as String? ?? '',
      mensaje: json['mensaje'] as String? ?? '',
      tipo: json['tipo'] as String? ?? '',
      leida: json['leida'] as bool? ?? false,
      creadoEn: json['creado_en'] as String? ?? '',
    );
  }
}

class TallerChatItem {
  TallerChatItem({
    required this.id,
    required this.ordenId,
  });

  final String id;
  final String ordenId;

  factory TallerChatItem.fromJson(Map<String, dynamic> json) {
    return TallerChatItem(
      id: json['id'] as String? ?? '',
      ordenId: json['orden_id'] as String? ?? '',
    );
  }
}

class TallerMensajeItem {
  TallerMensajeItem({
    required this.id,
    required this.remitenteId,
    required this.contenido,
    required this.leido,
    required this.enviadoEn,
  });

  final String id;
  final String remitenteId;
  final String? contenido;
  final bool leido;
  final String enviadoEn;

  factory TallerMensajeItem.fromJson(Map<String, dynamic> json) {
    return TallerMensajeItem(
      id: json['id'] as String? ?? '',
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
