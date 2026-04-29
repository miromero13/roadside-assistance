from __future__ import annotations

from datetime import datetime, time, timedelta
from decimal import Decimal
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).resolve().parents[1]))

import app.models  # noqa: F401
from app.auth.hash import hash_password
from app.core.database import Base, SessionLocal, engine
from app.models.averia import Averia, DiagnosticoIA, MedioAveria
from app.models.comunicacion import Calificacion, Chat, DispositivoPush, Mensaje, Notificacion
from app.models.enums import (
    ClasificacionIA,
    DiaSemana,
    EstadoAsignacion,
    EstadoAveria,
    EstadoComision,
    EstadoOrdenServicio,
    EstadoPago,
    EstadoPresupuesto,
    MedioTipo,
    MetodoPago,
    PlataformaPush,
    Prioridad,
    TipoCalificador,
    TipoCombustible,
    TipoMensaje,
    TipoNotificacion,
    UserRole,
)
from app.models.finanzas import ComisionPlataforma, Factura, Pago, Presupuesto
from app.models.orden import AsignacionOrden, HistorialEstadoOrden, MetricaServicio, OrdenServicio
from app.models.taller import (
    BloqueoTaller,
    CategoriaServicio,
    HorarioTaller,
    Mecanico,
    ServicioTaller,
    Taller,
)
from app.models.usuario import Usuario, Vehiculo


def d(value: str) -> Decimal:
    return Decimal(value)


def ensure_usuario(
    db,
    *,
    nombre: str,
    apellido: str,
    email: str,
    telefono: str,
    password: str,
    rol: UserRole,
    activo: bool = True,
) -> Usuario:
    user = db.query(Usuario).filter(Usuario.email == email).first()
    if user:
        return user

    user = Usuario(
        nombre=nombre,
        apellido=apellido,
        email=email,
        telefono=telefono,
        password_hash=hash_password(password),
        rol=rol,
        activo=activo,
    )
    db.add(user)
    db.flush()
    return user


def ensure_categoria(db, nombre: str, descripcion: str) -> CategoriaServicio:
    row = db.query(CategoriaServicio).filter(CategoriaServicio.nombre == nombre).first()
    if row:
        return row

    row = CategoriaServicio(nombre=nombre, descripcion=descripcion, activo=True)
    db.add(row)
    db.flush()
    return row


def ensure_taller(
    db,
    *,
    usuario: Usuario,
    nombre: str,
    descripcion: str,
    direccion: str,
    latitud: str,
    longitud: str,
    radio_cobertura_km: str,
    telefono: str,
    acepta_domicilio: bool,
    calificacion_promedio: str,
) -> Taller:
    row = db.query(Taller).filter(Taller.usuario_id == usuario.id).first()
    if row:
        return row

    row = Taller(
        usuario_id=usuario.id,
        nombre=nombre,
        descripcion=descripcion,
        direccion=direccion,
        latitud=d(latitud),
        longitud=d(longitud),
        radio_cobertura_km=d(radio_cobertura_km),
        telefono=telefono,
        acepta_domicilio=acepta_domicilio,
        activo=True,
        calificacion_promedio=d(calificacion_promedio),
    )
    db.add(row)
    db.flush()
    return row


def ensure_mecanico(
    db,
    *,
    usuario: Usuario,
    taller: Taller,
    especialidad: str,
    disponible: bool,
) -> Mecanico:
    row = db.query(Mecanico).filter(Mecanico.usuario_id == usuario.id).first()
    if row:
        return row

    row = Mecanico(
        usuario_id=usuario.id,
        taller_id=taller.id,
        especialidad=especialidad,
        disponible=disponible,
        activo=True,
    )
    db.add(row)
    db.flush()
    return row


def ensure_horario(
    db,
    *,
    taller: Taller,
    dia_semana: DiaSemana,
    hora_apertura: time,
    hora_cierre: time,
    disponible: bool,
) -> HorarioTaller:
    row = (
        db.query(HorarioTaller)
        .filter(HorarioTaller.taller_id == taller.id, HorarioTaller.dia_semana == dia_semana)
        .first()
    )
    if row:
        return row

    row = HorarioTaller(
        taller_id=taller.id,
        dia_semana=dia_semana,
        hora_apertura=hora_apertura,
        hora_cierre=hora_cierre,
        disponible=disponible,
    )
    db.add(row)
    db.flush()
    return row


def ensure_bloqueo(
    db,
    *,
    taller: Taller,
    fecha_inicio: datetime,
    fecha_fin: datetime,
    motivo: str,
) -> BloqueoTaller:
    row = (
        db.query(BloqueoTaller)
        .filter(
            BloqueoTaller.taller_id == taller.id,
            BloqueoTaller.fecha_inicio == fecha_inicio,
            BloqueoTaller.fecha_fin == fecha_fin,
        )
        .first()
    )
    if row:
        return row

    row = BloqueoTaller(
        taller_id=taller.id,
        fecha_inicio=fecha_inicio,
        fecha_fin=fecha_fin,
        motivo=motivo,
    )
    db.add(row)
    db.flush()
    return row


def ensure_servicio(
    db,
    *,
    taller: Taller,
    categoria: CategoriaServicio,
    descripcion: str,
    precio_min: str,
    precio_max: str,
    tiempo_min: int,
    servicio_movil: bool,
) -> ServicioTaller:
    row = (
        db.query(ServicioTaller)
        .filter(ServicioTaller.taller_id == taller.id, ServicioTaller.categoria_id == categoria.id)
        .first()
    )
    if row:
        return row

    row = ServicioTaller(
        taller_id=taller.id,
        categoria_id=categoria.id,
        descripcion=descripcion,
        precio_base_min=d(precio_min),
        precio_base_max=d(precio_max),
        tiempo_estimado_min=tiempo_min,
        servicio_movil=servicio_movil,
        activo=True,
    )
    db.add(row)
    db.flush()
    return row


def ensure_vehiculo(
    db,
    *,
    usuario: Usuario,
    marca: str,
    modelo: str,
    anio: int,
    placa: str,
    color: str,
    combustible: TipoCombustible,
) -> Vehiculo:
    row = db.query(Vehiculo).filter(Vehiculo.placa == placa).first()
    if row:
        return row

    row = Vehiculo(
        usuario_id=usuario.id,
        marca=marca,
        modelo=modelo,
        anio=anio,
        placa=placa,
        color=color,
        tipo_combustible=combustible,
    )
    db.add(row)
    db.flush()
    return row


