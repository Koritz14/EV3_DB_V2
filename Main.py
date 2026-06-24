from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, BulkWriteError
import json
import os

# ─────────────────────────────────────────────
#  CONEXIÓN
# ─────────────────────────────────────────────
db = None
try:
    cliente = MongoClient(
        "mongodb://localhost:27017/",
        serverSelectionTimeoutMS=3000
    )
    cliente.admin.command('ping')
    print("Conexión exitosa a MongoDB")
    db = cliente["prueba3"] # Nombre de la base de datos, modificar según corresponda
except ConnectionFailure as e:
    print(f"Error de conexión a MongoDB: {e}")
    exit(1)

# --- Nombres de colecciones (modificar el día de la prueba según el JSON entregado) ---
NOMBRE_INVITADOS = "invitados"
NOMBRE_EVENTOS   = "eventos"


# ─────────────────────────────────────────────
#  UTILIDADES
# ─────────────────────────────────────────────
def cls():
    os.system("cls" if os.name == "nt" else "clear")


def pedir_input(mensaje):
    """Solicita input y valida que no esté vacío."""
    while True:
        valor = input(mensaje).strip()
        if valor:
            return valor
        print("  El campo no puede estar vacío. Intente nuevamente.")


# ─────────────────────────────────────────────
#  CARGA DE DATOS
# ─────────────────────────────────────────────
def insertar_json(db):
    """Carga archivos JSON del directorio actual a MongoDB."""
    archivos_json = [f for f in os.listdir() if f.endswith(".json")]

    if not archivos_json:
        print("No se encontraron archivos JSON en el directorio actual.")
        return

    for archivo in archivos_json:
        nombre_coleccion = os.path.splitext(archivo)[0]

        try:
            with open(archivo, "r", encoding="utf-8") as f:
                datos = json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            print(f"Error al leer '{archivo}': {e}")
            continue

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
                continue

        try:
            coleccion.insert_many(datos)
            print(f"Datos insertados en la colección '{nombre_coleccion}'.")
        except BulkWriteError:
            print(f"Error al insertar en '{nombre_coleccion}': documentos duplicados u otro problema de escritura.")


# ─────────────────────────────────────────────
#  CONSULTAS
# ─────────────────────────────────────────────

# Consulta 1: Buscar evento por código
def consulta_1_eventos_por_categoria(db):
    """
    db.eventos.find(
        { "codigo": "<codigo>" },
        { "_id": 0, "codigo": 1, "nombre": 1, "fecha": 1, "lugar": 1, "categoria": 1 }
    )
    """
    coleccion = db[NOMBRE_EVENTOS]
    codigo = pedir_input("Ingrese el código del evento: ")

    filtro     = {"codigo": codigo}
    proyeccion = {"_id": 0, "codigo": 1, "nombre": 1, "fecha": 1, "lugar": 1, "categoria": 1}

    try:
        resultados = list(coleccion.find(filtro, proyeccion))
        if resultados:
            for evento in resultados:
                print(evento)
        else:
            print(f"No se encontraron eventos con código '{codigo}'.")
    except Exception as e:
        print(f"Error al ejecutar la consulta: {e}")


# Consulta 2: Buscar invitados por nombre parcial o dominio de correo (regex)
def consulta_2_buscar_regex(db):
    """
    db.invitados.find({
        "$or": [
            { "nombre": { "$regex": texto,   "$options": "i" } },
            { "correo":  { "$regex": texto+"$", "$options": "i" } }
        ]
    })
    """
    coleccion = db[NOMBRE_INVITADOS]
    texto = pedir_input("Ingrese nombre parcial o dominio de email (ej: pedro, yahoo.com): ")

    filtro = {
        "$or": [
            {"nombre": {"$regex": texto,        "$options": "i"}},
            {"correo":  {"$regex": f"{texto}$", "$options": "i"}}
        ]
    }

    try:
        resultados = list(coleccion.find(filtro))
        if resultados:
            for invitado in resultados:
                print(invitado)
        else:
            print(f"No se encontraron coincidencias para '{texto}'.")
    except Exception as e:
        print(f"Error al ejecutar la consulta: {e}")


