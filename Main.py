from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, BulkWriteError
import json
import os


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

def cls():
    os.system("cls")

# Consultas

# Cargar datos desde archivos JSON 
def insertar_json(db):
    for archivo in os.listdir():
        if archivo.endswith(".json"):
            nombre_coleccion = os.path.splitext(archivo)[0]

            with open(archivo, "r", encoding="utf-8") as f:
                datos = json.load(f)

            if not isinstance(datos, list):
                datos = [datos]

            coleccion = db[nombre_coleccion]
            cantidad_actual = coleccion.count_documents({})

            if cantidad_actual > 0:
                respuesta = input(
                    f"La colección '{nombre_coleccion}' ya tiene {cantidad_actual} documento(s). "
                    f"¿Reemplazar? (s/n): "
                ).strip().lower()

                if respuesta == "s":
                    coleccion.drop()
                else:
                    print(f"Se omitió la carga de '{nombre_coleccion}'.")
                    continue  # pasa al siguiente archivo del for, sin insertar

            try:
                coleccion.insert_many(datos)
                print(f"Datos insertados en la colección '{nombre_coleccion}'")
            except BulkWriteError as e:
                print(f"Error al insertar en '{nombre_coleccion}': documentos duplicados u otro problema de escritura.")

# Consulta 1: Listar clientes inactivos 
def consulta_1_clientes_inactivos(db):
    """
    Consulta MongoDB equivalente:
    db.clientes.find(
        { "Activo": false },
        { "_id": 1, "nombre": 1, "fecha_registro": 1 }
    )
    """
    print("\n--- Clientes inactivos ---")

    filtro = {"Activo": False}
    proyeccion = {"_id": 1, "nombre": 1, "fecha_registro": 1}

    resultados = db.clientes.find(filtro, proyeccion)

    for cliente in resultados:
        print(cliente)

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
            input("\nPresiona Enter para volver al menú...")
            cls()

        elif opcion == "1":
            consulta_1_clientes_inactivos(db)
            input("\nPresiona Enter para volver al menú...")
            cls()
            
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