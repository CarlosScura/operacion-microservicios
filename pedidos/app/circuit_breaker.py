import pybreaker
import httpx  # para hacer llamadas HTTP entre microservicios
from fastapi import HTTPException

# URLs de los otros microservicios
CATALOGO_URL = "http://catalogo:8000"
INVENTARIO_URL = "http://inventario:8001"
USUARIOS_URL = "http://usuarios:8002"

# Creás un breaker por cada servicio al que llamás — uno por servicio
catalogo_breaker = pybreaker.CircuitBreaker(fail_max=3, reset_timeout=30)
inventario_breaker = pybreaker.CircuitBreaker(fail_max=3, reset_timeout=30)
usuarios_breaker = pybreaker.CircuitBreaker(fail_max=3, reset_timeout=30)

@catalogo_breaker
def obtener_precio_juego(juego_id: int) -> float:
    '''Obtiene el precio de un juego desde Catálogo. 
    Fallback: error controlado.'''
    try:
        response = httpx.get(f"{CATALOGO_URL}/juegos/{juego_id}", timeout=5)
        response.raise_for_status()
        return response.json()["precio"]
    except httpx.TimeoutException:
        raise HTTPException(status_code=503, detail="Catálogo no disponible, reintentá más tarde")
    except httpx.HTTPStatusError:
        raise HTTPException(status_code=503, detail="Error al obtener el precio del juego")



@inventario_breaker
def reservar_stock(pedido_id: int, juego_id: int, cantidad: int) -> dict:
    '''Reserva stock en Inventario para un pedido.
    Fallback: error controlado.'''
    try:
        response = httpx.put(
            f"{INVENTARIO_URL}/reserva",
            json={"pedido_id": pedido_id, "juego_id": juego_id, "cantidad": cantidad},
            timeout=5
        )
        # Si es 409 (stock insuficiente), es un error de negocio, no de conexión
        if response.status_code == 409:
            raise HTTPException(status_code=409, detail="Stock insuficiente para completar el pedido")
        response.raise_for_status()
        return response.json()
    except httpx.TimeoutException:
        raise HTTPException(status_code=503, detail="Inventario no disponible, reintentá más tarde")
    except httpx.HTTPStatusError:
        raise HTTPException(status_code=503, detail="Inventario no disponible, reintentá más tarde")

@inventario_breaker
def cancelar_reserva(pedido_id: int) -> dict:
    '''Cancela una reserva en Inventario.'''
    try:
        response = httpx.put(
            f"{INVENTARIO_URL}/reserva/cancelar",
            json={"pedido_id": pedido_id},
            timeout=5
        )
        response.raise_for_status()
        return response.json()
    except (httpx.TimeoutException, httpx.HTTPStatusError):
        raise HTTPException(status_code=503, detail="Inventario no disponible, reintentá más tarde")


@inventario_breaker
def confirmar_reserva(pedido_id: int) -> dict:
    '''Confirma una reserva en Inventario.'''
    try:
        response = httpx.put(
            f"{INVENTARIO_URL}/reserva/confirmar",
            json={"pedido_id": pedido_id},
            timeout=5
        )
        if response.status_code == 404:
            raise HTTPException(status_code=404, detail="Reserva no encontrada")
        response.raise_for_status()
        return response.json()
    except httpx.TimeoutException:
        raise HTTPException(status_code=503, detail="Inventario no disponible, reintentá más tarde")
    except httpx.HTTPStatusError:
        raise HTTPException(status_code=503, detail="Inventario no disponible, reintentá más tarde")


@usuarios_breaker
def obtener_tarjeta_usuario(usuario_id: int, tarjeta_id: int) -> dict:
    '''Obtiene datos de una tarjeta guardada desde Usuarios.
    Fallback: error controlado, sin cache (dato sensible).'''
    try:
        response = httpx.get(
            f"{USUARIOS_URL}/usuarios/{usuario_id}/tarjetas",
            timeout=5
        )
        response.raise_for_status()
        tarjetas = response.json()
        tarjeta = next((t for t in tarjetas if t["id"] == tarjeta_id), None)
        if not tarjeta:
            raise HTTPException(status_code=404, detail="Tarjeta no encontrada")
        return tarjeta
    except httpx.TimeoutException:
        raise HTTPException(status_code=503, detail="Usuarios no disponible, reintentá más tarde")
    except httpx.HTTPStatusError:
        raise HTTPException(status_code=503, detail="Error al obtener datos de la tarjeta")