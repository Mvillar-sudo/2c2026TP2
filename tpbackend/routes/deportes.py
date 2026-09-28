from flask import Blueprint, jsonify
from db import get_connection

deportes_bp = Blueprint("deportes", __name__)

#Endpoint: GET /deportes
@deportes_bp.route('/deportes', methods=['GET'])
def obtener_deportes():
    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)

        sql = "SELECT id, nombre FROM deportes ORDER BY id ASC"
        cursor.execute(sql)
        deportes = cursor.fetchall()

        cursor.close()
        connection.close()

        return jsonify(deportes), 200
    except Exception as e:
        return jsonify({"error": "Error al consultar la base de datos", "detalle": str(e)}), 500
