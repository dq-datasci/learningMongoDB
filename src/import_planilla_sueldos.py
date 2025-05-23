# src/import_csv.py
import csv
from pymongo import MongoClient
from dotenv import load_dotenv
import os
from datetime import datetime

# Cargar variables de entorno desde .env
load_dotenv()

# --- Configuración ---
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
DATABASE_NAME = "examen"
COLLECTION_NAME = "planilla_sueldos"
CSV_FILE_PATH = "datos_subir_examen.csv" # Asegúrate que este archivo esté en la raíz del proyecto

def get_mongo_client():
    """Obtiene un cliente de MongoDB."""
    print(f"Intentando conectar a MongoDB con URI: {MONGO_URI.split('@')[-1] if '@' in MONGO_URI else MONGO_URI}")
    return MongoClient(MONGO_URI)

def import_csv_to_mongodb():
    client = None
    try:
        client = get_mongo_client()
        db = client[DATABASE_NAME] # Accede a la base de datos 'examen'
        collection = db[COLLECTION_NAME] # Accede a la colección 'planilla_sueldos'

        # Opcional: Eliminar documentos existentes antes de la importación
        # Esto es útil para empezar de cero cada vez que ejecutes el script
        # print(f"Eliminando documentos existentes en la colección '{COLLECTION_NAME}'...")
        # collection.delete_many({})
        # print("Documentos eliminados.")

        print(f"Importando datos desde '{CSV_FILE_PATH}' a '{DATABASE_NAME}.{COLLECTION_NAME}'...")

        inserted_count = 0
        with open(CSV_FILE_PATH, mode='r', encoding='utf-8-sig') as csvfile:
            # Usa csv.DictReader para leer las filas como diccionarios
            # donde las claves son los encabezados del CSV
            # El utf-8-sig es para manejar el encoding UTF-8 con BOM
            csv_reader = csv.DictReader(csvfile)

            # Definir los nombres de las columnas en tu CSV para mapearlas
            # Asegúrate que estos nombres coincidan EXACTAMENTE con los de tu CSV
            # Nombre, Apellido, SEXO (M/F), DNI, ESTADO CIVIL, DEPORTE, SUELDO, FECHA INGRESO, N° HIJOS, PROFESIÓN
            field_names = [
                "Nombre", "Apellido", "SEXO (M/F)", "DNI", "ESTADO CIVIL",
                "DEPORTE", "SUELDO", "FECHA INGRESO", "N° HIJOS", "PROFESIÓN"
            ]

            # Itera sobre cada fila en el CSV
            for row_num, row in enumerate(csv_reader):
                document = {}
                for field in field_names:
                    # Limpia espacios en blanco alrededor del valor y maneja valores numéricos/fecha
                    value = row.get(field, '').strip()

                    if field == "SUELDO":
                        try:
                            # Intenta convertir SUELDO a float
                            document[field.replace(" ", "_").lower()] = float(value)
                        except ValueError:
                            document[field.replace(" ", "_").lower()] = None # O maneja el error como prefieras
                            print(f"Advertencia: Sueldo inválido '{value}' en fila {row_num + 2}. Se establecerá como None.")
                    elif field == "FECHA INGRESO":
                        try:
                            # Convierte FECHA INGRESO a un objeto datetime
                            # Asumiendo formato DD/MM/YYYY o DD-MM-YYYY
                            document[field.replace(" ", "_").lower()] = datetime.strptime(value, "%d/%m/%Y")
                        except ValueError:
                            try: # Intenta con otro formato común
                                document[field.replace(" ", "_").lower()] = datetime.strptime(value, "%d-%m-%Y")
                            except ValueError:
                                document[field.replace(" ", "_").lower()] = None
                                print(f"Advertencia: Fecha de ingreso inválida '{value}' en fila {row_num + 2}. Se establecerá como None.")
                    elif field == "N° HIJOS":
                        try:
                            # Intenta convertir N° HIJOS a int
                            document[field.replace(" ", "_").replace("°", "").lower()] = int(value)
                        except ValueError:
                            document[field.replace(" ", "_").replace("°", "").lower()] = None
                            print(f"Advertencia: N° Hijos inválido '{value}' en fila {row_num + 2}. Se establecerá como None.")
                    else:
                        # Para los demás campos, usa el valor tal cual, convirtiendo el nombre del campo
                        # a un formato más adecuado para MongoDB (minúsculas y guiones bajos)
                        document[field.replace(" ", "_").replace("(", "").replace(")", "").replace("°", "").lower()] = value

                # Inserta el documento en la colección
                collection.insert_one(document)
                inserted_count += 1
        print(f"Importación completada. Se insertaron {inserted_count} documentos.")

    except FileNotFoundError:
        print(f"Error: El archivo CSV '{CSV_FILE_PATH}' no se encontró en la raíz del proyecto.")
        print("Asegúrate de que 'datos_subir_examen.csv' esté en C:\\Proyectos\\learning_mongoDB\\")
    except Exception as e:
        print(f"Error durante la importación: {e}")
    finally:
        if client:
            client.close()
            print("Conexión a MongoDB cerrada.")

if __name__ == "__main__":
    import_csv_to_mongodb()