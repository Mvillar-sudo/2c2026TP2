"""
Rutas relacionadas a la entidad "cancha".

Este archivo se ocupa únicamente de: recibir el request, llamar al
validador correspondiente, hablar con la base de datos y devolver la
respuesta. Toda la validación vive en validators/canchas.py.
"""
from flask import Blueprint, request, jsonify
from mysql.connector import Error as MySQLError
from datetime import datetime
from db import get_connection
from errors import error_response
from tpbackend.validators.canchas import validar_creacion, validar_modificacion, validar_reglas_horarias

canchas_bp = Blueprint("canchas", __name__)

"""
Pre: 'base_url' debe ser string. 
'total_items', 'limit' y 'offset' debem ser ints mayores o iguales a 0.
Post: Devuelve un diccionario con los hipervínculos HATEOAS calculados según los parámetros.
"""
def generar_hateoas(base_url, total_items, limit, offset, query_extra=""):
    links = {}
    extra = f"&{query_extra}" if query_extra else ""
    links["_first"] = {"href": f"{base_url}?_limit={limit}&_offset=0{extra}"}
    if offset > 0:
        prev_offset = max(0, offset - limit)
        links["_prev"] = {"href": f"{base_url}?_limit={limit}&_offset={prev_offset}{extra}"}
    if offset + limit < total_items:
        links["_next"] = {"href": f"{base_url}?_limit={limit}&_offset={offset + limit}{extra}"}
    last_offset = max(0, ((total_items - 1) // limit) * limit) if total_items > 0 else 0
    links["_last"] = {"href": f"{base_url}?_limit={limit}&_offset={last_offset}{extra}"}
    return links

"""
Pre: La base de datos debe estar activa y accesible mediante get_connection().
Post: Inserta una nueva cancha y devuelve 201 con la entidad creada.
Ante algun error devuelve 400/404/500 dependiendo de lo ocurrido.
"""
@canchas_bp.route("/canchas", methods=["POST"])
def crear_cancha():
    body = request.get_json(silent=True)

    error, datos = validar_creacion(body)
    if error:
        return error

    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute(
            "SELECT id_deporte FROM deportes WHERE id_deporte = %s",
            (datos["id_deporte"],)
        )
        if cursor.fetchone() is None:
            return error_response(404, "DEPORTE_NO_ENCONTRADO",
                                   "El deporte indicado no existe",
                                   f"No existe un deporte con id_deporte={datos['id_deporte']}.")

        cursor.execute(
            """
            INSERT INTO canchas (nombre_cancha, id_deporte, precio_hora, techada, cancha_activa)
            VALUES (%s, %s, %s, %s, %s)
            """,
            (datos["nombre"], datos["id_deporte"], datos["precio_hora"],
             datos["techada"], datos["activa"])
        )
        conn.commit()
        nuevo_id = cursor.lastrowid

        return jsonify({
            "id": nuevo_id,
            "nombre": datos["nombre"],
            "id_deporte": datos["id_deporte"],
            "precio_hora": datos["precio_hora"],
            "techada": datos["techada"],
            "activa": datos["activa"],
        }), 201

    except MySQLError as e:
        return error_response(500, "ERROR_BASE_DE_DATOS",
                               "Ocurrió un error interno al acceder a la base de datos",
                               str(e))
    finally:
        if conn is not None:
            conn.close()

"""
Pre: La base de datos debe estar activa e 'id' debe ser un entero.
Post: Modifica los campos solicitados y devuelve 204 No Content, o 400/404/500 ante errores.
"""
@canchas_bp.route("/canchas/<int:id>", methods=["PATCH"])
def actualizar_cancha(id):
    body = request.get_json(silent=True)
    error, updates_dict = validar_modificacion(body)
    if error:
        return error

    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("SELECT id_cancha FROM canchas WHERE id_cancha = %s", (id,))
        if not cursor.fetchone():
            return error_response(404, "NO_ENCONTRADO", "Recurso no encontrado", f"Cancha con id {id} no encontrada")

        clausulas = [f"{campo} = %s" for campo in updates_dict.keys()]
        valores = list(updates_dict.values()) + [id]

        query = f"UPDATE canchas SET {', '.join(clausulas)} WHERE id_cancha = %s"
        cursor.execute(query, tuple(valores))
        conn.commit()

        return '', 204
    except MySQLError as e:
        return error_response(500, "ERROR_BASE_DE_DATOS", "Error interno al acceder a la base de datos", str(e))
    finally:
        if conn:
            conn.close()

"""
Pre: La base de datos debe estar activa e 'id' debe ser un int.
Post: Elimina la cancha y devuelve 204 si no tiene reservas.
En caso de tener reservas no elimina la cancha y devuelve 409.
Si ocurre algun error devuelve 404/500 dependiendo de la situacion.
"""
@canchas_bp.route("/canchas/<int:id>", methods=["DELETE"])
def eliminar_cancha(id):
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("SELECT id_cancha FROM canchas WHERE id_cancha = %s", (id,))
        if not cursor.fetchone():
            return error_response(404, "NO_ENCONTRADO", "Recurso no encontrado", f"Cancha con id {id} no encontrada")

        cursor.execute("SELECT id_reserva FROM reservas WHERE id_cancha = %s LIMIT 1", (id,))
        if cursor.fetchone():
            return error_response(409, "CONFLICTO", "Conflicto de integridad", "No se puede eliminar la cancha porque posee reservas asociadas")

        cursor.execute("DELETE FROM canchas WHERE id_cancha = %s", (id,))
        conn.commit()

        return '', 204
    except MySQLError as e:
        return error_response(500, "ERROR_BASE_DE_DATOS", "Error interno al acceder a la base de datos", str(e))
    finally:
        if conn:
            conn.close()

"""
Pre: La base de datos debe estar activa y accesible mediante get_connection().
Post: Devuelve 200 con la lista paginada de canchas disponibles y sus enlaces HATEOAS.
En caso de que ocurra algun error devuelve 400/500 dependiendo del caso.
"""
@canchas_bp.route("/canchas/disponibles", methods=["GET"])
def canchas_disponibles():
    permitidos = {'fecha', 'hora_inicio', 'hora_fin', 'id_deporte', 'techada', '_limit', '_offset'}
    for param in request.args.keys():
        if param not in permitidos:
            return error_response(400, "PARAMETRO_INVALIDO", "Parametro desconocido", f"El parametro '{param}' no esta permitido")

    fecha = request.args.get('fecha')
    hora_inicio = request.args.get('hora_inicio')
    hora_fin = request.args.get('hora_fin')

    if not (fecha and hora_inicio and hora_fin):
        return error_response(400, "CAMPOS_FALTANTES", "Parametros faltantes", "Parametros obligatorios: fecha, hora_inicio, hora_fin")

    try:
        inicio = datetime.fromisoformat(f"{fecha}T{hora_inicio}-03:00")
        fin = datetime.fromisoformat(f"{fecha}T{hora_fin}-03:00")
    except ValueError:
        return error_response(400, "FORMATO_INVALIDO", "Formato invalido", "Formato de fecha u hora incorrecto (esperado YYYY-MM-DD y HH:MM:SS)")

    valido, msg = validar_reglas_horarias(inicio, fin)
    if not valido:
        return error_response(400, "REGLA_HORARIA_INVALIDA", "Horario no valido", msg)

    try:
        limit = int(request.args.get('_limit', 10))
        offset = int(request.args.get('_offset', 0))
    except ValueError:
        return error_response(400, "PAGINACION_INVALIDA", "Parametros de paginacion invalidos", "_limit y _offset deben ser enteros")

    if limit < 1 or limit > 100 or offset < 0:
        return error_response(400, "PAGINACION_INVALIDA", "Rango de paginacion invalido", "_limit debe estar entre 1 y 100, y _offset mayor o igual a 0")

    str_inicio = inicio.strftime('%Y-%m-%d %H:%M:%S')
    str_fin = fin.strftime('%Y-%m-%d %H:%M:%S')

    query_base = """
        FROM canchas c
        WHERE c.cancha_activa = TRUE
        AND c.id_cancha NOT IN (
            SELECT id_cancha FROM reservas
            WHERE estado = 'confirmada'
            AND fecha_hora_inicio < %s AND fecha_hora_fin > %s
        )
    """
    params = [str_fin, str_inicio]
    filtros_url = [f"fecha={fecha}", f"hora_inicio={hora_inicio}", f"hora_fin={hora_fin}"]

    if request.args.get('id_deporte'):
        try:
            id_dep = int(request.args.get('id_deporte'))
            query_base += " AND c.id_deporte = %s"
            params.append(id_dep)
            filtros_url.append(f"id_deporte={id_dep}")
        except ValueError:
            return error_response(400, "VALOR_INVALIDO", "id_deporte invalido", "id_deporte debe ser un numero entero")

    if request.args.get('techada') is not None:
        techada_val = request.args.get('techada').lower()
        if techada_val in ['true', 'false']:
            query_base += " AND c.techada = %s"
            params.append(techada_val == 'true')
            filtros_url.append(f"techada={techada_val}")
        else:
            return error_response(400, "VALOR_INVALIDO", "techada invalida", "El filtro techada debe ser true o false")

    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute(f"SELECT COUNT(*) as total {query_base}", tuple(params))
        total = cursor.fetchone()['total']

        query_canchas = f"""
            SELECT c.id_cancha AS id, c.nombre_cancha AS nombre, c.id_deporte, c.precio_hora, c.techada, c.cancha_activa AS activa
            {query_base} ORDER BY c.id_cancha ASC LIMIT %s OFFSET %s
        """
        cursor.execute(query_canchas, tuple(params + [limit, offset]))
        canchas = cursor.fetchall()

        for c in canchas:
            c['techada'] = bool(c['techada'])
            c['activa'] = bool(c['activa'])

        links = generar_hateoas(request.base_url, total, limit, offset, "&".join(filtros_url))
        return jsonify({"canchas": canchas, "_links": links}), 200
    except MySQLError as e:
        return error_response(500, "ERROR_BASE_DE_DATOS", "Error interno al acceder a la base de datos", str(e))
    finally:
        if conn:
            conn.close()