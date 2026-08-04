from passlib.context import CryptContext
from datetime import datetime, timedelta, timezone
from jose import JWTError, jwt
from fastapi import HTTPException, Request, status, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

# Security scheme for OpenAPI / Swagger
bearer_scheme = HTTPBearer(bearerFormat='JWT')

import os

# Creamos las constantes.
SECRET_KEY = os.getenv("JWT_SECRET_KEY")
ALGORITHM = "HS256"
EXPIRACION_MINUTOS = 60

# Creamos el contexto de encriptación para las contraseñas.
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Función para hashear la contraseña
def hashear_password(password: str) -> str:
    '''Hashea la contraseña utilizando bcrypt.'''
    return pwd_context.hash(password)

# Función para verificar la contraseña
def verificar_password(password_plano: str, password_hash: str) -> bool:
    '''Verifica si la contraseña en texto plano coincide con el hash almacenado.'''
    return pwd_context.verify(password_plano, password_hash)

# Función para crear un token JWT
def crear_token(usuario_id: int) -> str:
    '''Crea un token JWT para el usuario con el ID proporcionado.'''
    datos = {"id": usuario_id}
    expiracion = datetime.now(timezone.utc) + timedelta(minutes=EXPIRACION_MINUTOS)
    datos.update({"exp": expiracion})
    token = jwt.encode(datos, SECRET_KEY, algorithm=ALGORITHM)
    return token


def _get_secret_key() -> str:
    '''Obtiene la clave secreta HS256 desde el entorno.'''
    if not SECRET_KEY:
        raise RuntimeError("JWT_SECRET_KEY no está configurada")
    return SECRET_KEY


def verify_token(token: str) -> dict:
    '''Verifica la firma y la validez del token JWT y devuelve las claims del usuario.'''
    try:
        payload = jwt.decode(token, _get_secret_key(), algorithms=[ALGORITHM])
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="El token ha expirado",
            headers={"WWW-Authenticate": "Bearer"}
        )
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido",
            headers={"WWW-Authenticate": "Bearer"}
        )

    if "id" not in payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido: falta la claim de usuario",
            headers={"WWW-Authenticate": "Bearer"}
        )

    try:
        user_id = int(payload["id"])
    except (TypeError, ValueError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido: el ID del usuario no es válido",
            headers={"WWW-Authenticate": "Bearer"}
        )

    return {"id": user_id}


def get_current_user(credentials: HTTPAuthorizationCredentials = Security(bearer_scheme)) -> dict:
    '''Extrae y valida el token desde el esquema HTTP Bearer (para OpenAPI).'''
    token = credentials.credentials if credentials else None
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token vacío",
            headers={"WWW-Authenticate": "Bearer"}
        )
    return verify_token(token)

# Creamos el contexto de encriptación para las contraseñas.
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Función para hashear la contraseña
def hashear_password(password: str) -> str:
    '''Hashea la contraseña utilizando bcrypt.'''
    return pwd_context.hash(password)

# Función para verificar la contraseña
def verificar_password(password_plano: str, password_hash: str) -> bool:
    '''Verifica si la contraseña en texto plano coincide con el hash almacenado.'''
    return pwd_context.verify(password_plano, password_hash)

# Función para crear un token JWT
def crear_token(usuario_id: int) -> str:
    '''Crea un token JWT para el usuario con el ID proporcionado.'''
    datos = {"id": usuario_id}
    expiracion = datetime.now(timezone.utc) + timedelta(minutes=EXPIRACION_MINUTOS)
    datos.update({"exp": expiracion})
    token = jwt.encode(datos, SECRET_KEY, algorithm=ALGORITHM)
    return token


def _get_secret_key() -> str:
    '''Obtiene la clave secreta HS256 desde el entorno.'''
    if not SECRET_KEY:
        raise RuntimeError("JWT_SECRET_KEY no está configurada")
    return SECRET_KEY


def verify_token(token: str) -> dict:
    '''Verifica la firma y la validez del token JWT y devuelve las claims del usuario.'''
    try:
        payload = jwt.decode(token, _get_secret_key(), algorithms=[ALGORITHM])
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="El token ha expirado",
            headers={"WWW-Authenticate": "Bearer"}
        )
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido",
            headers={"WWW-Authenticate": "Bearer"}
        )

    if "id" not in payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido: falta la claim de usuario",
            headers={"WWW-Authenticate": "Bearer"}
        )

    try:
        user_id = int(payload["id"])
    except (TypeError, ValueError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido: el ID del usuario no es válido",
            headers={"WWW-Authenticate": "Bearer"}
        )

    return {"id": user_id}


def get_current_user(credentials: HTTPAuthorizationCredentials = Security(bearer_scheme)) -> dict:
    '''Extrae y valida el token Bearer de la cabecera Authorization.'''
    if not credentials or not credentials.credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Se requiere un token Bearer en la cabecera Authorization",
            headers={"WWW-Authenticate": "Bearer"}
        )
    return verify_token(credentials.credentials)