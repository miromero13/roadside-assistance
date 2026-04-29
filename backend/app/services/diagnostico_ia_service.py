import json
import base64
import httpx
import os
from decimal import Decimal
from typing import Optional
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.averia import Averia, MedioAveria, DiagnosticoIA
from app.models.enums import EstadoAveria, ClasificacionIA, Prioridad
from app.models.taller import CategoriaServicio, ServicioTaller, Taller
from app.models.orden import OrdenServicio
from app.models.enums import EstadoOrdenServicio, TipoNotificacion
from app.services.notificacion_service import notificar_a_taller_por_orden
from app.services.taller_disponibilidad_service import calcular_distancia_km

try:
    import google.genai as genai
except ImportError:
    genai = None


def _inicializar_gemini():
    """Inicializa el cliente de Gemini con la API key"""
    if not genai or not settings.gemini_api_key:
        raise ValueError("Gemini API key not configured")


def obtener_categorias_para_prompt(db: Session) -> str:
    """Obtiene las categorías de servicio activas y las formatea para el prompt"""
    categorias = db.execute(
        select(CategoriaServicio).where(CategoriaServicio.activo.is_(True))
    ).scalars().all()

    if not categorias:
        return ""

    formato = "\n".join([f"- {cat.nombre}: {cat.descripcion or ''}" for cat in categorias])
    return formato


def descargar_media_como_base64(url: str, tipo_media: str) -> str:
    """
    Descarga un archivo desde una URL y lo convierte a base64

    Args:
        url: URL del archivo
        tipo_media: tipo de media (foto, audio, video)

    Returns:
        String en base64
    """
    try:
        if url.startswith("/media/"):
          ruta_local = url.lstrip("/")
          if os.path.exists(ruta_local):
              with open(ruta_local, "rb") as archivo:
                  return base64.standard_b64encode(archivo.read()).decode("utf-8")

        with httpx.Client() as client:
            response = client.get(url, timeout=30.0)
            response.raise_for_status()
            return base64.standard_b64encode(response.content).decode('utf-8')
    except Exception as e:
        print(f"Error descargando media {url}: {e}")
        return None


def construir_prompt_para_gemini(
    averia: Averia,
    medios: list[MedioAveria],
    categorias_str: str,
) -> str:
    """Construye el prompt para enviar a Gemini"""

    medios_info = []
    medios_base64 = []

    for i, medio in enumerate(medios, 1):
        tipo_display = "foto" if medio.tipo.value == "foto" else "audio" if medio.tipo.value == "audio" else "video"
        medios_info.append(f"{i}. {tipo_display.upper()}")

        # Descargar y convertir a base64
        b64 = descargar_media_como_base64(medio.url, medio.tipo.value)
        if b64:
            medios_base64.append({
                "tipo": medio.tipo.value,
                "data": b64[:2000]  # Limitar tamaño para prompt
            })

    medios_info_str = "\n".join(medios_info) if medios_info else "No hay medios adjuntos"

    prioridad_texto = {
        "baja": "BAJA",
        "media": "MEDIA",
        "alta": "ALTA",
        "critica": "CRÍTICA"
    }.get(averia.prioridad.value, averia.prioridad.value.upper())

    prompt = f"""Eres un experto en diagnóstico de problemas vehiculares. Tu tarea es analizar los medios adjuntos (fotos, videos, audios) junto con la descripción del conductor para determinar qué está mal en el vehículo.

CATEGORÍAS DISPONIBLES:
{categorias_str}

INFORMACIÓN DE LA AVERÍA:
- Descripción del conductor: {averia.descripcion_conductor}
- Ubicación: {averia.direccion_averia or f"Latitud: {averia.latitud_averia}, Longitud: {averia.longitud_averia}"}
- Prioridad reportada: {prioridad_texto}
- Medios adjuntos: {medios_info_str}
- Cantidad de archivos: {len(medios)}

MEDIOS PARA ANALIZAR:
{json.dumps([{"tipo": m["tipo"]} for m in medios_base64], ensure_ascii=False)}

Tu análisis debe ser profundo y fundamentado. Proporciona tu respuesta en el siguiente formato JSON válido (solo JSON, sin markdown):

{{
  "categoria": "nombre_de_categoria_o_incierto",
  "confianza_categoria": 0.95,
  "diagnostico": "Análisis detallado de lo que observas en el vehículo basándote en la descripción y medios...",
  "notas_taller": "Recomendaciones específicas y precisas para que el taller sepa exactamente qué revisar y hacer",
  "urgencia": "baja|media|alta|critica",
  "danos_visibles": "Descripción de daños visibles identificados en fotos/videos",
  "costo_estimado_min": 10000,
  "costo_estimado_max": 100000,
  "requiere_revision_manual": true,
  "resumen_automatico": "Resumen de máximo 2 líneas del problema"
}}

IMPORTANTE:
- El JSON debe ser válido y parseble
- Las notas_taller serán mostradas al taller, sé específico
- Los costos son en moneda local (ajusta según contexto)
- Confianza debe ser decimal entre 0 y 1
- Si no puedes categorizar con confianza, usa "incierto"
"""

    return prompt


