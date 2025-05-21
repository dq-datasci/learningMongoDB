# src/app.py
from pymongo import MongoClient
from dotenv import load_dotenv
import os
# from dotenv import load_dotenv # Mantén esta línea para la prueba
# load_dotenv()

# Cargar variables de entorno desde .env
# Asegúrate de que este archivo esté en la raíz de tu proyecto, no dentro de src
load_dotenv()

def get_mongo_client():
    """Obtiene un cliente de MongoDB usando la URI de las variables de entorno o la predeterminada."""
    # Intenta obtener la URI de MongoDB de las variables de entorno
    # Si MONGO_URI no está definida en .env, usa la URI local por defecto
    mongo_uri = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
    print(f"Intentando conectar a MongoDB con URI: {mongo_uri.split('@')[-1] if '@' in mongo_uri else mongo_uri}") # Para no imprimir credenciales
    return MongoClient(mongo_uri)

def main():
    client = None # Inicializa client a None
    try:
        client = get_mongo_client()
        # Acceder a una base de datos (se crea si no existe)
        db = client.mydatabase
        # Acceder a una colección (se crea si no existe)
        my_collection = db.mycollection

        print("Conexión a MongoDB exitosa.")

        # ---- Operaciones CRUD de ejemplo ----

        # 1. Insertar un documento
        post = {
            "author": "Alice",
            "text": "My first blog post!",
            "tags": ["mongodb", "python"],
            "status": "published"
        }
        # Evitar insertar si ya existe para pruebas repetidas
        if my_collection.find_one({"author": "Alice", "text": "My first blog post!"}) is None:
            post_id = my_collection.insert_one(post).inserted_id
            print(f"Documento insertado con ID: {post_id}")
        else:
            print("Documento de Alice ya existe, omitiendo inserción.")

        # 2. Encontrar documentos
        print("\nDocumentos en la colección:")
        for doc in my_collection.find():
            print(doc)

        # 3. Actualizar un documento
        my_collection.update_one(
            {"author": "Alice"},
            {"$set": {"status": "updated", "timestamp": "2023-10-26"}}
        )
        print("\nDocumento de Alice actualizado:")
        print(my_collection.find_one({"author": "Alice"}))

        # 4. Eliminar un documento (descomentar la línea de abajo para probarlo)
        # result = my_collection.delete_one({"author": "Alice"})
        # print(f"\nDocumento de Alice eliminado: {result.deleted_count} documento(s)")
        # print("Documentos restantes después de la eliminación:")
        # for doc in my_collection.find():
        #     print(doc)

    except Exception as e:
        print(f"Error al conectar o interactuar con MongoDB: {e}")
    finally:
        if client:
            client.close()
            print("Conexión a MongoDB cerrada.")

if __name__ == "__main__":
    main()