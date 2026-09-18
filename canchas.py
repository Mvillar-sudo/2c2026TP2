"""
Rutas relacionadas a la entidad "cancha".

Este archivo se ocupa únicamente de: recibir el request, llamar al
validador correspondiente, hablar con la base de datos y devolver la
respuesta. Toda la validación vive en validators/canchas.py.
"""
from flask import Blueprint, request, jsonify
from mysql.connector import Error as MySQLError
from db import get_connection
from errors import error_response
from validators.canchas import validar_creacion

canchas_bp = Blueprint("canchas", __name__)


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