CREATE TYPE estadoreserva AS ENUM ('reservada', 'confirmada', 'cancelada');
CREATE TABLE IF NOT EXISTS stock (
    id SERIAL PRIMARY KEY,
    juego_id INTEGER NOT NULL UNIQUE,
    cantidad INTEGER NOT NULL
);
CREATE TABLE IF NOT EXISTS reserva (
    id SERIAL PRIMARY KEY,
    pedido_id INTEGER NOT NULL UNIQUE,
    juego_id INTEGER NOT NULL REFERENCES stock(juego_id),
    cantidad INTEGER NOT NULL,
    estado estadoreserva NOT NULL
);
