from fastapi import FastAPI, Depends, HTTPException, Response, status
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

# GET /stock
@app.get("/stock", response_model=list[schemas.StockResponse])
def listar_stock(db: Session = Depends(get_db), current_user: dict = Depends(auth.get_current_user)):
    '''Endpoint para listar el stock de todos los juegos en la base de datos.
    '''
    stock = db.query(models.Stock).all()
    return stock

# GET /stock/{id}
@app.get("/stock/{id}", response_model=schemas.StockResponse)
def obtener_stock(id: int, db: Session = Depends(get_db), current_user: dict = Depends(auth.get_current_user)):
    '''Endpoint para obtener un stock de un juego por su ID.
    '''
    stock = db.query(models.Stock).filter(models.Stock.id == id).first()
    if stock is None:
        raise HTTPException(status_code=404, detail='Juego no encontrado')
    return stock

# PUT /stock
@app.put("/stock", response_model=schemas.StockResponse)
def actualizar_stock(stock: schemas.StockBase, db: Session = Depends(get_db), current_user: dict = Depends(auth.get_current_user)):
    '''Endpoint para actualizar el stock de un juego.
    '''
    stock_db = db.query(models.Stock).filter(models.Stock.juego_id == stock.juego_id).first()
    if stock_db is None:
        # Si no existe, creamos un nuevo registro de stock
        nuevo_stock = models.Stock(juego_id=stock.juego_id, cantidad=stock.cantidad)
        db.add(nuevo_stock)
        db.commit()
        db.refresh(nuevo_stock)
        return nuevo_stock
    else:
        # Si existe, actualizamos la cantidad
        stock_db.cantidad += stock.cantidad
        db.commit()
        db.refresh(stock_db)
        return stock_db

# PUT /reserva
@app.put("/reserva", response_model=schemas.ReservaResponse)
def reservar_stock(reserva: schemas.ReservaCrear, response: Response , db: Session = Depends(get_db)):
    '''Endpoint para crear una reserva de juegos.
    '''
    # Buscamos si ya existe una reserva con ese pedido_id
    existente = db.query(models.Reserva).filter(models.Reserva.pedido_id == reserva.pedido_id).first()
    if existente:
        response.status_code = status.HTTP_200_OK
        return existente

    # Verificamos stock disponible
    stock = db.query(models.Stock).filter(models.Stock.juego_id == reserva.juego_id).first()
    if stock is None or stock.cantidad < reserva.cantidad:
        raise HTTPException(status_code=409, detail='Stock insuficiente')

    # Descontamos el stock y creamos la reserva.
    stock.cantidad -= reserva.cantidad
    nueva_reserva = models.Reserva(
        pedido_id=reserva.pedido_id,
        juego_id=reserva.juego_id,
        cantidad=reserva.cantidad,
        estado=models.EstadoReserva.RESERVADA
    )
    db.add(nueva_reserva)
    db.commit()
    db.refresh(nueva_reserva)
    response.status_code = status.HTTP_201_CREATED
    return nueva_reserva

# PUT /reserva/confirmar
@app.put("/reserva/confirmar", response_model=schemas.ReservaResponse)
def confirmar_reserva(datos: schemas.ReservaAccion, db: Session = Depends(get_db)):
    '''Endpoint para confirmar la reserva de juegos.'''
    reserva = db.query(models.Reserva).filter(models.Reserva.pedido_id == datos.pedido_id).first()
    
    if reserva is None:
        raise HTTPException(status_code=404, detail='Reserva no encontrada')
    if reserva.estado == models.EstadoReserva.CANCELADA:
        raise HTTPException(status_code=400, detail='Reserva ya fue cancelada, no se puede confirmar')
    elif reserva.estado == models.EstadoReserva.CONFIRMADA:
        return reserva

    reserva.estado = models.EstadoReserva.CONFIRMADA
    db.commit()
    db.refresh(reserva)
    return reserva

# PUT /reserva/cancelar
@app.put("/reserva/cancelar", response_model=schemas.ReservaResponse)
def cancelar_reserva(datos: schemas.ReservaAccion, db: Session = Depends(get_db)):
    '''Endpoint para cancelar la reserva de juegos.'''

    reserva = db.query(models.Reserva).filter(models.Reserva.pedido_id == datos.pedido_id).first()
    
    if reserva is None:
        raise HTTPException(status_code=404, detail='Reserva no encontrada')
    if reserva.estado == models.EstadoReserva.CANCELADA:
        return reserva
    elif reserva.estado == models.EstadoReserva.CONFIRMADA:
        raise HTTPException(status_code=400, detail='Reserva ya fue confirmada, no se puede cancelar')

    # Devolvemos el stock
    stock = db.query(models.Stock).filter(models.Stock.juego_id == reserva.juego_id).first()
    if stock is None:
        raise HTTPException(status_code=500, detail='Stock no encontrado para el juego reservado')
    stock.cantidad += reserva.cantidad

    reserva.estado = models.EstadoReserva.CANCELADA
    db.commit()
    db.refresh(reserva)
    return reserva