def ensure_averia(
    db,
    *,
    usuario: Usuario,
    vehiculo: Vehiculo,
    descripcion: str,
    latitud: str,
    longitud: str,
    direccion: str,
    prioridad: Prioridad,
    estado: EstadoAveria,
    creada_hace_horas: int,
) -> Averia:
    row = (
        db.query(Averia)
        .filter(Averia.vehiculo_id == vehiculo.id, Averia.descripcion_conductor == descripcion)
        .first()
    )
    if row:
        return row

    row = Averia(
        usuario_id=usuario.id,
        vehiculo_id=vehiculo.id,
        descripcion_conductor=descripcion,
        latitud_averia=d(latitud),
        longitud_averia=d(longitud),
        direccion_averia=direccion,
        prioridad=prioridad,
        estado=estado,
        creado_en=datetime.utcnow() - timedelta(hours=creada_hace_horas),
    )
    db.add(row)
    db.flush()
    return row


def ensure_medio_averia(db, *, averia: Averia, tipo: MedioTipo, url: str, orden: int = 1) -> MedioAveria:
    row = (
        db.query(MedioAveria)
        .filter(MedioAveria.averia_id == averia.id, MedioAveria.url == url)
        .first()
    )
    if row:
        return row

    row = MedioAveria(averia_id=averia.id, tipo=tipo, url=url, orden_visualizacion=orden)
    db.add(row)
    db.flush()
    return row


def ensure_diagnostico(
    db,
    *,
    averia: Averia,
    categoria: CategoriaServicio,
    clasificacion: ClasificacionIA,
    urgencia: Prioridad,
    analisis: str,
    costo_min: str,
    costo_max: str,
) -> DiagnosticoIA:
    row = db.query(DiagnosticoIA).filter(DiagnosticoIA.averia_id == averia.id).first()
    if row:
        return row

    row = DiagnosticoIA(
        averia_id=averia.id,
        categoria_id=categoria.id,
        clasificacion=clasificacion,
        urgencia=urgencia,
        nivel_confianza=d("0.89"),
        analisis=analisis,
        resumen_automatico="Revision automatica con alta probabilidad de coincidencia.",
        recomendacion="Asignar tecnico y validar en sitio.",
        danos_visibles="No aplica en esta simulacion",
        costo_estimado_min=d(costo_min),
        costo_estimado_max=d(costo_max),
        requiere_revision_manual=False,
        historial_conversacion={"mensajes": [{"rol": "sistema", "texto": "diagnostico semilla"}]},
    )
    db.add(row)
    db.flush()
    return row


def ensure_orden(
    db,
    *,
    averia: Averia,
    taller: Taller,
    categoria: CategoriaServicio,
    estado: EstadoOrdenServicio,
    notas_conductor: str,
    notas_taller: str | None,
    motivo_rechazo: str | None,
    motivo_cancelacion: str | None,
    tiempo_resp: int | None,
    tiempo_llegada: int | None,
    creado_hace_horas: int,
) -> OrdenServicio:
    row = db.query(OrdenServicio).filter(OrdenServicio.notas_conductor == notas_conductor).first()
    if row:
        return row

    created_at = datetime.utcnow() - timedelta(hours=creado_hace_horas)
    responded_at = created_at + timedelta(minutes=8) if estado != EstadoOrdenServicio.PENDIENTE_RESPUESTA else None
    accepted_at = created_at + timedelta(minutes=10) if estado in {
        EstadoOrdenServicio.ACEPTADA,
        EstadoOrdenServicio.TECNICO_ASIGNADO,
        EstadoOrdenServicio.EN_CAMINO,
        EstadoOrdenServicio.EN_PROCESO,
        EstadoOrdenServicio.COMPLETADA,
    } else None
    rejected_at = created_at + timedelta(minutes=9) if estado == EstadoOrdenServicio.RECHAZADA else None
    completed_at = created_at + timedelta(hours=2) if estado == EstadoOrdenServicio.COMPLETADA else None
    canceled_at = created_at + timedelta(minutes=30) if estado == EstadoOrdenServicio.CANCELADA else None
    started_at = created_at + timedelta(minutes=40) if estado in {
        EstadoOrdenServicio.EN_PROCESO,
        EstadoOrdenServicio.COMPLETADA,
    } else None

    row = OrdenServicio(
        averia_id=averia.id,
        taller_id=taller.id,
        categoria_id=categoria.id,
        estado=estado,
        es_domicilio=True,
        notas_conductor=notas_conductor,
        notas_taller=notas_taller,
        motivo_rechazo=motivo_rechazo,
        motivo_cancelacion=motivo_cancelacion,
        tiempo_estimado_respuesta_min=tiempo_resp,
        tiempo_estimado_llegada_min=tiempo_llegada,
        creado_en=created_at,
        respondido_en=responded_at,
        aceptado_en=accepted_at,
        rechazado_en=rejected_at,
        iniciado_en=started_at,
        completado_en=completed_at,
        cancelado_en=canceled_at,
    )
    db.add(row)
    db.flush()
    return row


def ensure_historial(
    db,
    *,
    orden: OrdenServicio,
    estado_anterior: str | None,
    estado_nuevo: str,
    usuario_id,
    observacion: str,
    creado_en: datetime,
) -> HistorialEstadoOrden:
    row = (
        db.query(HistorialEstadoOrden)
        .filter(
            HistorialEstadoOrden.orden_id == orden.id,
            HistorialEstadoOrden.estado_nuevo == estado_nuevo,
            HistorialEstadoOrden.observacion == observacion,
        )
        .first()
    )
    if row:
        return row

    row = HistorialEstadoOrden(
        orden_id=orden.id,
        estado_anterior=estado_anterior,
        estado_nuevo=estado_nuevo,
        usuario_id=usuario_id,
        observacion=observacion,
        creado_en=creado_en,
    )
    db.add(row)
    db.flush()
    return row


