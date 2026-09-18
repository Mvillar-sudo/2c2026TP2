import mysql.connector
import os
from dotenv import load_dotenv

load_dotenv()


def get_connection():
    """
    Abre y devuelve una nueva conexion a mysql usando los datos del .env
    """

    return mysql.connector.connect(
        host=os.getenv("DB_HOST", "localhost"),
        port=int(os.getenv("DB_PORT", 3306)),
        database=os.getenv("DB_NAME", "club_deportivo"),
        user=os.getenv("DB_USER", "root"),
        password=os.getenv("DB_PASSWORD", "")
    )