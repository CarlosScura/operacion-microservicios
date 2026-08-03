from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
import database
import models
import schemas
import auth
from fastapi.responses import JSONResponse
from pybreaker import CircuitBreakerError
import circuit_breaker as cb

app = FastAPI()

@app.exception_handler(CircuitBreakerError)
async def circuit_breaker_handler(request, exc):
    return JSONResponse(
        status_code=503,
        content={"detail": "Servicio temporalmente no disponible, reintentá más tarde"}
    )


def get_db():
    '''Dependencia para obtener la sesión de la base de datos.'''
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()


def _assert_usuario_es_propietario(pedido, usuario_id: int):
    '''Verifica que el pedido pertenezca al usuario autenticado.'''
    if pedido.usuario_id != usuario_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tiene permisos para acceder a este pedido"
        )


@app.post("/pedidos", response_model=schemas.PedidoResponse, status_code=status.HTTP_201_CREATED)
def crear_pedido(pedido: schemas.PedidoCreate, db: Session = Depends(get_db), current_user: dict = Depends(auth.get_current_user)):
    '''Crea un pedido con sus items y lo inicia en estado PENDIENTE.'''
    if pedido.usuario_id != current_user["id"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No puede crear pedidos para otro usuario"
        )

    nuevo_pedido = models.Pedido(
        usuario_id=pedido.usuario_id,
        estado=models.EstadoPedido.PENDIENTE
    )
    db.add(nuevo_pedido)
    db.commit()
    db.refresh(nuevo_pedido)

    items_response = []
    total = 0.0

    for item in pedido.items:
        # Obtenemos el precio real desde Catálogo con Circuit Breaker
        precio_unitario = cb.obtener_precio_juego(item.juego_id)

        nuevo_item = models.Item(
            pedido_id=nuevo_pedido.id,
            juego_id=item.juego_id,
            cantidad=item.cantidad,
            precio_unitario=precio_unitario
        )
        db.add(nuevo_item)
        db.commit()
        db.refresh(nuevo_item)

        subtotal = nuevo_item.cantidad * nuevo_item.precio_unitario
        total += subtotal

        items_response.append({
            "id": nuevo_item.id,
            "pedido_id": nuevo_item.pedido_id,
            "juego_id": nuevo_item.juego_id,
            "cantidad": nuevo_item.cantidad,
            "precio_unitario": nuevo_item.precio_unitario,
            "subtotal": subtotal
        })
        cb.reservar_stock(
            pedido_id=nuevo_pedido.id,
            juego_id=item.juego_id,
            cantidad=item.cantidad
            )

    return {
        "id": nuevo_pedido.id,
        "usuario_id": nuevo_pedido.usuario_id,
        "estado": nuevo_pedido.estado,
        "items": items_response,
        "total": total
    }


@app.get("/pedidos", response_model=list[schemas.PedidoResponse])
def listar_pedidos(db: Session = Depends(get_db), current_user: dict = Depends(auth.get_current_user)):
    '''Lista los pedidos del usuario autenticado con sus items y totales.'''
    pedidos = db.query(models.Pedido).filter(models.Pedido.usuario_id == current_user["id"]).all()
    response = []

    for pedido in pedidos:
        items = db.query(models.Item).filter(models.Item.pedido_id == pedido.id).all()
        items_response = []
        total = 0.0
        for item in items:
            subtotal = item.cantidad * item.precio_unitario
            total += subtotal
            items_response.append({
                "id": item.id,
                "pedido_id": item.pedido_id,
                "juego_id": item.juego_id,
                "cantidad": item.cantidad,
                "precio_unitario": item.precio_unitario,
                "subtotal": subtotal
            })

        response.append({
            "id": pedido.id,
            "usuario_id": pedido.usuario_id,
            "estado": pedido.estado,
            "items": items_response,
            "total": total
        })

    return response


@app.get("/pedidos/{id}", response_model=schemas.PedidoResponse)
def obtener_pedido(id: int, db: Session = Depends(get_db), current_user: dict = Depends(auth.get_current_user)):
    '''Obtiene un pedido por su ID, incluyendo sus items y total.'''
    pedido = db.query(models.Pedido).filter(models.Pedido.id == id).first()
    if not pedido:
        raise HTTPException(status_code=404, detail="Pedido no encontrado")

    _assert_usuario_es_propietario(pedido, current_user["id"])

    items = db.query(models.Item).filter(models.Item.pedido_id == id).all()
    items_response = []
    total = 0.0
    for item in items:
        subtotal = item.cantidad * item.precio_unitario
        total += subtotal
        items_response.append({
            "id": item.id,
            "pedido_id": item.pedido_id,
            "juego_id": item.juego_id,
            "cantidad": item.cantidad,
            "precio_unitario": item.precio_unitario,
            "subtotal": subtotal
        })

    return {
        "id": pedido.id,
        "usuario_id": pedido.usuario_id,
        "estado": pedido.estado,
        "items": items_response,
        "total": total
    }


