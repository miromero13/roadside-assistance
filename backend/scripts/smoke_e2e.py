from __future__ import annotations

import subprocess
import sys
import time
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import requests

sys.path.append(str(Path(__file__).resolve().parents[1]))

from app.core.database import SessionLocal
from app.models.taller import Mecanico


BASE_URL = "http://127.0.0.1:8001/api"


@dataclass
class Context:
    admin_token: str = ""
    conductor_token: str = ""
    taller_token: str = ""
    mecanico_token: str = ""
    categoria_id: str = ""
    taller_id: str = ""
    mecanico_id: str = ""
    vehiculo_id: str = ""
    averia_id: str = ""
    orden_id: str = ""
    asignacion_id: str = ""
    presupuesto_id: str = ""
    pago_id: str = ""
    pago_monto: float = 0.0


def wait_for_server(url: str, timeout_seconds: int = 20) -> None:
    started = time.time()
    while time.time() - started < timeout_seconds:
        try:
            requests.get(url, timeout=1)
            return
        except Exception:
            time.sleep(0.3)
    raise RuntimeError("No se pudo iniciar el servidor para smoke test")


def request_json(
    method: str,
    path: str,
    token: str | None = None,
    json_payload: dict[str, Any] | None = None,
    expected: tuple[int, ...] = (200, 201),
    params: dict[str, Any] | None = None,
) -> dict[str, Any]:
    headers: dict[str, str] = {}
    if token:
        headers["Authorization"] = f"Bearer {token}"

    response = requests.request(
        method=method,
        url=f"{BASE_URL}{path}",
        headers=headers,
        json=json_payload,
        params=params,
        timeout=20,
    )

    print(f"{method} {path} -> {response.status_code}")
    if response.status_code not in expected:
        print(response.text)
        raise RuntimeError(f"Paso fallido: {method} {path}")

    if not response.text.strip():
        return {}

    return response.json()


