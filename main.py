from flask import Flask, jsonify
from flask_cors import CORS
import logging

from database.mariadb_connection import MariaDBConnection
from routes import guia_route, promedio_tiempo_despacho_x_cond_pago

# Configuración de logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)
app = Flask(__name__)
db = MariaDBConnection()

# Middleware CORS
CORS(
    app,
    resources={
        r"/*": {
            "origins": "*",
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": "*",
        }
    },
)

# Registrar rutas
app.register_blueprint(promedio_tiempo_despacho_x_cond_pago.bp)
app.register_blueprint(guia_route.bp)


# Ruta raíz
@app.route("/")
def root():
    return (
        jsonify(
            {
                "message": "API de Análisis de Datos",
                "version": "1.0.0",
                "status": "Correcto",
            }
        ),
        404,
    )


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=8082,
        debug=True,     
    )