def llamar_gemini_para_diagnostico(prompt: str) -> Optional[dict]:
    """
    Llama a la API de Gemini para obtener el diagnóstico

    Returns:
        Dict con la respuesta parseada o None si hay error
    """
    try:
        _inicializar_gemini()
        client = genai.Client(api_key=settings.gemini_api_key)
        response = client.models.generate_content(
            model=settings.gemini_model,
            contents=prompt,
        )

        if not response.text:
            return None

        # Intentar parsear como JSON
        texto = response.text.strip()

        # Si contiene markdown code blocks, extraer el JSON
        if "```json" in texto:
            texto = texto.split("```json")[1].split("```")[0].strip()
        elif "```" in texto:
            texto = texto.split("```")[1].split("```")[0].strip()

        resultado = json.loads(texto)
        return resultado
    except json.JSONDecodeError as e:
        print(f"Error parseando respuesta JSON de Gemini: {e}")
        return None
    except Exception as e:
        print(f"Error llamando a Gemini: {e}")
        return None


def mapear_categoria_desde_nombre(db: Session, nombre_categoria: str) -> Optional[CategoriaServicio]:
    """Mapea el nombre de categoría retornado por IA a un CategoriaServicio existente"""

    # Buscar coincidencia exacta primero
    categoria = db.execute(
        select(CategoriaServicio)
        .where(CategoriaServicio.nombre.ilike(nombre_categoria))
        .where(CategoriaServicio.activo.is_(True))
    ).scalars().first()

    if categoria:
        return categoria

    # Si no encuentra, buscar la más similar o retornar None
    todas = db.execute(
        select(CategoriaServicio).where(CategoriaServicio.activo.is_(True))
    ).scalars().all()

    # Buscar palabra clave
    nombre_lower = nombre_categoria.lower()
    for cat in todas:
        if nombre_lower in cat.nombre.lower() or cat.nombre.lower() in nombre_lower:
            return cat

    return None


def crear_diagnostico_ia(
    db: Session,
    averia: Averia,
    respuesta_gemini: dict,
) -> DiagnosticoIA:
    """Crea un registro de DiagnosticoIA en la base de datos"""

    # Mapear categoría
    categoria = None
    nombre_categoria_ia = respuesta_gemini.get("categoria", "incierto")
    if nombre_categoria_ia.lower() != "incierto":
        categoria = mapear_categoria_desde_nombre(db, nombre_categoria_ia)

    # Mapear urgencia
    urgencia_str = respuesta_gemini.get("urgencia", "media").lower()
    urgencia_enum = Prioridad.MEDIA
    if urgencia_str in ["baja", "media", "alta", "critica"]:
        urgencia_enum = Prioridad(urgencia_str)

    # Mapear clasificación
    clasificacion_enum = ClasificacionIA.INCIERTO
    try:
        if nombre_categoria_ia.lower() in [e.value for e in ClasificacionIA]:
            clasificacion_enum = ClasificacionIA(nombre_categoria_ia.lower())
    except (ValueError, AttributeError):
        pass

    # Costos
    costo_min = respuesta_gemini.get("costo_estimado_min")
    costo_max = respuesta_gemini.get("costo_estimado_max")

    diagnostico = DiagnosticoIA(
        averia_id=averia.id,
        categoria_id=categoria.id if categoria else None,
        clasificacion=clasificacion_enum,
        urgencia=urgencia_enum,
        nivel_confianza=Decimal(str(respuesta_gemini.get("confianza_categoria", 0))),
        transcripcion_audio=None,  # No implementado aún
        analisis=respuesta_gemini.get("diagnostico", ""),
        resumen_automatico=respuesta_gemini.get("resumen_automatico", ""),
        recomendacion=respuesta_gemini.get("notas_taller", ""),
        danos_visibles=respuesta_gemini.get("danos_visibles", ""),
        costo_estimado_min=Decimal(str(costo_min)) if costo_min else None,
        costo_estimado_max=Decimal(str(costo_max)) if costo_max else None,
        requiere_revision_manual=respuesta_gemini.get("requiere_revision_manual", False),
        historial_conversacion=respuesta_gemini,
    )

    db.add(diagnostico)
    db.flush()
    return diagnostico


