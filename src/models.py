# src/models.py
from src.database import get_db
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from bson.objectid import ObjectId

class User:
    COLLECTION_NAME = "usuario" # Nombre de la colección de usuarios

    @staticmethod
    def get_collection():
        """Retorna la colección 'usuario'."""
        db = get_db()
        return db[User.COLLECTION_NAME]

    @staticmethod
    def create(nombre, apellido, celular, email, usuario, password):
        """
        Crea un nuevo usuario y lo inserta en la base de datos.
        Hashea la contraseña antes de guardarla.
        """
        users_collection = User.get_collection()

        # Verificar si el usuario o email ya existen
        if users_collection.find_one({"usuario": usuario}):
            print(f"Error: El usuario '{usuario}' ya existe.")
            return None
        if users_collection.find_one({"email": email}):
            print(f"Error: El email '{email}' ya existe.")
            return None

        # Hashear la contraseña por seguridad
        hashed_password = generate_password_hash(password)

        user_data = {
            "nombre": nombre,
            "apellido": apellido,
            "celular": celular,
            "email": email,
            "usuario": usuario,
            "password": hashed_password, # Guarda la contraseña hasheada
            "created_at": datetime.now() # Fecha de creación
        }
        try:
            result = users_collection.insert_one(user_data)
            print(f"Usuario '{usuario}' registrado con ID: {result.inserted_id}")
            return result.inserted_id
        except Exception as e:
            print(f"Error al registrar usuario: {e}")
            return None

    @staticmethod
    def find_by_username(username):
        """Busca un usuario por su nombre de usuario."""
        users_collection = User.get_collection()
        return users_collection.find_one({"usuario": username})

    @staticmethod
    def verify_password(hashed_password, password):
        """Verifica si la contraseña proporcionada coincide con el hash almacenado."""
        return check_password_hash(hashed_password, password)