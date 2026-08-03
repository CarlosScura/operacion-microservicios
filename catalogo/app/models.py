from sqlalchemy import Column, Integer, String, Float
import database

class Juego(database.Base):
    __tablename__ = 'juegos'

    id = Column(Integer, primary_key=True)
    nombre = Column(String(150), nullable=False)
    genero = Column(String(50), nullable=False)
    descripcion = Column(String(255), nullable=True)
    precio = Column(Float, nullable=False)

