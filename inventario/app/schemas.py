from pydantic import BaseModel
from models import EstadoReserva

class StockBase(BaseModel):
    juego_id: int
    cantidad: int

class StockResponse(StockBase):
    id: int

class ReservaCrear(BaseModel):
    pedido_id: int
    juego_id: int
    cantidad: int

class ReservaAccion(BaseModel):
    pedido_id: int

class ReservaResponse(BaseModel):
    id: int
    pedido_id: int
    juego_id: int
    cantidad: int
    estado: EstadoReserva