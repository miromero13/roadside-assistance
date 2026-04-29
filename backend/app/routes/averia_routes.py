from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session
from uuid import UUID
import os

from app.auth.dependencies import get_current_user, require_conductor
from app.core.database import get_db
from app.models.enums import UserRole, MedioTipo
from app.models.usuario import Usuario
from app.schemas.averia_schema import (
    AveriaCrear,
    AveriaDetalleRead,
    AveriaRead,
    DiagnosticoIARead,
    MedioAveriaCrear,
    MedioAveriaRead,
    ListaTalleresDisponiblesResponse,
    TallerOpcionRead,
)
from app.services.averia_service import (
    agregar_medio_averia,
    agregar_medio_averia_con_archivo,
    crear_averia,
    listar_averias,
    listar_averias_por_usuario,
    obtener_averia,
    obtener_talleres_disponibles_para_averia,
)
from app.services.diagnostico_ia_service import procesar_averia_con_ia
from app.utils.response import response

router = APIRouter(prefix="/averias", tags=["Averías"])


@router.post("/", status_code=status.HTTP_201_CREATED)
async def crear_averia_con_medios_route(
    vehiculo_id: UUID = Form(...),
    descripcion_conductor: str = Form(...),
    latitud_averia: float = Form(...),
    longitud_averia: float = Form(...),
    direccion_averia: str | None = Form(None),
    prioridad: str = Form(default="media"),
    archivos: list[UploadFile] = File(default=[]),
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_conductor),
):
    """
    Crea una avería con medios (fotos, audios, videos) en un solo request.

    Request:
    - multipart/form-data con campos: vehiculo_id, descripcion, latitud, longitud, etc.
    - archivos[] (array de archivos)
    - tipo_media[] (array de tipos: foto|audio|video)
    """
    try:
        from app.models.enums import Prioridad

        # Validar prioridad
        prioridad_enum = Prioridad(prioridad.lower())

        # Crear avería
        payload = AveriaCrear(
            vehiculo_id=vehiculo_id,
            descripcion_conductor=descripcion_conductor,
            latitud_averia=latitud_averia,
            longitud_averia=longitud_averia,
            direccion_averia=direccion_averia,
            prioridad=prioridad_enum,
        )

        averia = crear_averia(db, payload, current_user.id)

        # Agregar medios
        if archivos:
            for idx, archivo in enumerate(archivos):
                try:
                    contenido = archivo.file.read()

                    # Validar tamaño (máximo 50MB)
                    if len(contenido) > 50 * 1024 * 1024:
                        continue  # Saltar este archivo

                    # Detectar tipo de archivo por nombre o usar parámetro
                    tipo_media = MedioTipo.FOTO  # default
                    if "." in archivo.filename:
                        extension = archivo.filename.split(".")[-1].lower()
                        if extension in ["mp3", "wav", "m4a", "flac"]:
                            tipo_media = MedioTipo.AUDIO
                        elif extension in ["mp4", "avi", "mov", "mkv", "webm"]:
                            tipo_media = MedioTipo.VIDEO
                        elif extension in ["jpg", "jpeg", "png", "gif", "webp"]:
                            tipo_media = MedioTipo.FOTO

                    agregar_medio_averia_con_archivo(
                        db, averia, tipo_media, contenido, orden_visualizacion=idx + 1
                    )
                except Exception as e:
                    print(f"Error procesando archivo {archivo.filename}: {e}")
                    continue

        # Procesar diagnóstico en la misma petición para devolver la avería ya clasificada
        procesar_averia_con_ia(db, averia.id, crear_orden=False)

        # Obtener avería actualizada
        averia = obtener_averia(db, averia.id)
        data = AveriaDetalleRead.model_validate(averia).model_dump()
        if averia.diagnostico_ia:
            data["diagnostico_ia"] = DiagnosticoIARead.model_validate(
                averia.diagnostico_ia
            ).model_dump()

        talleres_disponibles = obtener_talleres_disponibles_para_averia(db, averia.id)
        data["talleres_disponibles"] = [
            TallerOpcionRead(
                taller_id=taller.id,
                nombre=taller.nombre,
                distancia_km=round(distancia, 2),
                tiempo_aproximado_min=taller.tiempo_respuesta_promedio_min,
                radio_cobertura_km=float(taller.radio_cobertura_km),
                calificacion_promedio=float(taller.calificacion_promedio),
                acepta_domicilio=taller.acepta_domicilio,
            ).model_dump()
            for taller, distancia in talleres_disponibles
        ]

        return response(
            status_code=201,
            message="Avería creada y diagnosticada exitosamente",
            data=data,
        )

    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Error: {str(exc)}")


