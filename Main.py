from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
import json
import os

os.system("cls")

try:
    cliente = MongoClient(
        "mongodb://localhost:27017/",
        serverSelectionTimeoutMS=3000
        )

    cliente.admin.command('ping')
    print("Conexión exitosa a MongoDB")
    db = cliente["empresa"]

except ConnectionFailure as e:
    print(f"Error de conexión a MongoDB: {e}")

def insertar_json():
    for archivo in os.listdir():
        if archivo.endswith(".json"):
            nombre_coleccion = os.path.splitext(archivo)[0]

            with open(archivo, "r", encoding="utf-8") as f:
                datos = json.load(f)

            if not isinstance(datos, list):
                datos = [datos]

            db[nombre_coleccion].insert_many(datos)
            print(f"Datos insertados en la colección '{nombre_coleccion}'")