# Consulta 3: Listar invitados confirmados de un evento (con $lookup)
def consulta_3_lista_invitados_confirmados(db):
    """
    db.eventos.aggregate([
        { "$match":  { "codigo": codigo_evento } },
        { "$unwind": "$invitados" },
        { "$match":  { "invitados.estado": "confirmado" } },
        { "$lookup": {
            "from":         "invitados",
            "localField":   "invitados.rut",
            "foreignField": "rut",
            "as":           "datos_invitado"
        }},
        { "$unwind": "$datos_invitado" },
        { "$project": {
            "_id": 0,
            "rut":    "$invitados.rut",
            "nombre": "$datos_invitado.nombre",
            "correo": "$datos_invitado.correo",
            "estado": "$invitados.estado"
        }}
    ])
    """
    coleccion    = db[NOMBRE_EVENTOS]
    codigo_evento = pedir_input("Ingrese el código del evento: ")

    pipeline = [
        {"$match":  {"codigo": codigo_evento}},
        {"$unwind": "$invitados"},
        {"$match":  {"invitados.estado": "confirmado"}},
        {"$lookup": {
            "from":         NOMBRE_INVITADOS,
            "localField":   "invitados.rut",
            "foreignField": "rut",
            "as":           "datos_invitado"
        }},
        {"$unwind": "$datos_invitado"},
        {"$project": {
            "_id":    0,
            "rut":    "$invitados.rut",
            "nombre": "$datos_invitado.nombre",
            "correo": "$datos_invitado.correo",
            "estado": "$invitados.estado"
        }}
    ]

    try:
        resultados = list(coleccion.aggregate(pipeline))
        if resultados:
            print(f"\nInvitados confirmados en '{codigo_evento}':")
            for inv in resultados:
                print(f"  RUT: {inv['rut']} | Nombre: {inv['nombre']} | Correo: {inv['correo']}")
        else:
            print(f"No se encontraron invitados confirmados para el evento '{codigo_evento}'.")
    except Exception as e:
        print(f"Error al ejecutar la consulta: {e}")


# Consulta 4: Top 3 eventos con mayor número de invitados confirmados
def consulta_4_top3_eventos_mas_invitados(db):
    """
    db.eventos.aggregate([
        { "$unwind": "$invitados" },
        { "$match":  { "invitados.estado": "confirmado" } },
        { "$group":  { "_id": { "codigo": "$codigo", "nombre": "$nombre" },
                       "total_confirmados": { "$sum": 1 } } },
        { "$sort":   { "total_confirmados": -1 } },
        { "$limit":  3 },
        { "$project": { "_id": 0,
                        "codigo": "$_id.codigo",
                        "nombre": "$_id.nombre",
                        "total_confirmados": 1 } }
    ])
    """
    coleccion = db[NOMBRE_EVENTOS]

    pipeline = [
        {"$unwind": "$invitados"},
        {"$match":  {"invitados.estado": "confirmado"}},
        {"$group": {
            "_id": {"codigo": "$codigo", "nombre": "$nombre"},
            "total_confirmados": {"$sum": 1}
        }},
        {"$sort":  {"total_confirmados": -1}},
        {"$limit": 3},
        {"$project": {
            "_id":               0,
            "codigo":            "$_id.codigo",
            "nombre":            "$_id.nombre",
            "total_confirmados": 1
        }}
    ]

    try:
        resultados = list(coleccion.aggregate(pipeline))
        if resultados:
            print("\nTop 3 eventos con más invitados confirmados:")
            for i, evt in enumerate(resultados, start=1):
                print(f"  #{i} | {evt['codigo']} - {evt['nombre']} | Confirmados: {evt['total_confirmados']}")
        else:
            print("No se encontraron resultados.")
    except Exception as e:
        print(f"Error al ejecutar la consulta: {e}")


# ─────────────────────────────────────────────
#  MENÚ PRINCIPAL
# ─────────────────────────────────────────────
def menu(db):
    opciones = {
        "0": "Cargar datos desde JSON a MongoDB",
        "1": "Buscar evento por código",
        "2": "Buscar invitados por nombre o email (regex)",
        "3": "Listar invitados confirmados de un evento ($lookup)",
        "4": "Top 3 eventos con más invitados confirmados",
        "9": "Salir"
    }

    while True:
        cls()
        print("\n--- MENÚ ---")
        for clave, texto in opciones.items():
            print(f"[{clave}] {texto}")

        opcion = input("\nSelecciona una opción: ").strip()

        if opcion == "0":
            insertar_json(db)
        elif opcion == "1":
            consulta_1_eventos_por_categoria(db)
        elif opcion == "2":
            consulta_2_buscar_regex(db)
        elif opcion == "3":
            consulta_3_lista_invitados_confirmados(db)
        elif opcion == "4":
            consulta_4_top3_eventos_mas_invitados(db)
        elif opcion == "9":
            print("Saliendo...")
            break
        else:
            print("Opción no válida.")

        if opcion != "9":
            input("\nPresiona Enter para volver al menú...")


menu(db)