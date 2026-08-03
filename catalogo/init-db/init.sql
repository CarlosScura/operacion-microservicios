CREATE TABLE IF NOT EXISTS juegos (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(150) NOT NULL,
    genero VARCHAR(50) NOT NULL,
    descripcion VARCHAR(255),
    precio FLOAT NOT NULL
);

