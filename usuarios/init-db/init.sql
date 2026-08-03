CREATE TABLE IF NOT EXISTS usuarios (
    id SERIAL PRIMARY KEY,
    mail VARCHAR(100) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL
);
CREATE TABLE IF NOT EXISTS tarjetas (
    id SERIAL PRIMARY KEY,
    usuario_id INTEGER NOT NULL REFERENCES usuarios(id),
    nombre VARCHAR(100) NOT NULL,
    ultimos_4_digitos VARCHAR(4) NOT NULL,
    marca VARCHAR(20) NOT NULL
);
