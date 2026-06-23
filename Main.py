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
    db = cliente["prueba3"]
    # --- Nombres de colecciones (modificar el día de la prueba según el JSON entregado) ---
    NOMBRE_INVITADOS = "invitados"
    NOMBRE_EVENTOS = "eventos"

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

# Consulta 1: Listar eventos por código
def consulta_1_eventos_por_categoria(db):
    """
    Equivalente de consulta en MongoDB:
    Consulta todos los invitados activos

    db.eventos.find(
    { "codigo": "EVT-2025-003" },
    { "_id": 0, "codigo": 1, "nombre":1, "fecha": 1 , "lugar": 1, "categoria": 1}
    )
    """
    coleccion = db[NOMBRE_EVENTOS]

    categoria = input("Ingrese el código del evento: ").strip()
    filtro = {"codigo": categoria}
    proyeccion = { "_id": 0, "codigo": 1, "nombre":1, "fecha": 1 , "lugar": 1, "categoria": 1}

    resultados = coleccion.find(filtro, proyeccion)

    contador = 0
    for evento in resultados:
        print(evento)
        contador += 1

    if contador == 0:
        print(f"No se encontraron eventos de la categoría '{categoria}'.")
    

# Consulta 2: Buscar invitados por nombre o email (regex)
def consulta_2_buscar_regex(db):
    """
    Equivalente en MongoDB:
    db.invitados.find({
        "$or": [
            { "nombre": { "$regex": texto, "$options": "i" } },
            { "correo":  { "$regex": texto$, "$options": "i" } }
        ]
    })
    """
    coleccion = db[NOMBRE_INVITADOS]
    texto = input("Ingrese nombre parcial o dominio de email a buscar (Ej: pedo, yahoo.com):").strip()

    filtro = {
        "$or": [
            {"nombre": {"$regex": texto, "$options": "i"}},
            {"correo":  {"$regex": f"{texto}$", "$options": "i"}}
        ]
    }

    resultados = coleccion.find(filtro)

    contador = 0
    for invitado in resultados:
        print(invitado)
        contador += 1

    if contador == 0:
        print(f"No se encontraron coincidencias para '{texto}'.")

# Consulta 3: Validación de acceso a eventos con búsqueda cruzada
def consulta_3_Lista_invitados_confirmados_evento(db):
    """
    """
    coleccion = db[NOMBRE_EVENTOS]
    codigo_evento = input("Ingrese el código del evento: ").strip()
    filtro = {
        "codigo": codigo_evento,
        "invitados.estado": "confirmado"
    }

    resultados = coleccion.find(filtro)

    for invitado in resultados:
        print(f"El invitado con rut '{invitado['rut']}' y nombre '{invitado['nombre']}' tiene el estado 'confirmado' para el evento '{codigo_evento}'.")
        encontrado = True
    
    if not encontrado:
        print(f"El cliente con ID '{codigo_evento}' NO tiene el producto 101 en ningún pedido.")

# Consulta 4: buscar a los 3 eventos con mayor número de invitados, 
def consulta_4_Top3_eventos_mas_invitados(db):

    """    
    """
    coleccion = db[NOMBRE_EVENTOS]
    filtro = [
        { "$group": { "_id": "$invitado_id", "total": { "$sum": 1 } } },
        { "$sort": { "total": -1 } },   
        { "$limit": 1 }
    ]

    resultados = coleccion.aggregate(filtro)

    for resultado in resultados:
        print(f"El evento con ID '{resultado['codigo']}' tiene el mayor número de invitados: {resultado['total']}.")
        encontrado = True
    
    if not encontrado:
        print("No se encontraron pedidos en la colección.")
        
# Menus
# Menu principal
def menu(db):
    opciones = {
        "0": "Cargar datos desde JSON a MongoDB",                     # LISTO
        "1": "Buscar evento por codigo",                              # LISTO    
        "2": "Buscar invitados por nombre o email (regex)",           # LISTO
        "3": "Verificar acceso a evento por estado (Confirmado)",     # FALTA
        "4": "Invitado con mayor número de pedidos",                  # FALTA
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
            consulta_1_eventos_por_categoria(db)
            input("\nPresiona Enter para volver al menú...")

        elif opcion == "2":
            consulta_2_buscar_regex(db)
            input("\nPresiona Enter para volver al menú...")

        elif opcion == "3":
            consulta_3_Lista_invitados_confirmados_evento(db)
            input("\nPresiona Enter para volver al menú...")

        elif opcion == "4":
            consulta_4_Top3_eventos_mas_invitados(db)
            input("\nPresiona Enter para volver al menú...")
        elif opcion == "9":
            print("Saliendo...")
            break
        else:
            print("Opción no válida")

menu(db)