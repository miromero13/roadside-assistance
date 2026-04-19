from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from uuid import UUID

from app.auth.dependencies import get_current_user
from app.core.database import get_db
from app.models.usuario import Usuario
from app.schemas.chat_schema import ChatRead, MensajeCrearRequest, MensajeRead
from app.services.chat_service import (
    contar_mensajes_no_leidos_chat,
    contar_mensajes_chat,
    enviar_mensaje,
    listar_mensajes_chat,
    marcar_chat_como_leido,
    marcar_mensaje_leido,
    obtener_chat,
    obtener_mensaje,
    obtener_o_crear_chat_por_orden,
    obtener_orden,
    validar_acceso_chat,
)
from app.utils.response import response

router = APIRouter(tags=["Chat"])


@router.get("/ordenes/{orden_id}/chat")
def obtener_chat_orden_route(
    orden_id: UUID,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    orden = obtener_orden(db, orden_id)
    if not orden:
        raise HTTPException(status_code=404, detail="Orden no encontrada")

    try:
        chat = obtener_o_crear_chat_por_orden(db, orden, current_user)
    except PermissionError as exc:
        raise HTTPException(status_code=403, detail=str(exc))
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    data = ChatRead.model_validate(chat).model_dump()
    return response(status_code=200, message="Chat obtenido exitosamente", data=data)


@router.get("/chats/{chat_id}/mensajes")
def listar_mensajes_route(
    chat_id: UUID,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, gt=0, le=200),
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    chat = obtener_chat(db, chat_id)
    if not chat:
        raise HTTPException(status_code=404, detail="Chat no encontrado")

    orden = obtener_orden(db, chat.orden_id)
    if not orden:
        raise HTTPException(status_code=404, detail="Orden asociada no encontrada")

    if not validar_acceso_chat(db, orden, current_user):
        raise HTTPException(status_code=403, detail="No tienes permisos para ver este chat")

    mensajes = listar_mensajes_chat(db, chat.id, skip=skip, limit=limit)
    total = contar_mensajes_chat(db, chat.id)
    data = [MensajeRead.model_validate(item).model_dump() for item in mensajes]
    return response(
        status_code=200,
        message="Mensajes obtenidos exitosamente",
        data=data,
        count_data=total,
    )


@router.post("/chats/{chat_id}/mensajes", status_code=status.HTTP_201_CREATED)
def enviar_mensaje_route(
    chat_id: UUID,
    payload: MensajeCrearRequest,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    chat = obtener_chat(db, chat_id)
    if not chat:
        raise HTTPException(status_code=404, detail="Chat no encontrado")

    orden = obtener_orden(db, chat.orden_id)
    if not orden:
        raise HTTPException(status_code=404, detail="Orden asociada no encontrada")

    try:
        mensaje = enviar_mensaje(
            db,
            chat,
            orden,
            current_user,
            payload.contenido,
            payload.tipo,
            payload.media_url,
        )
    except PermissionError as exc:
        raise HTTPException(status_code=403, detail=str(exc))
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    data = MensajeRead.model_validate(mensaje).model_dump()
    return response(status_code=201, message="Mensaje enviado exitosamente", data=data)


@router.put("/chats/{chat_id}/mensajes/{mensaje_id}/leer")
def leer_mensaje_route(
    chat_id: UUID,
    mensaje_id: UUID,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    chat = obtener_chat(db, chat_id)
    if not chat:
        raise HTTPException(status_code=404, detail="Chat no encontrado")

    orden = obtener_orden(db, chat.orden_id)
    if not orden:
        raise HTTPException(status_code=404, detail="Orden asociada no encontrada")

    mensaje = obtener_mensaje(db, mensaje_id, chat.id)
    if not mensaje:
        raise HTTPException(status_code=404, detail="Mensaje no encontrado")

    try:
        mensaje = marcar_mensaje_leido(db, mensaje, current_user, orden)
    except PermissionError as exc:
        raise HTTPException(status_code=403, detail=str(exc))

    data = MensajeRead.model_validate(mensaje).model_dump()
    return response(status_code=200, message="Mensaje marcado como leído", data=data)


@router.put("/chats/{chat_id}/leer-todo")
def leer_chat_completo_route(
    chat_id: UUID,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    chat = obtener_chat(db, chat_id)
    if not chat:
        raise HTTPException(status_code=404, detail="Chat no encontrado")

    orden = obtener_orden(db, chat.orden_id)
    if not orden:
        raise HTTPException(status_code=404, detail="Orden asociada no encontrada")

    try:
        total_marcados = marcar_chat_como_leido(db, chat, current_user, orden)
    except PermissionError as exc:
        raise HTTPException(status_code=403, detail=str(exc))

    return response(
        status_code=200,
        message="Mensajes marcados como leídos",
        data={"total_marcados": total_marcados},
    )


@router.get("/chats/{chat_id}/no-leidos/count")
def contar_no_leidos_chat_route(
    chat_id: UUID,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    chat = obtener_chat(db, chat_id)
    if not chat:
        raise HTTPException(status_code=404, detail="Chat no encontrado")

    orden = obtener_orden(db, chat.orden_id)
    if not orden:
        raise HTTPException(status_code=404, detail="Orden asociada no encontrada")

    if not validar_acceso_chat(db, orden, current_user):
        raise HTTPException(status_code=403, detail="No tienes permisos para ver este chat")

    total_no_leidos = contar_mensajes_no_leidos_chat(db, chat.id, current_user.id)
    return response(
        status_code=200,
        message="Conteo de mensajes no leídos obtenido exitosamente",
        data={"no_leidos": total_no_leidos},
    )
