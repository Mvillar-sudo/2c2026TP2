"""
Punto de entrada de la aplicación.

Creamos la app de Flask y registramos los blueprints de las distintas entidades.
"""

from flask import Flask, jsonify
from db import get_connection

app = Flask(__name__)

app.register_blueprint(canchas_bp)


#Edpoint: GET /deportes
app.route('/deportes', methods=['GET'])
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

if __name__ == "__main__":
    app.run(port=8080, debug=True)


