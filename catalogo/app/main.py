from fastapi import FastAPI, Depends, HTTPException
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

# GET /juegos
@app.get("/juegos", response_model=list[schemas.JuegoResponse])
def listar_juegos(db: Session = Depends(get_db)):
    '''Endpoint para listar todos los juegos en la base de datos.
    '''
    juegos = db.query(models.Juego).all()
    return juegos

# GET /juegos/{id}
@app.get("/juegos/{id}", response_model=schemas.JuegoResponse)
def obtener_juego(id: int, db: Session = Depends(get_db)):
    '''Endpoint para obtener un juego por su ID.
    '''
    juego = db.query(models.Juego).filter(models.Juego.id == id).first()
    if juego is None:
        raise HTTPException(status_code=404, detail='Juego no encontrado')
    return juego

# POST /juegos
@app.post("/juegos", response_model=schemas.JuegoResponse)
def crear_juego(juego: schemas.JuegoBase, db: Session = Depends(get_db), current_user: dict = Depends(auth.get_current_user)):
    '''Endpoint para crear un nuevo juego en la base de datos.
    '''
    nuevo_juego = models.Juego(
        nombre=juego.nombre,
        genero=juego.genero,
        descripcion=juego.descripcion,
        precio=juego.precio
    )
    db.add(nuevo_juego)
    db.commit()
    db.refresh(nuevo_juego)
    return nuevo_juego


# PUT /juegos/{id}
@app.put("/juegos/{id}", response_model=schemas.JuegoResponse)
def actualizar_juego(id: int, actualizado: schemas.JuegoBase, db: Session = Depends(get_db), current_user: dict = Depends(auth.get_current_user)):
    '''Endpoint para actualizar un juego por su ID.
    '''
    juego = db.query(models.Juego).filter(models.Juego.id == id).first()
    if juego is None:
        raise HTTPException(status_code=404, detail='Juego no encontrado')
    
    juego.nombre = actualizado.nombre
    juego.genero = actualizado.genero
    juego.descripcion = actualizado.descripcion
    juego.precio = actualizado.precio
    
    db.commit()
    db.refresh(juego)
    return juego

# DELETE /juegos/{id}
@app.delete("/juegos/{id}")
def eliminar_juego(id: int, db: Session = Depends(get_db), current_user: dict = Depends(auth.get_current_user)):
    '''Endpoint para eliminar un juego por su ID.
    '''
    juego = db.query(models.Juego).filter(models.Juego.id == id).first()
    if juego is None:
        raise HTTPException(status_code=404, detail='Juego no encontrado')
    
    db.delete(juego)
    db.commit()
    return {"mensaje": "El juego fue eliminado exitosamente"}