def ensure_asignacion(
    db,
    *,
    orden: OrdenServicio,
    mecanico: Mecanico,
    asignado_por: Usuario,
    estado: EstadoAsignacion,
    notas: str,
    asignado_en: datetime,
) -> AsignacionOrden:
    row = (
        db.query(AsignacionOrden)
        .filter(AsignacionOrden.orden_id == orden.id, AsignacionOrden.mecanico_id == mecanico.id)
        .first()
    )
    if row:
        return row

    salida = asignado_en + timedelta(minutes=10) if estado in {EstadoAsignacion.EN_CAMINO, EstadoAsignacion.ATENDIENDO, EstadoAsignacion.FINALIZADO} else None
    llegada = asignado_en + timedelta(minutes=30) if estado in {EstadoAsignacion.ATENDIENDO, EstadoAsignacion.FINALIZADO} else None
    finalizado = asignado_en + timedelta(minutes=90) if estado == EstadoAsignacion.FINALIZADO else None

    row = AsignacionOrden(
        orden_id=orden.id,
        mecanico_id=mecanico.id,
        asignado_por=asignado_por.id,
        estado=estado,
        notas=notas,
        asignado_en=asignado_en,
        salida_en=salida,
        llegada_en=llegada,
        finalizado_en=finalizado,
    )
    db.add(row)
    db.flush()
    return row


def ensure_presupuesto(
    db,
    *,
    orden: OrdenServicio,
    version: int,
    descripcion: str,
    repuestos: str,
    mano_obra: str,
    estado: EstadoPresupuesto,
    motivo_rechazo: str | None,
    enviado_en: datetime,
    respondido_en: datetime | None,
) -> Presupuesto:
    row = (
        db.query(Presupuesto)
        .filter(Presupuesto.orden_id == orden.id, Presupuesto.version == version)
        .first()
    )
    if row:
        return row

    rep = d(repuestos)
    mo = d(mano_obra)
    total = rep + mo
    row = Presupuesto(
        orden_id=orden.id,
        version=version,
        descripcion_trabajos=descripcion,
        items_detalle={
            "items": [
                {"concepto": "Repuestos", "cantidad": 1, "precio": float(rep)},
                {"concepto": "Mano de obra", "cantidad": 1, "precio": float(mo)},
            ]
        },
        monto_repuestos=rep,
        monto_mano_obra=mo,
        monto_total=total,
        estado=estado,
        motivo_rechazo=motivo_rechazo,
        enviado_en=enviado_en,
        respondido_en=respondido_en,
    )
    db.add(row)
    db.flush()
    return row


def ensure_pago(
    db,
    *,
    orden: OrdenServicio,
    presupuesto: Presupuesto,
    monto: str,
    metodo: MetodoPago,
    estado: EstadoPago,
    referencia: str,
    creado_en: datetime,
    pagado_en: datetime | None,
) -> Pago:
    row = db.query(Pago).filter(Pago.referencia_externa == referencia).first()
    if row:
        return row

    row = Pago(
        orden_id=orden.id,
        presupuesto_id=presupuesto.id,
        monto=d(monto),
        metodo=metodo,
        estado=estado,
        referencia_externa=referencia,
        creado_en=creado_en,
        pagado_en=pagado_en,
    )
    db.add(row)
    db.flush()
    return row


def ensure_comision(
    db,
    *,
    orden: OrdenServicio,
    pago: Pago,
    base: str,
    porcentaje: str,
    estado: EstadoComision,
    creado_en: datetime,
) -> ComisionPlataforma:
    row = db.query(ComisionPlataforma).filter(ComisionPlataforma.pago_id == pago.id).first()
    if row:
        return row

    base_dec = d(base)
    pct = d(porcentaje)
    row = ComisionPlataforma(
        orden_id=orden.id,
        pago_id=pago.id,
        monto_base=base_dec,
        porcentaje=pct,
        monto_comision=(base_dec * pct) / d("100"),
        estado=estado,
        creado_en=creado_en,
    )
    db.add(row)
    db.flush()
    return row


def ensure_factura(
    db,
    *,
    pago: Pago,
    orden: OrdenServicio,
    numero: str,
    total: str,
    emitida_en: datetime,
) -> Factura:
    row = db.query(Factura).filter(Factura.pago_id == pago.id).first()
    if row:
        return row

    total_dec = d(total)
    row = Factura(
        pago_id=pago.id,
        orden_id=orden.id,
        numero_factura=numero,
        datos_emisor={"nombre": "ACI Plataforma", "nit": "1234567011"},
        datos_receptor={"nombre": "Cliente Demo", "nit": "0"},
        items={
            "items": [
                {"descripcion": "Servicio mecanico", "cantidad": 1, "precio_unitario": float(total_dec)}
            ]
        },
        subtotal=total_dec,
        impuesto=d("0.00"),
        total=total_dec,
        pdf_url=None,
        emitida_en=emitida_en,
    )
    db.add(row)
    db.flush()
    return row


def ensure_chat(db, *, orden: OrdenServicio) -> Chat:
    row = db.query(Chat).filter(Chat.orden_id == orden.id).first()
    if row:
        return row

    row = Chat(orden_id=orden.id)
    db.add(row)
    db.flush()
    return row


def ensure_mensaje(
    db,
    *,
    chat: Chat,
    remitente: Usuario,
    contenido: str,
    tipo: TipoMensaje,
    leido: bool,
    enviado_en: datetime,
) -> Mensaje:
    row = (
        db.query(Mensaje)
        .filter(Mensaje.chat_id == chat.id, Mensaje.remitente_id == remitente.id, Mensaje.contenido == contenido)
        .first()
    )
    if row:
        return row

    row = Mensaje(
        chat_id=chat.id,
        remitente_id=remitente.id,
        contenido=contenido,
        tipo=tipo,
        leido=leido,
        enviado_en=enviado_en,
    )
    db.add(row)
    db.flush()
    return row


def ensure_notificacion(
    db,
    *,
    usuario: Usuario,
    orden: OrdenServicio | None,
    titulo: str,
    mensaje: str,
    tipo: TipoNotificacion,
    leida: bool,
    creado_en: datetime,
) -> Notificacion:
    row = (
        db.query(Notificacion)
        .filter(Notificacion.usuario_id == usuario.id, Notificacion.titulo == titulo, Notificacion.mensaje == mensaje)
        .first()
    )
    if row:
        return row

    row = Notificacion(
        usuario_id=usuario.id,
        orden_id=orden.id if orden else None,
        titulo=titulo,
        mensaje=mensaje,
        tipo=tipo,
        leida=leida,
        creado_en=creado_en,
    )
    db.add(row)
    db.flush()
    return row


