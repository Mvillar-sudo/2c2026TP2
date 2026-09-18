"""
Punto de entrada de la aplicación.

Creamos la app de Flask y registramos los blueprints de las distintas entidades.
"""

from flask import Flask

app = Flask(__name__)

app.register_blueprint(canchas_bp)

if __name__ == "__main__":
    app.run(port=8080, debug=True)


