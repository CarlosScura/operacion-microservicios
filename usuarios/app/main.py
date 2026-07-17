from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session

import database
import models
import schemas
import auth

# Iniciamos la aplicación FastAPI
app = FastAPI()

# Dependencia para obtener la sesión de la base de datos
def get_db():
    '''Dependencia para obtener la sesión de la base de datos.'''
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

# GET /usuarios
@app.get("/usuarios", response_model=list[schemas.UsuarioResponse])
def listar_usuarios(db: Session = Depends(get_db)):
    '''
    Endpoint para obtener todos los usuarios.
    '''
    usuarios = db.query(models.Usuario).all()
    return usuarios

# GET /usuarios/{id}
@app.get("/usuarios/{id}", response_model=schemas.UsuarioResponse)
def obtener_usuario(id: int, db: Session = Depends(get_db)):
    '''
    Endpoint para obtener un usuario por su ID.
    '''
    usuario = db.query(models.Usuario).filter(models.Usuario.id == id).first()
    if not usuario:
        raise HTTPException(status_code=404, detail='Usuario no encontrado')
    return usuario

# POST /usuarios
@app.post("/usuarios", response_model=schemas.UsuarioResponse, status_code=status.HTTP_201_CREATED)
def crear_usuario(usuario:schemas.UsuarioCreate, db: Session = Depends(get_db)):
    '''
    Endpoint para crear un nuevo usuario.
    '''
    # Buscamos si ya existe un usuario con ese correo electrónico.
    existente = db.query(models.Usuario).filter(models.Usuario.mail == usuario.mail).first()
    if existente:
        raise HTTPException(status_code=400, detail='El correo electrónico ya está registrado')
    
    # Creamos un nuevo usuario con la contraseña hasheada.
    nuevo_usuario = models.Usuario(
        mail=usuario.mail,
        password_hash=auth.hashear_password(usuario.password)
    )
    # response_model filtra para que solo viaje lo que tiene que viajar, 
    # sin que vaya la contraseña hasheada.
    db.add(nuevo_usuario)
    db.commit()
    db.refresh(nuevo_usuario)
    return nuevo_usuario

# PUT /usuarios/{id}
@app.put("/usuarios/{id}", response_model=schemas.UsuarioResponse)
def actualizar_usuario(id: int, datos: schemas.UsuarioUpdate, db: Session = Depends(get_db)):
    '''
    Endpoint para actualizar de forma parcial/total un usuario.
    '''
    usuario = db.query(models.Usuario).filter(models.Usuario.id == id).first()
    if not usuario:
        raise HTTPException(status_code=404, detail='Usuario no encontrado')
    
    # Actualizamos los campos que vinieron en la solicitud.
    # Si no vinieron, se mantienen los valores existentes.
    if datos.mail is not None:
        usuario.mail = datos.mail
    if datos.password is not None:
        usuario.password_hash = auth.hashear_password(datos.password)
    
    db.commit()
    db.refresh(usuario)
    return usuario

# POST /login
@app.post("/login", response_model=schemas.TokenResponse)
def login(usuario: schemas.UsuarioCreate, db: Session = Depends(get_db)):
    '''
    Endpoint para autenticar a un usuario y generar un token JWT.
    '''
    # Buscamos al usuario por su correo electrónico.
    existente = db.query(models.Usuario).filter(models.Usuario.mail == usuario.mail).first()
    if not existente:
        raise HTTPException(status_code=401, detail='Correo electrónico o contraseña incorrectos')
    
    # Verificamos la contraseña.
    if not auth.verificar_password(usuario.password, existente.password_hash):
        raise HTTPException(status_code=401, detail='Correo electrónico o contraseña incorrectos')
    
    # Creamos el token JWT.
    token = auth.crear_token(existente.id)
    return {"access_token": token, "token_type": "bearer"}

# DELETE /usuarios/{id}
@app.delete("/usuarios/{id}")
def eliminar_usuario(id: int, db: Session = Depends(get_db)):
    '''
    Endpoint para eliminar un usuario por su ID.
    '''
    usuario = db.query(models.Usuario).filter(models.Usuario.id == id).first()
    if not usuario:
        raise HTTPException(status_code=404, detail='Usuario no encontrado')
    
    db.delete(usuario)
    db.commit()
    return {"detail": "Usuario eliminado exitosamente"}

# GET /usuarios/{id}/tarjetas
@app.get("/usuarios/{id}/tarjetas", response_model=list[schemas.TarjetaResponse])
def listar_tarjetas(id: int, db:Session = Depends(get_db)):
    '''
    Endpoint para listar las tarjetas de un cliente.
    '''
    usuario = db.query(models.Usuario).filter(models.Usuario.id == id).first()
    if not usuario:
        raise HTTPException(status_code=404, detail='Usuario no encontrado')
    
    tarjetas = db.query(models.Tarjeta).filter(models.Tarjeta.usuario_id == id).all()

    return tarjetas

# POST /usuarios/{id}/tarjetas
@app.post("/usuarios/{id}/tarjetas", response_model=schemas.TarjetaResponse)
def crear_tarjeta(id: int, datos_tc:schemas.TarjetaCreate, db: Session = Depends(get_db)):
    '''
    Endpoint para crear una nueva tarjeta de un cliente.
    '''
    usuario = db.query(models.Usuario).filter(models.Usuario.id == id).first()
    if not usuario:
        raise HTTPException(status_code=404, detail='Usuario no encontrado')
    
    # Creamos una nueva tarjeta para el usuario.
    nueva_tarjeta = models.Tarjeta(
        usuario_id = id,
        nombre = datos_tc.nombre,
        ultimos_4_digitos = datos_tc.ultimos_4_digitos,
        marca = datos_tc.marca
    )

    db.add(nueva_tarjeta)
    db.commit()
    db.refresh(nueva_tarjeta)
    return nueva_tarjeta

# DELETE /usuarios/{id}/tarjetas/{tarjeta_id}
@app.delete("/usuarios/{id}/tarjetas/{tarjeta_id}")
def eliminar_tarjeta(id: int, tarjeta_id: int, db: Session = Depends(get_db)):
    '''
    Endpoint para eliminar una nueva tarjeta de un cliente.
    '''
    usuario = db.query(models.Usuario).filter(models.Usuario.id == id).first()
    if not usuario:
        raise HTTPException(status_code=404, detail='Usuario no encontrado')
    tarjeta = db.query(models.Tarjeta).filter(
            models.Tarjeta.id == tarjeta_id,
            models.Tarjeta.usuario_id == id
        ).first()
    if not tarjeta:
        raise HTTPException(status_code=404, detail='Tarjeta no encontrada')
    
    db.delete(tarjeta)
    db.commit()
    return {"detail": "Tarjeta eliminada exitosamente"}

