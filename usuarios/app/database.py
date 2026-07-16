from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase , sessionmaker
from dotenv import load_dotenv
import os

# leemos el archivo .env
load_dotenv()

# cargamos las variables del .env
DB_HOST = os.getenv('DB_HOST')
DB_NAME = os.getenv('DB_NAME')
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_PORT = os.getenv('DB_PORT')


# establecemos la conexion
engine = create_engine(
    f'postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}',
    connect_args={"options": "-c lc_messages=C"}
)

# 2. Configuración de la sesión local
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 3. Creación de la clase Base mediante herencia (Estilo 2.0)
class Base(DeclarativeBase):
    pass

