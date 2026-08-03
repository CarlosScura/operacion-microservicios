Los Pingüinos del Monolito
Documento de Diseño Técnico — Sistema de Microservicios
Tienda de videojuegos — Arquitectura, endpoints, seguridad y resiliencia

1. Visión general
El sistema modela una tienda de videojuegos compuesta por 4 microservicios independientes, cada uno con responsabilidad única, base de datos propia y contenedor Docker propio. Los servicios se comunican entre sí vía REST (HTTP), sin API Gateway (decisión consciente por tiempo de entrega; queda como posible mejora futura).
Reseñas se evaluó y se descartó conscientemente: requería dependencia adicional con Pedidos (validar que el producto fue comprado) y no aportaba al objetivo central del challenge (arquitectura, JWT, Circuit Breaker, Docker).
2. Microservicios
2.1 Catálogo
Responsabilidad: información descriptiva de los juegos — nombre, género, precio, descripción. No conoce el stock (eso es de Inventario).
Método	Endpoint	Descripción	Acceso
GET	/juegos	Lista todos los juegos	Usuario, Admin
GET	/juegos/{id}	Detalle de un juego puntual	Usuario, Admin
POST	/juegos	Crea un nuevo juego	Admin
PUT	/juegos/{id}	Modifica un juego existente	Admin
DELETE	/juegos/{id}	Elimina un juego	Admin
2.2 Inventario
Responsabilidad: cantidad de stock disponible por juego, y su ciclo de reserva. Es el único dueño del dato de stock.
Método	Endpoint	Descripción	Acceso
GET	/stock	Stock de todos los juegos	Usuario, Admin
GET	/stock/{id}	Stock de un juego puntual	Usuario, Admin
PUT	/stock	Carga de stock nuevo (idempotente)	Admin
PUT	/reserva	Reserva N unidades para un pedido (idempotente por ID de pedido)	Pedidos (interno)
PUT	/reserva/confirmar	Confirma una reserva: descuento definitivo	Pedidos (interno)
PUT	/reserva/cancelar	Libera una reserva: devuelve unidades al stock	Pedidos (interno)
Nota de diseño: reservar/confirmar/cancelar usan PUT porque son idempotentes al incluir una idempotency key (el ID del pedido). Si la misma llamada se reintenta (ej. por un retry del Circuit Breaker), el sistema reconoce que ya existe una reserva para ese pedido y no descuenta dos veces.
2.3 Pedidos / Pagos
Responsabilidad: qué compró un cliente, estado del pedido (pendiente, pagado, cancelado) y el registro del pago. Servicios fusionados intencionalmente: el pago ocurre siempre en el contexto de un pedido existente, y separar ambos hubiera duplicado la petición del pedido sin necesidad real.
Método	Endpoint	Descripción	Acceso
GET	/pedidos	Lista todos los pedidos	Admin
GET	/pedidos?estado=...	Filtra pedidos por estado (pendiente / pagado / cancelado)	Usuario, Admin
GET	/pedidos/{id}	Detalle de un pedido puntual	Usuario, Admin
POST	/pedidos	Crea un nuevo pedido	Usuario
PUT	/pedidos/{id}	Cambia el estado del pedido (pagar / cancelar), body: {estado}	Usuario, Admin
POST	/pedidos/{id}/items	Agrega un ítem (juego) al pedido	Usuario
DELETE	/pedidos/{id}/items/{item_id}	Quita un ítem del pedido	Usuario
Nota: cancelar un pedido usa PUT (cambia estado a "cancelado"), no DELETE — se necesita conservar el historial de pedidos cancelados para poder listarlos.
2.4 Usuarios
Responsabilidad: identidad, credenciales, datos personales y tarjetas guardadas. Único servicio que emite JWT (vía login).
Método	Endpoint	Descripción	Acceso
GET	/usuarios	Lista todos los usuarios	Admin
GET	/usuarios/{id}	Datos de un usuario puntual	Usuario (propio), Admin
POST	/usuarios	Registro de usuario nuevo	Público
PUT	/usuarios/{id}	Modifica datos del usuario	Usuario (propio), Admin
DELETE	/usuarios/{id}	Elimina un usuario	Admin
POST	/usuarios/{id}/tarjetas	Agrega una tarjeta guardada	Usuario (propio)
DELETE	/usuarios/{id}/tarjetas/{tarjeta_id}	Elimina una tarjeta guardada	Usuario (propio)
POST	/login	Autenticación — devuelve JWT	Público
3. Seguridad — JWT
•	El token se emite una sola vez, en POST /login, tras validar usuario y contraseña.
•	Cada microservicio valida el token de forma independiente (firma + expiración), sin llamar a Usuarios en cada request — todos comparten la misma clave secreta (variable de entorno).
•	El token tiene expiración (ej. minutos/horas) para limitar el daño si es robado o filtrado.
•	Datos sensibles (tarjetas) nunca se cachean ni se exponen en URLs; viajan en el body de la petición.
4. Comunicación entre servicios y Circuit Breaker
El Circuit Breaker se aplica del lado de quien llama, no de quien responde (protege al que llama de que el otro no responda). Se identificaron 4 llamadas entre servicios, cada una con retry + Circuit Breaker y su propio fallback:
Llamada	Motivo	Fallback si el circuito está abierto
Catálogo → Inventario	Consultar stock para mostrarlo junto al juego	Cache corto del último stock conocido
Pedidos → Inventario	Reservar / confirmar / liberar stock	Error controlado: "no disponible, reintentá"
Pedidos → Catálogo	Obtener el precio del juego al armar el pedido	Error controlado (no se inventa el precio)
Pedidos → Usuarios	Obtener datos de la tarjeta guardada para pagar	Error controlado, sin cache ni retry largo (dato sensible)
 
Retry: 2-3 reintentos con una breve espera entre cada uno (backoff), antes de considerar el circuito abierto. Estados: cerrado (funciona normal) -> abierto (deja de intentar y responde con el fallback) -> semi-abierto (deja pasar algunas peticiones de prueba para decidir si vuelve a cerrarse o se abre de nuevo).
5. Decisiones de diseño — justificación para la defensa
•	Catálogo e Inventario están separados: el precio/nombre y el stock cambian por razones y a velocidades distintas (cada venta cambia el stock; el precio cambia por decisión comercial). Se comunican vía HTTP en tiempo real en vez de duplicar datos.
•	Pedidos y Pagos están fusionados: el pago ocurre siempre en el contexto de un pedido; separarlos duplicaría la petición del pedido sin necesidad real en el alcance de este proyecto.
•	Reseñas fue descartado conscientemente por la dependencia adicional que introducía (validar compra contra Pedidos) frente al tiempo disponible.
•	No hay API Gateway: decisión de tiempo (3-5 días); cada servicio se expone directo, documentado con Swagger (gratis con FastAPI). Queda como posible mejora/bonus futuro.
•	JWT emitido una sola vez por Usuarios; validado de forma independiente por cada servicio con una clave secreta compartida — evita acoplar los servicios a una consulta constante contra Usuarios.
•	Reservas de stock son idempotentes (idempotency key = ID de pedido) para que un retry del Circuit Breaker no descuente stock dos veces.