def crear_orden_automatica_desde_diagnostico(
    db: Session,
    averia: Averia,
    diagnostico_ia: DiagnosticoIA,
) -> Optional[OrdenServicio]:
    """
    Crea una orden automáticamente basada en el diagnóstico de IA
    Similar a _crear_orden_automatica_tras_rechazo en orden_service.py
    """

    if not diagnostico_ia.categoria_id:
        print(f"No hay categoría para la avería {averia.id}")
        return None

    # Buscar servicios disponibles para esta categoría
    servicios = db.execute(
        select(ServicioTaller).where(
            ServicioTaller.categoria_id == diagnostico_ia.categoria_id,
            ServicioTaller.activo.is_(True),
        )
    ).scalars().all()

    if not servicios:
        print(f"No hay talleres que ofrezcan la categoría {diagnostico_ia.categoria_id}")
        return None

    # Encontrar el taller más cercano y disponible
    mejor_taller: Optional[Taller] = None
    mejor_distancia: Optional[float] = None

    for servicio in servicios:
        taller = db.execute(
            select(Taller).where(Taller.id == servicio.taller_id, Taller.activo.is_(True))
        ).scalars().first()

        if not taller:
            continue

        distancia = calcular_distancia_km(
            float(averia.latitud_averia),
            float(averia.longitud_averia),
            float(taller.latitud),
            float(taller.longitud),
        )

        if distancia > float(taller.radio_cobertura_km):
            continue

        if mejor_distancia is None or distancia < mejor_distancia:
            mejor_taller = taller
            mejor_distancia = distancia

    if not mejor_taller:
        print(f"No hay talleres disponibles en cobertura para avería {averia.id}")
        return None

    # Crear la orden
    orden = OrdenServicio(
        averia_id=averia.id,
        taller_id=mejor_taller.id,
        categoria_id=diagnostico_ia.categoria_id,
        estado=EstadoOrdenServicio.PENDIENTE_RESPUESTA,
        es_domicilio=False,
        notas_taller=diagnostico_ia.recomendacion or diagnostico_ia.analisis,
    )

    db.add(orden)
    db.flush()

    # Notificar al taller
    try:
        notificar_a_taller_por_orden(
            db,
            orden,
            TipoNotificacion.ORDEN_NUEVA,
            "Nueva orden de asistencia",
            f"Se creó automáticamente una orden basada en diagnóstico de IA: {diagnostico_ia.resumen_automatico or 'Revisión necesaria'}",
        )
    except Exception as e:
        print(f"Error notificando taller: {e}")

    db.commit()
    db.refresh(orden)
    return orden


def procesar_averia_con_ia(
    db: Session,
    averia_id,
    crear_orden: bool = False,
) -> tuple[Optional[DiagnosticoIA], Optional[OrdenServicio]]:
    """
    Procesa una avería con IA: obtiene el diagnóstico y opcionalmente crea orden

    Args:
        db: Sesión de BD
        averia_id: ID de la avería
        crear_orden: Si True, crea orden automáticamente. Si False, solo genera diagnóstico

    Returns:
        Tupla (DiagnosticoIA, OrdenServicio o None)
    """

    # Obtener la avería con sus medios
    averia = db.execute(
        select(Averia).where(Averia.id == averia_id)
    ).scalars().first()

    if not averia:
        raise ValueError(f"Avería {averia_id} no encontrada")

    # Cambiar estado a ANALIZANDO
    averia.estado = EstadoAveria.ANALIZANDO
    db.commit()

    try:
        # Obtener medios
        medios = db.execute(
            select(MedioAveria)
            .where(MedioAveria.averia_id == averia_id)
            .order_by(MedioAveria.orden_visualizacion)
        ).scalars().all()

        # Construir prompt
        categorias_str = obtener_categorias_para_prompt(db)
        prompt = construir_prompt_para_gemini(averia, medios, categorias_str)

        # Llamar a Gemini
        respuesta = llamar_gemini_para_diagnostico(prompt)

        if not respuesta:
            raise ValueError("No se pudo obtener respuesta de Gemini")

        # Crear diagnóstico
        diagnostico = crear_diagnostico_ia(db, averia, respuesta)

        # Cambiar estado a CLASIFICADA
        averia.estado = EstadoAveria.CLASIFICADA
        db.commit()

        # Crear orden automática si se solicita
        orden = None
        if crear_orden:
            orden = crear_orden_automatica_desde_diagnostico(db, averia, diagnostico)

        return diagnostico, orden

    except Exception as e:
        print(f"Error procesando avería con IA: {e}")
        # Mantener en ANALIZANDO para que se reintente después
        db.rollback()
        raise



