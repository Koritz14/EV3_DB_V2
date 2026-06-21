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

def insertar_json(db):
    for archivo in os.listdir():
        if archivo.endswith(".json"):
            nombre_coleccion = os.path.splitext(archivo)[0]

            with open(archivo, "r", encoding="utf-8") as f:
                datos = json.load(f)

            if not isinstance(datos, list):
                datos = [datos]

            db[nombre_coleccion].insert_many(datos)
            print(f"Datos insertados en la colección '{nombre_coleccion}'")


# Menus
# Menu principal
def menu(db):
    opciones = {
        "0": "Cargar datos desde JSON a MongoDB",
        "1": "Listar clientes inactivos",
        "2": "Buscar clientes por nombre o email (regex)",
        "3": "Verificar si un cliente tiene el producto 101",
        "4": "Cliente con mayor número de pedidos",
        "9": "Salir"
    }

    while True:
        print("\n--- MENÚ ---")
        for clave, texto in opciones.items():
            print(f"[{clave}] {texto}")

        opcion = input("Selecciona una opción: ").strip()

        if opcion == "0":
            insertar_json(db)
        elif opcion == "1":
            pass  # TODO: consulta 1 - filtros
        elif opcion == "2":
            pass  # TODO: consulta 2 - regex
        elif opcion == "3":
            pass  # TODO: consulta 3 - subdocumentos
        elif opcion == "4":
            pass  # TODO: consulta 4 - agregación
        elif opcion == "9":
            print("Saliendo...")
            break
        else:
            print("Opción no válida")

menu(db)