def ensure_dispositivo_push(
    db,
    *,
    usuario: Usuario,
    plataforma: PlataformaPush,
    token_push: str,
    activo: bool,
    registrado_en: datetime,
) -> DispositivoPush:
    row = (
        db.query(DispositivoPush)
        .filter(DispositivoPush.usuario_id == usuario.id, DispositivoPush.token_push == token_push)
        .first()
    )
    if row:
        return row

    row = DispositivoPush(
        usuario_id=usuario.id,
        plataforma=plataforma,
        token_push=token_push,
        activo=activo,
        registrado_en=registrado_en,
    )
    db.add(row)
    db.flush()
    return row


def ensure_calificacion(
    db,
    *,
    orden: OrdenServicio,
    calificador: Usuario,
    calificado: Usuario,
    puntuacion: int,
    comentario: str,
    creado_en: datetime,
) -> Calificacion:
    row = (
        db.query(Calificacion)
        .filter(Calificacion.orden_id == orden.id, Calificacion.calificador_id == calificador.id)
        .first()
    )
    if row:
        return row

    row = Calificacion(
        orden_id=orden.id,
        calificador_id=calificador.id,
        calificado_id=calificado.id,
        tipo_calificador=TipoCalificador.CONDUCTOR,
        puntuacion=puntuacion,
        comentario=comentario,
        creado_en=creado_en,
    )
    db.add(row)
    db.flush()
    return row


def ensure_metrica(
    db,
    *,
    orden: OrdenServicio,
    tiempo_respuesta: int,
    tiempo_llegada: int,
    tiempo_resolucion: int,
    calificacion: str,
    creado_en: datetime,
) -> MetricaServicio:
    row = db.query(MetricaServicio).filter(MetricaServicio.orden_id == orden.id).first()
    if row:
        return row

    row = MetricaServicio(
        orden_id=orden.id,
        tiempo_respuesta_min=tiempo_respuesta,
        tiempo_llegada_min=tiempo_llegada,
        tiempo_resolucion_min=tiempo_resolucion,
        calificacion_final=d(calificacion),
        creado_en=creado_en,
    )
    db.add(row)
    db.flush()
    return row


