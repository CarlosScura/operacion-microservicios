import enum
from sqlalchemy import ForeignKey ,Column, Integer, Enum as SQLEnum
import database

class EstadoReserva(str, enum.Enum):
    RESERVADA = "reservada"
    CONFIRMADA = "confirmada"
    CANCELADA = "cancelada"

class Stock(database.Base):
    __tablename__ = "stock"

    id = Column(Integer, primary_key=True)
    juego_id = Column(Integer, nullable=False, unique=True)
    cantidad = Column(Integer, nullable=False)
    
class Reserva(database.Base):
    __tablename__ = "reserva"

    id = Column(Integer, primary_key=True, index=True)
    pedido_id = Column(Integer, nullable=False, unique=True)
    juego_id = Column(Integer, ForeignKey("stock.juego_id"), nullable=False)
    cantidad = Column(Integer, nullable=False)
    estado = Column(SQLEnum(EstadoReserva, values_callable=lambda x: [e.value for e in x]), nullable=False, default=EstadoReserva.RESERVADA)
