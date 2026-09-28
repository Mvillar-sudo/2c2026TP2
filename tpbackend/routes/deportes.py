from flask import Blueprint, jsonify
from mysql.connector import Error as MySQLError
from db import get_connection
from errors import error_response

deportes_bp = Blueprint("deportes", __name__)

"""
Pre: La base de datos debe estar activa y accesible mediante get_connection().
Post: Devuelve 200 con la lista de deportes precargados, envuelta en la
clave 'deportes' tal como define el schema DeportesListResponse del
swagger. Ante un error de base de datos devuelve 500.
"""
@deportes_bp.route('/deportes', methods=['GET'])
def obtener_deportes():
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute(
            "SELECT id_deporte AS id, nombre_deporte AS nombre FROM deportes ORDER BY id_deporte ASC"
        )
        deportes = cursor.fetchall()

        return jsonify({"deportes": deportes}), 200

    except MySQLError as e:
        return error_response(500, "ERROR_BASE_DE_DATOS",
                               "Error interno al acceder a la base de datos", str(e))
    finally:
        if conn:
            conn.close()