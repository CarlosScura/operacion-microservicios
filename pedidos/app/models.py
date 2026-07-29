import enum
from sqlalchemy import ForeignKey ,Column, Integer, Float, Enum as SQLEnum
import database

class EstadoPedido(str, enum.Enum):
    PENDIENTE = "pendiente"
    PAGADO = "pagado"
    CANCELADO = "cancelado"

class Pedido(database.Base):
    __tablename__ = "pedidos"

    id = Column(Integer, primary_key=True)
    usuario_id = Column(Integer, nullable=False)
    estado = Column(SQLEnum(EstadoPedido), nullable=False)
    
class Item(database.Base):
    __tablename__ = "items"

    id = Column(Integer, primary_key=True, index=True)
    pedido_id = Column(Integer, ForeignKey("pedidos.id"), nullable=False)
    juego_id = Column(Integer, nullable=False)
    cantidad = Column(Integer, nullable=False)
    precio_unitario = Column(Float, nullable=False)
