from typing import List
from pydantic import BaseModel
from models import EstadoPedido

# Cuando se crea un pedido, el cliente debe enviar el usuario y la lista de items.
# El estado se fija en PENDIENTE por defecto en el servicio.
class ItemCreate(BaseModel):
    juego_id: int
    cantidad: int

class PedidoCreate(BaseModel):
    usuario_id: int
    items: List[ItemCreate]

class PedidoUpdate(BaseModel):
    estado: EstadoPedido

# Respuestas incluyen los campos persistidos y los calculados por el servicio.
class ItemResponse(BaseModel):
    id: int
    pedido_id: int
    juego_id: int
    cantidad: int
    precio_unitario: float
    subtotal: float | None = None

class PedidoResponse(BaseModel):
    id: int
    usuario_id: int
    estado: EstadoPedido
    items: List[ItemResponse] = []
    total: float | None = None