def run() -> None:
    ctx = Context()

    ctx.admin_token = request_json(
        "POST",
        "/auth/login",
        json_payload={"email": "admin@aci.com", "password": "Admin123!"},
        expected=(200,),
    )["access_token"]

    ctx.conductor_token = request_json(
        "POST",
        "/auth/login",
        json_payload={"email": "conductor@aci.com", "password": "Conductor123!"},
        expected=(200,),
    )["access_token"]

    ctx.taller_token = request_json(
        "POST",
        "/auth/login",
        json_payload={"email": "taller@aci.com", "password": "Taller123!"},
        expected=(200,),
    )["access_token"]

    ctx.mecanico_token = request_json(
        "POST",
        "/auth/login",
        json_payload={"email": "mecanico@aci.com", "password": "Mecanico123!"},
        expected=(200,),
    )["access_token"]

    vehiculo_payload = {
        "marca": "Kia",
        "modelo": "Rio",
        "anio": 2021,
        "placa": f"Z{str(uuid.uuid4())[:7].upper()}",
        "color": "Rojo",
        "tipo_combustible": "gasolina",
    }
    ctx.vehiculo_id = request_json(
        "POST", "/vehiculos/", token=ctx.conductor_token, json_payload=vehiculo_payload
    )["data"]["id"]

    averia_payload = {
        "vehiculo_id": ctx.vehiculo_id,
        "descripcion_conductor": "No enciende el motor",
        "latitud_averia": -16.505,
        "longitud_averia": -68.155,
        "direccion_averia": "Zona Sur",
        "prioridad": "media",
    }
    ctx.averia_id = request_json(
        "POST", "/averias/", token=ctx.conductor_token, json_payload=averia_payload
    )["data"]["id"]

    categorias = request_json("GET", "/categorias-servicio", token=ctx.admin_token, expected=(200,))["data"]
    ctx.categoria_id = categorias[0]["id"]

    candidatos = request_json(
        "GET",
        "/talleres/candidatos",
        token=ctx.conductor_token,
        params={"averia_id": ctx.averia_id, "categoria_id": ctx.categoria_id},
    )["data"]
    ctx.taller_id = candidatos[0]["id"]

    orden_payload = {
        "averia_id": ctx.averia_id,
        "taller_id": ctx.taller_id,
        "categoria_id": ctx.categoria_id,
        "es_domicilio": True,
        "notas_conductor": "Necesito ayuda urgente",
    }
    ctx.orden_id = request_json(
        "POST", "/ordenes/", token=ctx.conductor_token, json_payload=orden_payload
    )["data"]["id"]

    request_json(
        "PUT",
        f"/ordenes/{ctx.orden_id}/aceptar",
        token=ctx.taller_token,
        json_payload={
            "tiempo_estimado_respuesta_min": 20,
            "tiempo_estimado_llegada_min": 30,
            "notas_taller": "Aceptamos la orden",
        },
    )

    with SessionLocal() as db:
        mecanico = (
            db.query(Mecanico)
            .filter(Mecanico.taller_id == ctx.taller_id)
            .order_by(Mecanico.creado_en.asc())
            .first()
        )
        if not mecanico:
            raise RuntimeError("No hay mecanicos para el taller seleccionado")
        ctx.mecanico_id = str(mecanico.id)

    request_json(
        "PATCH",
        f"/mecanicos/{ctx.mecanico_id}/disponibilidad",
        token=ctx.taller_token,
        json_payload={"disponible": True},
        expected=(200,),
    )

    ctx.asignacion_id = request_json(
        "POST",
        f"/ordenes/{ctx.orden_id}/asignar-mecanico",
        token=ctx.taller_token,
        json_payload={"mecanico_id": ctx.mecanico_id, "notas": "Asignacion inicial"},
    )["data"]["id"]

    request_json(
        "PUT",
        f"/asignaciones/{ctx.asignacion_id}/estado",
        token=ctx.mecanico_token,
        json_payload={"estado": "en_camino", "notas": "Saliendo al lugar"},
    )

    presupuesto_payload = {
        "descripcion_trabajos": "Cambio de bateria y revision general",
        "items_detalle": {
            "items": [
                {"concepto": "Bateria", "cantidad": 1, "precio": 200},
                {"concepto": "Mano de obra", "cantidad": 1, "precio": 50},
            ]
        },
        "monto_repuestos": 200,
        "monto_mano_obra": 50,
    }
    presupuesto = request_json(
        "POST",
        f"/ordenes/{ctx.orden_id}/presupuestos",
        token=ctx.taller_token,
        json_payload=presupuesto_payload,
    )["data"]
    ctx.presupuesto_id = presupuesto["id"]
    ctx.pago_monto = float(presupuesto["monto_total"])

    request_json(
        "PUT",
        f"/presupuestos/{ctx.presupuesto_id}/aprobar",
        token=ctx.conductor_token,
        json_payload={},
    )

    request_json(
        "PUT",
        f"/asignaciones/{ctx.asignacion_id}/estado",
        token=ctx.mecanico_token,
        json_payload={"estado": "atendiendo", "notas": "Iniciando atencion"},
    )

    pago_payload = {
        "orden_id": ctx.orden_id,
        "presupuesto_id": ctx.presupuesto_id,
        "metodo": "tarjeta",
        "monto": ctx.pago_monto,
    }
    ctx.pago_id = request_json(
        "POST", "/pagos/", token=ctx.conductor_token, json_payload=pago_payload
    )["data"]["id"]

    request_json(
        "POST", f"/pagos/{ctx.pago_id}/confirmar", token=ctx.admin_token, json_payload={}
    )

    request_json("GET", f"/ordenes/{ctx.orden_id}", token=ctx.conductor_token)
    request_json("GET", f"/pagos/{ctx.pago_id}", token=ctx.conductor_token)

    request_json("GET", "/pagos/", token=ctx.admin_token)
    request_json("GET", "/comisiones/", token=ctx.admin_token)
    request_json("GET", "/facturas", token=ctx.admin_token)
    request_json("GET", "/metricas/ordenes", token=ctx.admin_token)

    print("Smoke E2E finalizado correctamente")


def main() -> None:
    process = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "main:app", "--port", "8001"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    try:
        wait_for_server("http://127.0.0.1:8001/docs")
        run()
    finally:
        process.terminate()
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()


if __name__ == "__main__":
    main()
