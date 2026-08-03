CREATE TYPE estadopedido AS ENUM ('pendiente', 'pagado', 'cancelado');
CREATE TABLE IF NOT EXISTS pedidos (
    id SERIAL PRIMARY KEY,
    usuario_id INTEGER NOT NULL,
    estado estadopedido NOT NULL
);
CREATE TABLE IF NOT EXISTS items (
    id SERIAL PRIMARY KEY,
    pedido_id INTEGER NOT NULL REFERENCES pedidos(id),
    juego_id INTEGER NOT NULL,
    cantidad INTEGER NOT NULL,
    precio_unitario FLOAT NOT NULL
);
