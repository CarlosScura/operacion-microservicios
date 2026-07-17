from pydantic import BaseModel

# GET /usuarios
class UsuarioResponse(BaseModel):
    id: int
    mail: str

# POST /usuarios
class UsuarioCreate(BaseModel):
    mail: str
    password: str

# PUT /usuarios/{id}
class UsuarioUpdate(BaseModel):
    mail: str | None = None
    password: str | None = None

# POST /login
class TokenResponse(BaseModel):
    access_token: str
    token_type: str

# GET /usuarios/{id}/tarjetas
class TarjetaResponse(BaseModel):
    id: int
    usuario_id: int
    nombre: str
    ultimos_4_digitos: str
    marca: str

# POST /usuarios/{id}/tarjetas
class TarjetaCreate(BaseModel):
    nombre: str
    ultimos_4_digitos: str
    marca: str