@app.post("/pedidos/{id}/items", response_model=schemas.ItemResponse, status_code=status.HTTP_201_CREATED)
def agregar_item_pedido(id: int, item: schemas.ItemCreate, db: Session = Depends(get_db), current_user: dict = Depends(auth.get_current_user)):
    '''Agrega un item a un pedido existente en estado PENDIENTE.'''
    pedido = db.query(models.Pedido).filter(models.Pedido.id == id).first()
    if not pedido:
        raise HTTPException(status_code=404, detail="Pedido no encontrado")

    _assert_usuario_es_propietario(pedido, current_user["id"])

    if pedido.estado != models.EstadoPedido.PENDIENTE:
        raise HTTPException(status_code=400, detail="No se puede agregar items a un pedido que no está en estado PENDIENTE")

    nuevo_item = models.Item(
        pedido_id=id,
        juego_id=item.juego_id,
        cantidad=item.cantidad,
        precio_unitario = cb.obtener_precio_juego(item.juego_id)
    )
    db.add(nuevo_item)
    db.commit()
    db.refresh(nuevo_item)

    subtotal = nuevo_item.cantidad * nuevo_item.precio_unitario
    return {
        "id": nuevo_item.id,
        "pedido_id": nuevo_item.pedido_id,
        "juego_id": nuevo_item.juego_id,
        "cantidad": nuevo_item.cantidad,
        "precio_unitario": nuevo_item.precio_unitario,
        "subtotal": subtotal
    }


@app.delete("/pedidos/{id}/items/{item_id}")
def eliminar_item_pedido(id: int, item_id: int, db: Session = Depends(get_db), current_user: dict = Depends(auth.get_current_user)):
    '''Elimina un item de un pedido si el pedido está en estado PENDIENTE.'''
    pedido = db.query(models.Pedido).filter(models.Pedido.id == id).first()
    if not pedido:
        raise HTTPException(status_code=404, detail="Pedido no encontrado")

    _assert_usuario_es_propietario(pedido, current_user["id"])

    if pedido.estado != models.EstadoPedido.PENDIENTE:
        raise HTTPException(status_code=400, detail="No se pueden eliminar items de un pedido que no esté en estado PENDIENTE")

    item = db.query(models.Item).filter(models.Item.id == item_id, models.Item.pedido_id == id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item no encontrado en el pedido")

    db.delete(item)
    db.commit()

    return {"mensaje": "Item eliminado exitosamente"}

@app.put("/pedidos/{id}", response_model=schemas.PedidoResponse)
def actualizar_estado_pedido(id: int, datos: schemas.PedidoUpdate, db: Session = Depends(get_db), current_user: dict = Depends(auth.get_current_user)):
    '''Actualiza el estado de un pedido existente.'''
    pedido = db.query(models.Pedido).filter(models.Pedido.id == id).first()
    if not pedido:
        raise HTTPException(status_code=404, detail="Pedido no encontrado")

    _assert_usuario_es_propietario(pedido, current_user["id"])

    # Llamamos a Inventario según el nuevo estado
    if datos.estado == models.EstadoPedido.PAGADO:
        cb.confirmar_reserva(pedido_id=id)
    elif datos.estado == models.EstadoPedido.CANCELADO:
        cb.cancelar_reserva(pedido_id=id)

    pedido.estado = datos.estado
    db.commit()
    db.refresh(pedido)

    items = db.query(models.Item).filter(models.Item.pedido_id == id).all()
    items_response = []
    total = 0.0
    for item in items:
        subtotal = item.cantidad * item.precio_unitario
        total += subtotal
        items_response.append({
            "id": item.id,
            "pedido_id": item.pedido_id,
            "juego_id": item.juego_id,
            "cantidad": item.cantidad,
            "precio_unitario": item.precio_unitario,
            "subtotal": subtotal
        })

    return {
        "id": pedido.id,
        "usuario_id": pedido.usuario_id,
        "estado": pedido.estado,
        "items": items_response,
        "total": total
    }
