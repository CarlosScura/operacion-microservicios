from passlib.context import CryptContext
from datetime import datetime, timedelta, timezone
from jose import jwt
import os

# Creamos la constantes.
SECRET_KEY = os.getenv("JWT_SECRET_KEY")
ALGORITHM = "HS256"
EXPIRACION_MINUTOS = 60

# Creamos el contexto de encriptación para las contraseñas.
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Función para hashear la contraseña
def hashear_password(password: str) -> str:
    '''
    Hashea la contraseña utilizando bcrypt.
    '''
    return pwd_context.hash(password)

# Función para verificar la contraseña
def verificar_password(password_plano: str, password_hash: str) -> bool:
    '''
    Verifica si la contraseña en texto plano coincide con el hash almacenado.
    '''
    return pwd_context.verify(password_plano, password_hash)

# Función para crear un token JWT
def crear_token(usuario_id: int) -> str:
    '''
    Crea un token JWT para el usuario con el ID proporcionado.
    '''
    datos = {"id": usuario_id}
    expiracion = datetime.now(timezone.utc) + timedelta(minutes=EXPIRACION_MINUTOS)
    datos.update({"exp": expiracion})
    token = jwt.encode(datos, SECRET_KEY, algorithm=ALGORITHM)
    return token