def mapear_categoria_desde_nombre(db: Session, nombre_categoria: str) -> Optional[CategoriaServicio]:
    """Mapea el nombre de categoría retornado por IA a un CategoriaServicio existente"""

    # Buscar coincidencia exacta primero
    categoria = db.execute(
        select(CategoriaServicio)
        .where(CategoriaServicio.nombre.ilike(nombre_categoria))
        .where(CategoriaServicio.activo.is_(True))
    ).scalars().first()

    if categoria:
        return categoria

    # Si no encuentra, buscar la más similar o retornar None
    todas = db.execute(
        select(CategoriaServicio).where(CategoriaServicio.activo.is_(True))
    ).scalars().all()

    # Buscar palabra clave
    nombre_lower = nombre_categoria.lower()
    for cat in todas:
        if nombre_lower in cat.nombre.lower() or cat.nombre.lower() in nombre_lower:
            return cat

    return None


def crear_diagnostico_ia(
    db: Session,
    averia: Averia,
    respuesta_gemini: dict,
) -> DiagnosticoIA:
    """Crea un registro de DiagnosticoIA en la base de datos"""

    # Mapear categoría
    categoria = None
    nombre_categoria_ia = respuesta_gemini.get("categoria", "incierto")
    if nombre_categoria_ia.lower() != "incierto":
        categoria = mapear_categoria_desde_nombre(db, nombre_categoria_ia)

    # Mapear urgencia
    urgencia_str = respuesta_gemini.get("urgencia", "media").lower()
    urgencia_enum = Prioridad.MEDIA
    if urgencia_str in ["baja", "media", "alta", "critica"]:
        urgencia_enum = Prioridad(urgencia_str)

    # Mapear clasificación
    clasificacion_enum = ClasificacionIA.INCIERTO
    try:
        if nombre_categoria_ia.lower() in [e.value for e in ClasificacionIA]:
            clasificacion_enum = ClasificacionIA(nombre_categoria_ia.lower())
    except (ValueError, AttributeError):
        pass

    # Costos
    costo_min = respuesta_gemini.get("costo_estimado_min")
    costo_max = respuesta_gemini.get("costo_estimado_max")

    diagnostico = DiagnosticoIA(
        averia_id=averia.id,
        categoria_id=categoria.id if categoria else None,
        clasificacion=clasificacion_enum,
        urgencia=urgencia_enum,
        nivel_confianza=Decimal(str(respuesta_gemini.get("confianza_categoria", 0))),
        transcripcion_audio=None,  # No implementado aún
        analisis=respuesta_gemini.get("diagnostico", ""),
        resumen_automatico=respuesta_gemini.get("resumen_automatico", ""),
        recomendacion=respuesta_gemini.get("notas_taller", ""),
        danos_visibles=respuesta_gemini.get("danos_visibles", ""),
        costo_estimado_min=Decimal(str(costo_min)) if costo_min else None,
        costo_estimado_max=Decimal(str(costo_max)) if costo_max else None,
        requiere_revision_manual=respuesta_gemini.get("requiere_revision_manual", False),
        historial_conversacion=respuesta_gemini,
    )

    db.add(diagnostico)
    db.flush()
    return diagnostico


