# operacion-microservicios
Septimo challenge de the Huddle, Operación Microservicios - Los pinguinos del monolito.

## Cómo correr cada microservicio

Cada microservicio tiene su propio entorno virtual ubicado en la carpeta raíz del servicio (./venv). Para iniciar uno, activar el entorno virtual y ejecutar uvicorn.

### Catálogo (puerto 8000)

```bash
cd catalogo/app
# Windows
..\venv\Scripts\activate
# macOS / Linux
source ../venv/bin/activate
uvicorn main:app --reload --port 8000
```

### Inventario (puerto 8001)

```bash
cd inventario/app
# Windows
..\venv\Scripts\activate
# macOS / Linux
source ../venv/bin/activate
uvicorn main:app --reload --port 8001
```

### Usuarios (puerto 8002)

```bash
cd usuarios/app
# Windows
..\venv\Scripts\activate
# macOS / Linux
source ../venv/bin/activate
uvicorn main:app --reload --port 8002
```

### Pedidos (puerto 8003)

```bash
cd pedidos/app
# Windows
..\venv\Scripts\activate
# macOS / Linux
source ../venv/bin/activate
uvicorn main:app --reload --port 8003
```

Notas:
- En Windows la activación del virtualenv es `..\venv\Scripts\activate` cuando se está dentro de la carpeta `app`.
- En macOS / Linux la activación es `source ../venv/bin/activate` cuando se está dentro de la carpeta `app`.
- Asegurarse de definir las variables de entorno necesarias (DB_HOST, DB_NAME, DB_USER, DB_PASSWORD, DB_PORT, JWT_SECRET_KEY) en un archivo `.env` en la carpeta del microservicio antes de arrancar.
- Cada servicio expone documentación Swagger en `/docs` una vez levantado.
