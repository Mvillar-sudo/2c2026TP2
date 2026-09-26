"""
Punto de entrada de la aplicación.

Creamos la app de Flask y registramos los blueprints de las distintas entidades.
"""

from flask import Flask
from tpbackend.routes.canchas import canchas_bp
from tpbackend.routes.socios import socios_bp
from tpbackend.constants import BASE_URL

app = Flask(__name__)

app.register_blueprint(canchas_bp)
app.register_blueprint(socios_bp, url_prefix=BASE_URL)

if __name__ == "__main__":
    app.run(port=8080, debug=True)