def crear_orden_automatica_desde_diagnostico(
    db: Session,
    averia: Averia,
    diagnostico_ia: DiagnosticoIA,
) -> Optional[OrdenServicio]:
    """
    Crea una orden automáticamente basada en el diagnóstico de IA
    Similar a _crear_orden_automatica_tras_rechazo en orden_service.py
    """

    if not diagnostico_ia.categoria_id:
        print(f"No hay categoría para la avería {averia.id}")
        return None

    # Buscar servicios disponibles para esta categoría
    servicios = db.execute(
        select(ServicioTaller).where(
            ServicioTaller.categoria_id == diagnostico_ia.categoria_id,
            ServicioTaller.activo.is_(True),
        )
    ).scalars().all()

    if not servicios:
        print(f"No hay talleres que ofrezcan la categoría {diagnostico_ia.categoria_id}")
        return None

    # Encontrar el taller más cercano y disponible
    mejor_taller: Optional[Taller] = None
    mejor_distancia: Optional[float] = None

    for servicio in servicios:
        taller = db.execute(
            select(Taller).where(Taller.id == servicio.taller_id, Taller.activo.is_(True))
        ).scalars().first()

        if not taller:
            continue

        distancia = calcular_distancia_km(
            float(averia.latitud_averia),
            float(averia.longitud_averia),
            float(taller.latitud),
            float(taller.longitud),
        )

        if distancia > float(taller.radio_cobertura_km):
            continue

        if mejor_distancia is None or distancia < mejor_distancia:
            mejor_taller = taller
            mejor_distancia = distancia

    if not mejor_taller:
        print(f"No hay talleres disponibles en cobertura para avería {averia.id}")
        return None

    # Crear la orden
    orden = OrdenServicio(
        averia_id=averia.id,
        taller_id=mejor_taller.id,
        categoria_id=diagnostico_ia.categoria_id,
        estado=EstadoOrdenServicio.PENDIENTE_RESPUESTA,
        es_domicilio=False,
        notas_taller=diagnostico_ia.recomendacion or diagnostico_ia.analisis,
    )

    db.add(orden)
    db.flush()

    # Notificar al taller
    try:
        notificar_a_taller_por_orden(
            db,
            orden,
            TipoNotificacion.ORDEN_NUEVA,
            "Nueva orden de asistencia",
            f"Se creó automáticamente una orden basada en diagnóstico de IA: {diagnostico_ia.resumen_automatico or 'Revisión necesaria'}",
        )
    except Exception as e:
        print(f"Error notificando taller: {e}")

    db.commit()
    db.refresh(orden)
    return orden


def procesar_averia_con_ia(
    db: Session,
    averia_id,
    crear_orden: bool = False,
) -> tuple[Optional[DiagnosticoIA], Optional[OrdenServicio]]:
    """
    Procesa una avería con IA: obtiene el diagnóstico y opcionalmente crea orden

    Args:
        db: Sesión de BD
        averia_id: ID de la avería
        crear_orden: Si True, crea orden automáticamente. Si False, solo genera diagnóstico

    Returns:
        Tupla (DiagnosticoIA, OrdenServicio o None)
    """

    # Obtener la avería con sus medios
    averia = db.execute(
        select(Averia).where(Averia.id == averia_id)
    ).scalars().first()

    if not averia:
        raise ValueError(f"Avería {averia_id} no encontrada")

    # Cambiar estado a ANALIZANDO
    averia.estado = EstadoAveria.ANALIZANDO
    db.commit()

    try:
        # Obtener medios
        medios = db.execute(
            select(MedioAveria)
            .where(MedioAveria.averia_id == averia_id)
            .order_by(MedioAveria.orden_visualizacion)
        ).scalars().all()

        # Construir prompt
        categorias_str = obtener_categorias_para_prompt(db)
        prompt = construir_prompt_para_gemini(averia, medios, categorias_str)

        # Llamar a Gemini
        respuesta = llamar_gemini_para_diagnostico(prompt)

        if not respuesta:
            raise ValueError("No se pudo obtener respuesta de Gemini")

        # Crear diagnóstico
        diagnostico = crear_diagnostico_ia(db, averia, respuesta)

        # Cambiar estado a CLASIFICADA
        averia.estado = EstadoAveria.CLASIFICADA
        db.commit()

        # Crear orden automática si se solicita
        orden = None
        if crear_orden:
            orden = crear_orden_automatica_desde_diagnostico(db, averia, diagnostico)

        return diagnostico, orden

    except Exception as e:
        print(f"Error procesando avería con IA: {e}")
        # Mantener en ANALIZANDO para que se reintente después
        db.rollback()
        raise
