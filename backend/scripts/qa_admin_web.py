from __future__ import annotations

import subprocess
import sys
import time
from typing import Any

import requests


BASE_URL = "http://127.0.0.1:8001/api"


def wait_for_server(url: str, timeout_seconds: int = 20) -> None:
    started = time.time()
    while time.time() - started < timeout_seconds:
        try:
            requests.get(url, timeout=1)
            return
        except Exception:
            time.sleep(0.3)
    raise RuntimeError("No se pudo iniciar el servidor para QA admin")


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
        timeout=25,
    )

    print(f"{method} {path} -> {response.status_code}")
    if response.status_code not in expected:
        print(response.text)
        raise RuntimeError(f"Fallo QA admin: {method} {path}")

    if not response.text.strip():
        return {}

    return response.json()


def run() -> None:
    admin_token = request_json(
        "POST",
        "/auth/login",
        json_payload={"email": "admin@aci.com", "password": "Admin123!"},
        expected=(200,),
    )["access_token"]

    usuarios_response = request_json("GET", "/users/", token=admin_token)
    usuarios = usuarios_response.get("data", [])
    if not usuarios:
        raise RuntimeError("No se obtuvieron usuarios para QA admin")

    usuario_target = next((u for u in usuarios if u.get("rol") != "admin"), None)
    if not usuario_target:
        raise RuntimeError("No se encontró usuario no-admin para probar cambio de rol")

    request_json(
        "PATCH",
        f"/users/{usuario_target['id']}/rol",
        token=admin_token,
        json_payload={"rol": usuario_target["rol"]},
        expected=(200,),
    )

    mecanicos_response = request_json("GET", "/operaciones/mecanicos", token=admin_token)
    mecanicos = mecanicos_response.get("data", [])
    if not mecanicos:
        raise RuntimeError("No se obtuvieron mecánicos para QA admin")
    mecanico = mecanicos[0]
    estado_original = bool(mecanico.get("disponible", False))

    request_json(
        "PATCH",
        f"/mecanicos/{mecanico['id']}/disponibilidad",
        token=admin_token,
        json_payload={"disponible": not estado_original},
        expected=(200,),
    )
    request_json(
        "PATCH",
        f"/mecanicos/{mecanico['id']}/disponibilidad",
        token=admin_token,
        json_payload={"disponible": estado_original},
        expected=(200,),
    )

    categorias = request_json("GET", "/categorias-servicio", token=admin_token).get("data", [])
    if not categorias:
        raise RuntimeError("No se obtuvieron categorías para QA admin")
    categoria = categorias[0]
    request_json(
        "PATCH",
        f"/categorias-servicio/{categoria['id']}",
        token=admin_token,
        json_payload={"activo": categoria["activo"]},
        expected=(200,),
    )

    ordenes = request_json("GET", "/ordenes/", token=admin_token).get("data", [])
    if not ordenes:
        raise RuntimeError("No se obtuvieron órdenes para QA admin")
    orden_id = ordenes[0]["id"]

    request_json("GET", f"/ordenes/{orden_id}", token=admin_token)
    request_json("GET", f"/ordenes/{orden_id}/historial-estados", token=admin_token)
    request_json("GET", f"/ordenes/{orden_id}/asignaciones", token=admin_token)

    request_json("GET", "/pagos/", token=admin_token)
    request_json("GET", "/comisiones/", token=admin_token)
    request_json("GET", "/facturas", token=admin_token)

    request_json("GET", "/metricas/ordenes", token=admin_token)
    request_json("POST", f"/metricas/ordenes/{orden_id}/recalcular", token=admin_token)

    print("QA admin web finalizado correctamente")


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
