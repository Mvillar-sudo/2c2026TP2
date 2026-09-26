from flask import jsonify

"""
Pre: Recibe el codigo de estado HTTP, el cual debe ser un entero valido, y el codigo de alfanumerico de error, 
mensaje, descripcion y nivel igualado a error, los cuales deben ser strings.
Post: Devuelve una tupla con el JSON de respuesta junto a un codigo de estado.
"""
def error_response(status, code, message, description, level="error"):
    return jsonify({
        "errors": [
            {
                "code": code,
                "message": message,
                "level": level,
                "description": description
            }
        ]
    }), status