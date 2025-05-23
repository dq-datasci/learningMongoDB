# src/database.py
from pymongo import MongoClient
from dotenv import load_dotenv
import os

# Cargar variables de entorno
load_dotenv()

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
DATABASE_NAME = "examen" # Base de datos para usuarios y planilla de sueldos

# Cliente global para no abrir y cerrar conexiones constantemente
_mongo_client = None

def get_mongo_client():
    """Obtiene una instancia del cliente de MongoDB."""
    global _mongo_client
    if _mongo_client is None:
        try:
            _mongo_client = MongoClient(MONGO_URI)
            # El ping es opcional, pero verifica la conexión
            _mongo_client.admin.command('ping')
            print("Conexión a MongoDB establecida.")
        except Exception as e:
            print(f"Error al conectar a MongoDB: {e}")
            _mongo_client = None # Reinicia el cliente si hay un error
            raise # Lanza la excepción para que el llamador lo maneje
    return _mongo_client

def get_db():
    """Retorna la base de datos 'examen'."""
    client = get_mongo_client()
    return client[DATABASE_NAME]

def close_mongo_client():
    """Cierra la conexión de MongoDB si está abierta."""
    global _mongo_client
    if _mongo_client:
        _mongo_client.close()
        print("Conexión a MongoDB cerrada.")
        _mongo_client = None