def seed() -> None:
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    try:
        now = datetime.utcnow()

        admin = ensure_usuario(
            db,
            nombre="Admin",
            apellido="Plataforma",
            email="admin@aci.com",
            telefono="70000001",
            password="Admin123!",
            rol=UserRole.ADMIN,
        )

        conductor_1 = ensure_usuario(
            db,
            nombre="Carlos",
            apellido="Conductor",
            email="conductor@aci.com",
            telefono="70000002",
            password="Conductor123!",
            rol=UserRole.CONDUCTOR,
        )
        conductor_2 = ensure_usuario(
            db,
            nombre="Ana",
            apellido="Rojas",
            email="conductor2@aci.com",
            telefono="70000012",
            password="Conductor123!",
            rol=UserRole.CONDUCTOR,
        )
        conductor_3 = ensure_usuario(
            db,
            nombre="Luis",
            apellido="Perez",
            email="conductor3@aci.com",
            telefono="70000013",
            password="Conductor123!",
            rol=UserRole.CONDUCTOR,
        )

        usuario_taller_1 = ensure_usuario(
            db,
            nombre="Tania",
            apellido="Taller",
            email="taller@aci.com",
            telefono="70000003",
            password="Taller123!",
            rol=UserRole.TALLER,
        )
        usuario_taller_2 = ensure_usuario(
            db,
            nombre="Jorge",
            apellido="Quispe",
            email="taller2@aci.com",
            telefono="70000014",
            password="Taller123!",
            rol=UserRole.TALLER,
        )
        usuario_taller_3 = ensure_usuario(
            db,
            nombre="Laura",
            apellido="Mendez",
            email="taller3@aci.com",
            telefono="70000015",
            password="Taller123!",
            rol=UserRole.TALLER,
        )

        usuario_mecanico_1 = ensure_usuario(
            db,
            nombre="Mario",
            apellido="Mecanico",
            email="mecanico@aci.com",
            telefono="70000004",
            password="Mecanico123!",
            rol=UserRole.MECANICO,
        )
        usuario_mecanico_2 = ensure_usuario(
            db,
            nombre="Pedro",
            apellido="Vargas",
            email="mecanico2@aci.com",
            telefono="70000016",
            password="Mecanico123!",
            rol=UserRole.MECANICO,
        )
        usuario_mecanico_3 = ensure_usuario(
            db,
            nombre="Sofia",
            apellido="Nina",
            email="mecanico3@aci.com",
            telefono="70000017",
            password="Mecanico123!",
            rol=UserRole.MECANICO,
        )
        usuario_mecanico_4 = ensure_usuario(
            db,
            nombre="Diego",
            apellido="Flores",
            email="mecanico4@aci.com",
            telefono="70000018",
            password="Mecanico123!",
            rol=UserRole.MECANICO,
        )
        usuario_mecanico_5 = ensure_usuario(
            db,
            nombre="Elena",
            apellido="Suarez",
            email="mecanico5@aci.com",
            telefono="70000019",
            password="Mecanico123!",
            rol=UserRole.MECANICO,
        )
        usuario_mecanico_6 = ensure_usuario(
            db,
            nombre="Bruno",
            apellido="Rios",
            email="mecanico6@aci.com",
            telefono="70000020",
            password="Mecanico123!",
            rol=UserRole.MECANICO,
        )
        usuario_mecanico_7 = ensure_usuario(
            db,
            nombre="Rosa",
            apellido="Salazar",
            email="mecanico7@aci.com",
            telefono="70000021",
            password="Mecanico123!",
            rol=UserRole.MECANICO,
        )

        usuario_taller_4 = ensure_usuario(
            db,
            nombre="Gabriel",
            apellido="Cruz",
            email="taller4@aci.com",
            telefono="70000022",
            password="Taller123!",
            rol=UserRole.TALLER,
        )

        cat_bateria = ensure_categoria(db, "Bateria", "Problemas de bateria y alternador")
        cat_llanta = ensure_categoria(db, "Llantas", "Pinchazos, cambio y alineacion")
        cat_motor = ensure_categoria(db, "Motor", "Fallas de encendido y motor")
        cat_electrico = ensure_categoria(db, "Electrico", "Sistema electrico y luces")
        cat_grua = ensure_categoria(db, "Grua", "Remolque y traslado")
        cat_frenos = ensure_categoria(db, "Frenos", "Revision y cambio de frenos")

        taller_1 = ensure_taller(
            db,
            usuario=usuario_taller_1,
            nombre="Taller Central ACI",
            descripcion="Taller principal de la red",
            direccion="Av. Principal 123",
            latitud="-16.5000000",
            longitud="-68.1500000",
            radio_cobertura_km="12.00",
            telefono="72000001",
            acepta_domicilio=True,
            calificacion_promedio="4.70",
        )
        taller_2 = ensure_taller(
            db,
            usuario=usuario_taller_2,
            nombre="Taller Norte Express",
            descripcion="Atencion rapida en zona norte",
            direccion="Calle Norte 456",
            latitud="-16.4800000",
            longitud="-68.1300000",
            radio_cobertura_km="9.50",
            telefono="72000002",
            acepta_domicilio=True,
            calificacion_promedio="4.50",
        )
        taller_3 = ensure_taller(
            db,
            usuario=usuario_taller_3,
            nombre="Taller Sur Movil",
            descripcion="Especialistas en servicios a domicilio",
            direccion="Av. Sur 789",
            latitud="-16.5400000",
            longitud="-68.1800000",
            radio_cobertura_km="15.00",
            telefono="72000003",
            acepta_domicilio=True,
            calificacion_promedio="4.80",
        )
        taller_4 = ensure_taller(
            db,
            usuario=usuario_taller_4,
            nombre="Taller Rescate Santa Cruz",
            descripcion="Servicio de grua y rescate en Santa Cruz",
            direccion="Av. Beni 2000",
            latitud="-17.785750",
            longitud="-63.116608",
            radio_cobertura_km="18.00",
            telefono="72000004",
            acepta_domicilio=True,
            calificacion_promedio="4.75",
        )

        mecanico_1 = ensure_mecanico(db, usuario=usuario_mecanico_1, taller=taller_1, especialidad="Motor y bateria", disponible=True)
        mecanico_2 = ensure_mecanico(db, usuario=usuario_mecanico_2, taller=taller_1, especialidad="Frenos y suspension", disponible=True)
        mecanico_3 = ensure_mecanico(db, usuario=usuario_mecanico_3, taller=taller_2, especialidad="Electrico", disponible=True)
        mecanico_4 = ensure_mecanico(db, usuario=usuario_mecanico_4, taller=taller_2, especialidad="Llantas", disponible=False)
        mecanico_5 = ensure_mecanico(db, usuario=usuario_mecanico_5, taller=taller_3, especialidad="Grua y rescate", disponible=True)
        mecanico_6 = ensure_mecanico(db, usuario=usuario_mecanico_6, taller=taller_3, especialidad="Diagnostico general", disponible=True)
        mecanico_7 = ensure_mecanico(db, usuario=usuario_mecanico_7, taller=taller_4, especialidad="Grua y rescate en ruta", disponible=True)

        for dia in [
            DiaSemana.LUNES,
            DiaSemana.MARTES,
            DiaSemana.MIERCOLES,
            DiaSemana.JUEVES,
            DiaSemana.VIERNES,
            DiaSemana.SABADO,
        ]:
            ensure_horario(db, taller=taller_1, dia_semana=dia, hora_apertura=time(8, 0), hora_cierre=time(18, 30), disponible=True)
            ensure_horario(db, taller=taller_2, dia_semana=dia, hora_apertura=time(8, 30), hora_cierre=time(18, 0), disponible=True)
            ensure_horario(db, taller=taller_3, dia_semana=dia, hora_apertura=time(7, 30), hora_cierre=time(19, 0), disponible=True)
            ensure_horario(db, taller=taller_4, dia_semana=dia, hora_apertura=time(8, 0), hora_cierre=time(20, 0), disponible=True)

        ensure_bloqueo(
            db,
            taller=taller_1,
            fecha_inicio=now + timedelta(days=1, hours=3),
            fecha_fin=now + timedelta(days=1, hours=5),
            motivo="Mantenimiento de elevador",
        )
        ensure_bloqueo(
            db,
            taller=taller_2,
            fecha_inicio=now + timedelta(days=2, hours=2),
            fecha_fin=now + timedelta(days=2, hours=4),
            motivo="Capacitacion de personal",
        )

        ensure_servicio(db, taller=taller_1, categoria=cat_bateria, descripcion="Cambio y recarga de bateria", precio_min="80", precio_max="260", tiempo_min=45, servicio_movil=True)
        ensure_servicio(db, taller=taller_1, categoria=cat_motor, descripcion="Diagnostico de motor", precio_min="120", precio_max="450", tiempo_min=90, servicio_movil=True)
        ensure_servicio(db, taller=taller_1, categoria=cat_frenos, descripcion="Revision de frenos", precio_min="90", precio_max="300", tiempo_min=60, servicio_movil=False)
        ensure_servicio(db, taller=taller_2, categoria=cat_llanta, descripcion="Cambio de llanta", precio_min="60", precio_max="200", tiempo_min=35, servicio_movil=True)
        ensure_servicio(db, taller=taller_2, categoria=cat_electrico, descripcion="Sistema electrico", precio_min="110", precio_max="380", tiempo_min=70, servicio_movil=True)
        ensure_servicio(db, taller=taller_2, categoria=cat_bateria, descripcion="Auxilio por bateria", precio_min="75", precio_max="240", tiempo_min=40, servicio_movil=True)
        ensure_servicio(db, taller=taller_3, categoria=cat_grua, descripcion="Servicio de grua", precio_min="150", precio_max="500", tiempo_min=80, servicio_movil=True)
        ensure_servicio(db, taller=taller_3, categoria=cat_llanta, descripcion="Asistencia en carretera", precio_min="70", precio_max="210", tiempo_min=45, servicio_movil=True)
        ensure_servicio(db, taller=taller_3, categoria=cat_motor, descripcion="Encendido de emergencia", precio_min="100", precio_max="320", tiempo_min=55, servicio_movil=True)
        ensure_servicio(db, taller=taller_4, categoria=cat_grua, descripcion="Servicio de grua 24/7", precio_min="160", precio_max="520", tiempo_min=75, servicio_movil=True)
        ensure_servicio(db, taller=taller_4, categoria=cat_motor, descripcion="Diagnostico en ruta", precio_min="110", precio_max="350", tiempo_min=60, servicio_movil=True)

        veh_1 = ensure_vehiculo(db, usuario=conductor_1, marca="Toyota", modelo="Corolla", anio=2018, placa="1234ABC", color="Blanco", combustible=TipoCombustible.GASOLINA)
        veh_2 = ensure_vehiculo(db, usuario=conductor_1, marca="Nissan", modelo="Sentra", anio=2020, placa="5678DEF", color="Gris", combustible=TipoCombustible.GASOLINA)
        veh_3 = ensure_vehiculo(db, usuario=conductor_2, marca="Hyundai", modelo="Accent", anio=2017, placa="9012GHI", color="Azul", combustible=TipoCombustible.GASOLINA)
        veh_4 = ensure_vehiculo(db, usuario=conductor_2, marca="Suzuki", modelo="Vitara", anio=2022, placa="3456JKL", color="Negro", combustible=TipoCombustible.GASOLINA)
        veh_5 = ensure_vehiculo(db, usuario=conductor_3, marca="Kia", modelo="Sportage", anio=2019, placa="7890MNO", color="Rojo", combustible=TipoCombustible.DIESEL)
        veh_6 = ensure_vehiculo(db, usuario=conductor_3, marca="Renault", modelo="Kwid", anio=2023, placa="2468PQR", color="Plata", combustible=TipoCombustible.GASOLINA)

        av_1 = ensure_averia(
            db,
            usuario=conductor_1,
            vehiculo=veh_1,
            descripcion="[SEED] No enciende el vehiculo",
            latitud="-16.5050000",
            longitud="-68.1550000",
            direccion="Zona Sur",
            prioridad=Prioridad.MEDIA,
            estado=EstadoAveria.REGISTRADA,
            creada_hace_horas=20,
        )
        av_2 = ensure_averia(
            db,
            usuario=conductor_1,
            vehiculo=veh_2,
            descripcion="[SEED] Bateria descargada",
            latitud="-16.5060000",
            longitud="-68.1560000",
            direccion="Centro",
            prioridad=Prioridad.ALTA,
            estado=EstadoAveria.ASIGNADA,
            creada_hace_horas=16,
        )
        av_3 = ensure_averia(
            db,
            usuario=conductor_2,
            vehiculo=veh_3,
            descripcion="[SEED] Pinchazo en autopista",
            latitud="-16.5070000",
            longitud="-68.1570000",
            direccion="Norte",
            prioridad=Prioridad.MEDIA,
            estado=EstadoAveria.EN_PROCESO,
            creada_hace_horas=14,
        )
        av_4 = ensure_averia(
            db,
            usuario=conductor_2,
            vehiculo=veh_4,
            descripcion="[SEED] Luces delanteras sin funcionar",
            latitud="-16.4940000",
            longitud="-68.1410000",
            direccion="Miraflores",
            prioridad=Prioridad.BAJA,
            estado=EstadoAveria.ATENDIDA,
            creada_hace_horas=40,
        )
        av_5 = ensure_averia(
            db,
            usuario=conductor_3,
            vehiculo=veh_5,
            descripcion="[SEED] Ruido en frenos",
            latitud="-16.5200000",
            longitud="-68.1700000",
            direccion="Calacoto",
            prioridad=Prioridad.MEDIA,
            estado=EstadoAveria.CANCELADA,
            creada_hace_horas=10,
        )
        av_6 = ensure_averia(
            db,
            usuario=conductor_3,
            vehiculo=veh_6,
            descripcion="[SEED] Calentamiento de motor",
            latitud="-16.5110000",
            longitud="-68.1620000",
            direccion="Obrajes",
            prioridad=Prioridad.CRITICA,
            estado=EstadoAveria.CLASIFICADA,
            creada_hace_horas=6,
        )

        ensure_medio_averia(db, averia=av_1, tipo=MedioTipo.FOTO, url="https://seed.local/averias/av1-foto.jpg")
        ensure_medio_averia(db, averia=av_2, tipo=MedioTipo.AUDIO, url="https://seed.local/averias/av2-audio.mp3")
        ensure_medio_averia(db, averia=av_3, tipo=MedioTipo.VIDEO, url="https://seed.local/averias/av3-video.mp4")

        ensure_diagnostico(
            db,
            averia=av_1,
            categoria=cat_bateria,
            clasificacion=ClasificacionIA.BATERIA,
            urgencia=Prioridad.MEDIA,
            analisis="Se detectan sintomas de falla electrica y descarga de bateria.",
            costo_min="80.00",
            costo_max="220.00",
        )
        ensure_diagnostico(
            db,
            averia=av_6,
            categoria=cat_motor,
            clasificacion=ClasificacionIA.MOTOR,
            urgencia=Prioridad.CRITICA,
            analisis="Patron de sobrecalentamiento con posible falla de refrigeracion.",
            costo_min="150.00",
            costo_max="500.00",
        )

        orden_1 = ensure_orden(
            db,
            averia=av_1,
            taller=taller_1,
            categoria=cat_bateria,
            estado=EstadoOrdenServicio.PENDIENTE_RESPUESTA,
            notas_conductor="[SEED] Orden pendiente de respuesta",
            notas_taller=None,
            motivo_rechazo=None,
            motivo_cancelacion=None,
            tiempo_resp=None,
            tiempo_llegada=None,
            creado_hace_horas=20,
        )
        orden_2 = ensure_orden(
            db,
            averia=av_2,
            taller=taller_1,
            categoria=cat_bateria,
            estado=EstadoOrdenServicio.TECNICO_ASIGNADO,
            notas_conductor="[SEED] Orden con tecnico asignado",
            notas_taller="Asignando tecnico",
            motivo_rechazo=None,
            motivo_cancelacion=None,
            tiempo_resp=18,
            tiempo_llegada=25,
            creado_hace_horas=16,
        )
        orden_3 = ensure_orden(
            db,
            averia=av_3,
            taller=taller_2,
            categoria=cat_llanta,
            estado=EstadoOrdenServicio.EN_PROCESO,
            notas_conductor="[SEED] Orden en proceso",
            notas_taller="Tecnico en sitio",
            motivo_rechazo=None,
            motivo_cancelacion=None,
            tiempo_resp=15,
            tiempo_llegada=20,
            creado_hace_horas=14,
        )
        orden_4 = ensure_orden(
            db,
            averia=av_4,
            taller=taller_2,
            categoria=cat_electrico,
            estado=EstadoOrdenServicio.COMPLETADA,
            notas_conductor="[SEED] Orden completada con pago",
            notas_taller="Trabajo concluido",
            motivo_rechazo=None,
            motivo_cancelacion=None,
            tiempo_resp=12,
            tiempo_llegada=18,
            creado_hace_horas=40,
        )
        orden_5 = ensure_orden(
            db,
            averia=av_5,
            taller=taller_3,
            categoria=cat_frenos,
            estado=EstadoOrdenServicio.CANCELADA,
            notas_conductor="[SEED] Orden cancelada por conductor",
            notas_taller=None,
            motivo_rechazo=None,
            motivo_cancelacion="Conductor resolvio por cuenta propia",
            tiempo_resp=None,
            tiempo_llegada=None,
            creado_hace_horas=10,
        )
        orden_6 = ensure_orden(
            db,
            averia=av_6,
            taller=taller_3,
            categoria=cat_motor,
            estado=EstadoOrdenServicio.RECHAZADA,
            notas_conductor="[SEED] Orden rechazada por taller",
            notas_taller=None,
            motivo_rechazo="No hay capacidad tecnica inmediata",
            motivo_cancelacion=None,
            tiempo_resp=None,
            tiempo_llegada=None,
            creado_hace_horas=6,
        )

        ensure_historial(
            db,
            orden=orden_1,
            estado_anterior=None,
            estado_nuevo=EstadoOrdenServicio.PENDIENTE_RESPUESTA.value,
            usuario_id=conductor_1.id,
            observacion="Creacion de orden",
            creado_en=orden_1.creado_en,
        )
        ensure_historial(
            db,
            orden=orden_2,
            estado_anterior=EstadoOrdenServicio.PENDIENTE_RESPUESTA.value,
            estado_nuevo=EstadoOrdenServicio.TECNICO_ASIGNADO.value,
            usuario_id=usuario_taller_1.id,
            observacion="Orden aceptada y tecnico asignado",
            creado_en=orden_2.creado_en + timedelta(minutes=15),
        )
        ensure_historial(
            db,
            orden=orden_3,
            estado_anterior=EstadoOrdenServicio.ACEPTADA.value,
            estado_nuevo=EstadoOrdenServicio.EN_PROCESO.value,
            usuario_id=usuario_taller_2.id,
            observacion="Tecnico atendiendo en sitio",
            creado_en=orden_3.creado_en + timedelta(minutes=40),
        )
        ensure_historial(
            db,
            orden=orden_4,
            estado_anterior=EstadoOrdenServicio.EN_PROCESO.value,
            estado_nuevo=EstadoOrdenServicio.COMPLETADA.value,
            usuario_id=usuario_taller_2.id,
            observacion="Servicio finalizado",
            creado_en=orden_4.completado_en or (orden_4.creado_en + timedelta(hours=2)),
        )

        asign_2 = ensure_asignacion(
            db,
            orden=orden_2,
            mecanico=mecanico_1,
            asignado_por=usuario_taller_1,
            estado=EstadoAsignacion.EN_CAMINO,
            notas="Tecnico en traslado",
            asignado_en=orden_2.creado_en + timedelta(minutes=18),
        )
        asign_3 = ensure_asignacion(
            db,
            orden=orden_3,
            mecanico=mecanico_3,
            asignado_por=usuario_taller_2,
            estado=EstadoAsignacion.ATENDIENDO,
            notas="Cambio de llanta en curso",
            asignado_en=orden_3.creado_en + timedelta(minutes=20),
        )
        _ = ensure_asignacion(
            db,
            orden=orden_4,
            mecanico=mecanico_4,
            asignado_por=usuario_taller_2,
            estado=EstadoAsignacion.FINALIZADO,
            notas="Reparacion electrica completada",
            asignado_en=orden_4.creado_en + timedelta(minutes=12),
        )

        pres_3_v1 = ensure_presupuesto(
            db,
            orden=orden_3,
            version=1,
            descripcion="Cambio de llanta y calibracion",
            repuestos="120.00",
            mano_obra="40.00",
            estado=EstadoPresupuesto.ENVIADO,
            motivo_rechazo=None,
            enviado_en=orden_3.creado_en + timedelta(minutes=55),
            respondido_en=None,
        )
        pres_4_v1 = ensure_presupuesto(
            db,
            orden=orden_4,
            version=1,
            descripcion="Reparacion sistema electrico delantero",
            repuestos="180.00",
            mano_obra="70.00",
            estado=EstadoPresupuesto.APROBADO,
            motivo_rechazo=None,
            enviado_en=orden_4.creado_en + timedelta(minutes=30),
            respondido_en=orden_4.creado_en + timedelta(minutes=40),
        )
        _ = ensure_presupuesto(
            db,
            orden=orden_6,
            version=1,
            descripcion="Diagnostico preliminar de motor",
            repuestos="0.00",
            mano_obra="35.00",
            estado=EstadoPresupuesto.RECHAZADO,
            motivo_rechazo="No se aprobo por capacidad limitada",
            enviado_en=orden_6.creado_en + timedelta(minutes=20),
            respondido_en=orden_6.creado_en + timedelta(minutes=30),
        )

        pago_4 = ensure_pago(
            db,
            orden=orden_4,
            presupuesto=pres_4_v1,
            monto="250.00",
            metodo=MetodoPago.TARJETA,
            estado=EstadoPago.COMPLETADO,
            referencia="seed_pago_orden4_completado",
            creado_en=orden_4.creado_en + timedelta(hours=1, minutes=10),
            pagado_en=orden_4.creado_en + timedelta(hours=1, minutes=15),
        )
        _ = ensure_pago(
            db,
            orden=orden_3,
            presupuesto=pres_3_v1,
            monto="160.00",
            metodo=MetodoPago.QR,
            estado=EstadoPago.PENDIENTE,
            referencia="seed_pago_orden3_pendiente",
            creado_en=orden_3.creado_en + timedelta(hours=1),
            pagado_en=None,
        )

        _ = ensure_comision(
            db,
            orden=orden_4,
            pago=pago_4,
            base="250.00",
            porcentaje="10.00",
            estado=EstadoComision.PENDIENTE,
            creado_en=orden_4.creado_en + timedelta(hours=1, minutes=20),
        )

        _ = ensure_factura(
            db,
            pago=pago_4,
            orden=orden_4,
            numero="FAC-SEED-0001",
            total="250.00",
            emitida_en=orden_4.creado_en + timedelta(hours=1, minutes=30),
        )

        _ = ensure_calificacion(
            db,
            orden=orden_4,
            calificador=conductor_2,
            calificado=usuario_taller_2,
            puntuacion=5,
            comentario="Muy buena atencion y tiempo de llegada.",
            creado_en=orden_4.creado_en + timedelta(hours=2, minutes=5),
        )

        _ = ensure_metrica(
            db,
            orden=orden_4,
            tiempo_respuesta=12,
            tiempo_llegada=18,
            tiempo_resolucion=95,
            calificacion="5.00",
            creado_en=orden_4.creado_en + timedelta(hours=2, minutes=10),
        )

        chat_3 = ensure_chat(db, orden=orden_3)
        chat_4 = ensure_chat(db, orden=orden_4)

        ensure_mensaje(
            db,
            chat=chat_3,
            remitente=conductor_2,
            contenido="Buenos dias, sigo esperando asistencia.",
            tipo=TipoMensaje.TEXTO,
            leido=True,
            enviado_en=orden_3.creado_en + timedelta(minutes=25),
        )
        ensure_mensaje(
            db,
            chat=chat_3,
            remitente=usuario_taller_2,
            contenido="Tecnico en camino, llega en 20 minutos.",
            tipo=TipoMensaje.TEXTO,
            leido=True,
            enviado_en=orden_3.creado_en + timedelta(minutes=27),
        )
        ensure_mensaje(
            db,
            chat=chat_3,
            remitente=usuario_mecanico_3,
            contenido="Ya estoy en la ubicacion, inicio trabajo.",
            tipo=TipoMensaje.TEXTO,
            leido=False,
            enviado_en=orden_3.creado_en + timedelta(minutes=45),
        )

        ensure_mensaje(
            db,
            chat=chat_4,
            remitente=conductor_2,
            contenido="Gracias por la reparacion.",
            tipo=TipoMensaje.TEXTO,
            leido=True,
            enviado_en=orden_4.creado_en + timedelta(hours=2),
        )
        ensure_mensaje(
            db,
            chat=chat_4,
            remitente=usuario_taller_2,
            contenido="A usted por confiar en nosotros.",
            tipo=TipoMensaje.TEXTO,
            leido=True,
            enviado_en=orden_4.creado_en + timedelta(hours=2, minutes=1),
        )

        ensure_notificacion(
            db,
            usuario=usuario_taller_1,
            orden=orden_1,
            titulo="Nueva orden recibida",
            mensaje="Tienes una orden pendiente de respuesta.",
            tipo=TipoNotificacion.ORDEN_NUEVA,
            leida=False,
            creado_en=orden_1.creado_en,
        )
        ensure_notificacion(
            db,
            usuario=conductor_1,
            orden=orden_2,
            titulo="Tecnico asignado",
            mensaje="Se asigno un tecnico a tu orden.",
            tipo=TipoNotificacion.TECNICO_ASIGNADO,
            leida=False,
            creado_en=asign_2.asignado_en,
        )
        ensure_notificacion(
            db,
            usuario=conductor_2,
            orden=orden_3,
            titulo="Presupuesto enviado",
            mensaje="Tu orden tiene un nuevo presupuesto.",
            tipo=TipoNotificacion.PRESUPUESTO_ENVIADO,
            leida=False,
            creado_en=pres_3_v1.enviado_en,
        )
        ensure_notificacion(
            db,
            usuario=usuario_taller_2,
            orden=orden_4,
            titulo="Pago completado",
            mensaje="Se confirmo el pago de la orden completada.",
            tipo=TipoNotificacion.PAGO_COMPLETADO,
            leida=True,
            creado_en=pago_4.pagado_en or now,
        )
        ensure_notificacion(
            db,
            usuario=usuario_taller_2,
            orden=orden_4,
            titulo="Nueva calificacion",
            mensaje="Recibiste una calificacion de 5 estrellas.",
            tipo=TipoNotificacion.CALIFICACION_RECIBIDA,
            leida=False,
            creado_en=orden_4.creado_en + timedelta(hours=2, minutes=6),
        )

        ensure_dispositivo_push(
            db,
            usuario=conductor_1,
            plataforma=PlataformaPush.ANDROID,
            token_push="seed-push-conductor-1-android",
            activo=True,
            registrado_en=now - timedelta(days=2),
        )
        ensure_dispositivo_push(
            db,
            usuario=conductor_2,
            plataforma=PlataformaPush.WEB,
            token_push="seed-push-conductor-2-web",
            activo=True,
            registrado_en=now - timedelta(days=1),
        )
        ensure_dispositivo_push(
            db,
            usuario=conductor_3,
            plataforma=PlataformaPush.IOS,
            token_push="seed-push-conductor-3-ios",
            activo=False,
            registrado_en=now - timedelta(days=3),
        )

        db.commit()

        print("Seed ampliado aplicado correctamente.")
        print("Credenciales base:")
        print("admin@aci.com / Admin123!")
        print("conductor@aci.com / Conductor123!")
        print("conductor2@aci.com / Conductor123!")
        print("conductor3@aci.com / Conductor123!")
        print("taller@aci.com / Taller123!")
        print("taller2@aci.com / Taller123!")
        print("taller3@aci.com / Taller123!")
        print("taller4@aci.com / Taller123!")
        print("mecanico@aci.com / Mecanico123!")
        print("mecanico2@aci.com / Mecanico123!")
        print("mecanico3@aci.com / Mecanico123!")
        print("mecanico4@aci.com / Mecanico123!")
        print("mecanico5@aci.com / Mecanico123!")
        print("mecanico6@aci.com / Mecanico123!")
        print("mecanico7@aci.com / Mecanico123!")
        print("IDs utiles:")
        print(f"categoria_grua_id={cat_grua.id}")
        print(f"taller_rescate_id={taller_4.id}")
        print(f"mecanico_rescate_id={mecanico_7.id}")
        print(f"orden_en_proceso_id={orden_3.id}")
        print(f"orden_completada_id={orden_4.id}")

    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed()
