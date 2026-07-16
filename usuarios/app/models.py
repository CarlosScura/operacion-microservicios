from sqlalchemy import ForeignKey ,Column, Integer, String
import database

class Usuario(database.Base):
    __tablename__ = "usuarios"
    
    id = Column(Integer, primary_key=True)
    mail = Column(String(100), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)

class Tarjeta(database.Base):
    __tablename__ = "tarjetas"
    
    id = Column(Integer, primary_key=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    ultimos_4_digitos = Column(String(4), nullable=False)
    marca = Column(String(20), nullable=False)