@router.get("/")
def listar_averias_route(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    if current_user.rol == UserRole.ADMIN:
        averias = listar_averias(db)
    elif current_user.rol == UserRole.CONDUCTOR:
        averias = listar_averias_por_usuario(db, current_user.id)
    else:
        raise HTTPException(status_code=403, detail="No tienes permisos para listar averías")

    data = [AveriaRead.model_validate(item).model_dump() for item in averias]
    return response(
        status_code=200,
        message="Averías obtenidas exitosamente",
        data=data,
        count_data=len(data),
    )


@router.get("/{averia_id}")
def obtener_averia_route(
    averia_id: UUID,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    averia = obtener_averia(db, averia_id)
    if not averia:
        raise HTTPException(status_code=404, detail="Avería no encontrada")

    if current_user.rol != UserRole.ADMIN and averia.usuario_id != current_user.id:
        raise HTTPException(status_code=403, detail="No tienes permisos para ver esta avería")

    data = AveriaDetalleRead.model_validate(averia).model_dump()
    if averia.diagnostico_ia:
        data["diagnostico_ia"] = DiagnosticoIARead.model_validate(
            averia.diagnostico_ia
        ).model_dump()

    talleres_disponibles = obtener_talleres_disponibles_para_averia(db, averia_id)
    data["talleres_disponibles"] = [
        TallerOpcionRead(
            taller_id=taller.id,
            nombre=taller.nombre,
            distancia_km=round(distancia, 2),
            tiempo_aproximado_min=taller.tiempo_respuesta_promedio_min,
            radio_cobertura_km=float(taller.radio_cobertura_km),
            calificacion_promedio=float(taller.calificacion_promedio),
            acepta_domicilio=taller.acepta_domicilio,
        ).model_dump()
        for taller, distancia in talleres_disponibles
    ]
    return response(status_code=200, message="Avería obtenida exitosamente", data=data)


@router.get("/{averia_id}/talleres-disponibles")
def listar_talleres_disponibles_route(
    averia_id: UUID,
    categoria_id: UUID | None = None,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """
    Lista los talleres disponibles para una avería.
    El conductor elige uno y luego crea la orden usando POST /ordenes/

    Si la avería tiene diagnóstico de IA, filtra por categoría detectada.
    Si no, retorna todos los talleres activos cercanos.
    """
    averia = obtener_averia(db, averia_id)
    if not averia:
        raise HTTPException(status_code=404, detail="Avería no encontrada")

    if current_user.rol != UserRole.ADMIN and averia.usuario_id != current_user.id:
        raise HTTPException(status_code=403, detail="No tienes permisos para ver esta avería")

    try:
        talleres_disponibles = obtener_talleres_disponibles_para_averia(
            db, averia_id, categoria_id
        )

        data = [
            TallerOpcionRead(
                taller_id=taller.id,
                nombre=taller.nombre,
                distancia_km=round(distancia, 2),
                tiempo_aproximado_min=taller.tiempo_respuesta_promedio_min,
                radio_cobertura_km=float(taller.radio_cobertura_km),
                calificacion_promedio=float(taller.calificacion_promedio),
                acepta_domicilio=taller.acepta_domicilio,
            )
            for taller, distancia in talleres_disponibles
        ]

        return response(
            status_code=200,
            message="Talleres disponibles obtenidos exitosamente",
            data=data,
            count_data=len(data),
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{averia_id}/medios", status_code=status.HTTP_201_CREATED)
def agregar_medio_averia_route(
    averia_id: UUID,
    payload: MedioAveriaCrear,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """Endpoint legacy: agregar medio con URL (ya no recomendado)"""
    averia = obtener_averia(db, averia_id)
    if not averia:
        raise HTTPException(status_code=404, detail="Avería no encontrada")

    if current_user.rol != UserRole.ADMIN and averia.usuario_id != current_user.id:
        raise HTTPException(status_code=403, detail="No tienes permisos para modificar esta avería")

    medio = agregar_medio_averia(db, averia, payload)
    data = MedioAveriaRead.model_validate(medio).model_dump()
    return response(status_code=201, message="Medio agregado exitosamente", data=data)
