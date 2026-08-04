from fastapi import HTTPException, Request, status, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

# Security scheme for OpenAPI / Swagger
bearer_scheme = HTTPBearer(bearerFormat='JWT')
from jose import JWTError, jwt
import os


SECRET_KEY = os.getenv("JWT_SECRET_KEY")
ALGORITHM = "HS256"


def _get_secret_key() -> str:
    '''Obtiene la clave secreta HS256 desde el entorno.'''
    if not SECRET_KEY:
        raise RuntimeError("JWT_SECRET_KEY no está configurada")
    return SECRET_KEY


def verify_token(token: str) -> dict:
    '''Verifica la firma y validez del token JWT y devuelve las claims del usuario.'''
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