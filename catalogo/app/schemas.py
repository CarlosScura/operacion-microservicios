from pydantic import BaseModel

class JuegoBase(BaseModel):
    nombre: str
    genero: str
    descripcion: str | None = None
    precio: float

class JuegoResponse(JuegoBase):
    id: int

