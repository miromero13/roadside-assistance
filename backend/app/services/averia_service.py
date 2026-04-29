from decimal import Decimal
import os
import base64

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.core.database import SessionLocal
from app.models.averia import Averia, DiagnosticoIA, MedioAveria
from app.models.enums import EstadoAveria, MedioTipo
from app.models.usuario import Vehiculo
from app.models.taller import Taller, ServicioTaller
from app.schemas.averia_schema import AveriaCrear, MedioAveriaCrear
from app.services.taller_disponibilidad_service import calcular_distancia_km


def crear_averia(db: Session, payload: AveriaCrear, usuario_id) -> Averia:
    vehiculo = db.execute(
        select(Vehiculo).where(Vehiculo.id == payload.vehiculo_id)
    ).scalars().first()
    if not vehiculo:
        raise ValueError("El vehículo no existe")
    if vehiculo.usuario_id != usuario_id:
        raise PermissionError("No puedes registrar averías sobre un vehículo que no te pertenece")

    averia = Averia(
        usuario_id=usuario_id,
        vehiculo_id=payload.vehiculo_id,
        descripcion_conductor=payload.descripcion_conductor,
        latitud_averia=Decimal(str(payload.latitud_averia)),
        longitud_averia=Decimal(str(payload.longitud_averia)),
        direccion_averia=payload.direccion_averia,
        prioridad=payload.prioridad,
        estado=EstadoAveria.REGISTRADA,
    )
    db.add(averia)
    db.commit()
    db.refresh(averia)
    return averia


def listar_averias_por_usuario(db: Session, usuario_id):
    result = db.execute(
        select(Averia)
        .where(Averia.usuario_id == usuario_id)
        .options(selectinload(Averia.medios))
        .order_by(Averia.creado_en.desc())
    )
    return result.scalars().all()


def listar_averias(db: Session):
    result = db.execute(
        select(Averia).options(selectinload(Averia.medios)).order_by(Averia.creado_en.desc())
    )
    return result.scalars().all()


def obtener_averia(db: Session, averia_id):
    result = db.execute(
        select(Averia)
        .where(Averia.id == averia_id)
        .options(selectinload(Averia.medios))
        .options(selectinload(Averia.diagnostico_ia).selectinload(DiagnosticoIA.categoria))
    )
    return result.scalars().first()


def agregar_medio_averia(
    db: Session,
    averia: Averia,
    payload: MedioAveriaCrear,
) -> MedioAveria:
    medio = MedioAveria(
        averia_id=averia.id,
        tipo=payload.tipo,
        url=payload.url,
        orden_visualizacion=payload.orden_visualizacion,
    )
    db.add(medio)
    db.commit()
    db.refresh(medio)
    return medio


def agregar_medio_averia_con_archivo(
    db: Session,
    averia: Averia,
    tipo: MedioTipo,
    contenido_archivo: bytes,
    orden_visualizacion: int = 1,
    nombre_archivo_original: str | None = None,
) -> MedioAveria:
    """
    Agrega un medio a una avería guardando el archivo binario.

    Args:
        db: Sesión de BD
        averia: Avería a la que se le agregará el medio
        tipo: Tipo de medio (FOTO, AUDIO, VIDEO)
        contenido_archivo: Contenido binario del archivo
        orden_visualizacion: Orden de visualización

    Returns:
        MedioAveria creado
    """

    # Crear directorio si no existe
    media_dir = "media/averias"
    os.makedirs(media_dir, exist_ok=True)

    # Generar nombre de archivo
    extension_map = {
        MedioTipo.FOTO: "jpg",
        MedioTipo.AUDIO: "mp3",
        MedioTipo.VIDEO: "mp4",
    }
    extension = extension_map.get(tipo, "bin")
    if nombre_archivo_original and "." in nombre_archivo_original:
        extension = nombre_archivo_original.rsplit(".", 1)[-1].lower()

    # Contar medios existentes
    medios_count = db.execute(
        select(MedioAveria).where(MedioAveria.averia_id == averia.id)
    ).scalars().all()

    nombre_archivo = f"{averia.id}_{len(medios_count) + 1}.{extension}"
    ruta_archivo = os.path.join(media_dir, nombre_archivo)

    # Guardar archivo
    with open(ruta_archivo, "wb") as f:
        f.write(contenido_archivo)

    # Crear registro en BD con URL local
    url_local = f"/media/averias/{nombre_archivo}"

    medio = MedioAveria(
        averia_id=averia.id,
        tipo=tipo,
        url=url_local,
        orden_visualizacion=orden_visualizacion,
    )
    db.add(medio)
    db.commit()
    db.refresh(medio)
    return medio


def procesar_averia_con_ia(averia_id):
    """
    Procesa una avería con IA: obtiene el diagnóstico.
    No crea orden automáticamente - solo diagnóstico.
    Diseñado para ejecutarse como BackgroundTask.
    """
    db = SessionLocal()
    try:
        from app.services.diagnostico_ia_service import (
            procesar_averia_con_ia as procesar_averia_con_ia_ia,
        )

        diagnostico, _ = procesar_averia_con_ia_ia(db, averia_id, crear_orden=False)
        print(f"Avería {averia_id} procesada con IA. Diagnóstico generado.")

    except Exception as e:
        print(f"Error procesando avería {averia_id} con IA: {e}")
        # No lanzar excepción para no romper el background task
    finally:
        db.close()


def obtener_talleres_disponibles_para_averia(
    db: Session,
    averia_id,
    categoria_id=None,
):
    """
    Obtiene lista de talleres disponibles para una avería.
    Si hay diagnóstico de IA, filtra por categoría detectada.
    Si no, retorna todos los talleres activos cercanos.

    Returns:
        Lista de tuplas (Taller, distancia_km)
    """
    from app.models.averia import DiagnosticoIA

    averia = db.execute(
        select(Averia).where(Averia.id == averia_id)
    ).scalars().first()

    if not averia:
        raise ValueError("Avería no encontrada")

    # Si no especificó categoría, intentar obtener del diagnóstico
    if not categoria_id:
        diagnostico = db.execute(
            select(DiagnosticoIA).where(DiagnosticoIA.averia_id == averia_id)
        ).scalars().first()

        if diagnostico and diagnostico.categoria_id:
            categoria_id = diagnostico.categoria_id

    # Si tiene categoría, buscar servicios para esa categoría
    if categoria_id:
        servicios = db.execute(
            select(ServicioTaller).where(
                ServicioTaller.categoria_id == categoria_id,
                ServicioTaller.activo.is_(True),
            )
        ).scalars().all()

        taller_ids = {s.taller_id for s in servicios}
    else:
        # Sin categoría, obtener todos los talleres activos
        todos_talleres = db.execute(
            select(Taller.id).where(Taller.activo.is_(True))
        ).scalars().all()
        taller_ids = set(todos_talleres)

    # Calcular distancia y filtrar por cobertura
    talleres_con_distancia = []

    for taller_id in taller_ids:
        taller = db.execute(
            select(Taller).where(Taller.id == taller_id, Taller.activo.is_(True))
        ).scalars().first()

        if not taller:
            continue

        distancia = calcular_distancia_km(
            float(averia.latitud_averia),
            float(averia.longitud_averia),
            float(taller.latitud),
            float(taller.longitud),
        )

        # Filtrar por radio de cobertura
        if distancia > float(taller.radio_cobertura_km):
            continue

        talleres_con_distancia.append((taller, distancia))

    # Ordenar por distancia
    talleres_con_distancia.sort(key=lambda x: x[1])

    return talleres_con_distancia
