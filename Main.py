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
    # --- Nombres de colecciones (modificar el día de la prueba según el JSON entregado) ---
    NOMBRE_CLIENTES = "clientes_20"
    NOMBRE_PEDIDOS = "pedidos_20"

except ConnectionFailure as e:
    print(f"Error de conexión a MongoDB: {e}")
def cls():
    os.system("cls")

# Herramientas/utilidades

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

# Consulta 1: Listar clientes inactivos con filtros
def consulta_1_clientes_inactivos(db):
    """
    Equivalente de consulta en MongoDB:
    Consulta todos los clientes inactivos
    db.clientes_20.find(
    { "Activo": false },
    { "_id": 1, "nombre": 1, "fecha_registro": 1 }
    )

    Consulta cliente inactivo por id
    db.clientes_20.find(
    { "Activo": false, "_id": "11111111-1"},
    { "_id": 1, "nombre": 1, "fecha_registro": 1 }
    )
    """
    coleccion = db[NOMBRE_CLIENTES]
    opcion = input("¿Desea filtrar por ID? (s/n): ").strip().lower()
    proyeccion = {"_id": 1, "nombre": 1, "fecha_registro": 1}

    if opcion == "s":
        id_cliente = input("Ingrese el ID del cliente: ").strip()
        filtro = {"Activo": False, "_id": id_cliente}

        resultados = coleccion.find(filtro, proyeccion)

        contador = 0
        for cliente in resultados:
            print(cliente)
            contador += 1

        if contador == 0:
            print(f"No se encontró un cliente inactivo con ID '{id_cliente}'.")

    elif opcion == "n":
        filtro = {"Activo": False}
        resultados = coleccion.find(filtro, proyeccion)

        contador = 0
        for cliente in resultados:
            print(cliente)
            contador += 1

        if contador == 0:
            print("No se encontraron clientes inactivos.")

    else:
        print("Opción inválida.")

# Consulta 2: Buscar clientes por nombre o email (regex)
def consulta_2_buscar_regex(db):
    """
    Equivalente en MongoDB:
    db.clientes_20.find({
        "$or": [
            { "nombre": { "$regex": texto, "$options": "i" } },
            { "email":  { "$regex": texto$, "$options": "i" } }
        ]
    })
    """
    coleccion = db[NOMBRE_CLIENTES]
    texto = input("Ingrese nombre parcial o dominio de email a buscar (Ej: pedo, yahoo.com):").strip()

    filtro = {
        "$or": [
            {"nombre": {"$regex": texto, "$options": "i"}},
            {"email":  {"$regex": f"{texto}$", "$options": "i"}}
        ]
    }

    resultados = coleccion.find(filtro)

    contador = 0
    for cliente in resultados:
        print(cliente)
        contador += 1

    if contador == 0:
        print(f"No se encontraron coincidencias para '{texto}'.")

# Consulta 3: Verificar si un cliente tiene el producto por id
def consulta_3_buscar_cliente_producto(db):
    """
    Equivalente en MongoDB:
    db.pedidos_20.find({
        "cliente_id": "11111111-1",
        "productos.producto_id": 101
    })
    """
    coleccion = db[NOMBRE_PEDIDOS]
    cliente_id = input("Ingrese el ID del cliente a verificar: ").strip()
    filtro = {
        "cliente_id": cliente_id,
        "productos.producto_id": 101
    }

    resultados = coleccion.find(filtro)

    for pedido in resultados:
        print(f"El cliente con ID '{cliente_id}' tiene el producto 101 en el pedido con ID '{pedido['_id']}'.")
        encontrado = True
    
    if not encontrado:
        print(f"El cliente con ID '{cliente_id}' NO tiene el producto 101 en ningún pedido.")
    
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
        cls()
        print("\n--- MENÚ ---")
        for clave, texto in opciones.items():
            print(f"[{clave}] {texto}")

        opcion = input("Selecciona una opción: ").strip()

        if opcion == "0":
            insertar_json(db)
            input("\nPresiona Enter para volver al menú...")

        elif opcion == "1":
            consulta_1_clientes_inactivos(db)
            input("\nPresiona Enter para volver al menú...")

        elif opcion == "2":
            consulta_2_buscar_regex(db)
            input("\nPresiona Enter para volver al menú...")

        elif opcion == "3":
            consulta_3_buscar_cliente_producto(db)
            input("\nPresiona Enter para volver al menú...")

        elif opcion == "4":
            pass  # TODO: consulta 4 - agregación
        elif opcion == "9":
            print("Saliendo...")
            break
        else:
            print("Opción no válida")

menu(db)