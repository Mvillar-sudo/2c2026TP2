from flask import Flask
from tpbackend.routes.canchas import canchas_bp
from tpbackend.routes.reservas import reservas_bp
from tpbackend.routes.socios import socios_bp

app = Flask(__name__)

app.register_blueprint(canchas_bp)
app.register_blueprint(reservas_bp)
app.register_blueprint(socios_bp)

if __name__ == "__main__":
    app.run(port=8080, debug=True)