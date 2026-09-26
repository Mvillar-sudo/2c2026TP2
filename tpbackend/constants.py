import os

from dotenv import load_dotenv

load_dotenv()

BASE_URL = '/api'
DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_PORT = int(os.getenv('DB_PORT', '3306'))
DB_USER = os.getenv('DB_USER', 'root')
DB_PASSWORD = os.getenv('DB_PASSWORD', 'root')
DB_NAME = os.getenv('DB_NAME', 'club_deportivo')
DB_URL = f'mysql+mysqlconnector://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}'

ERROR_INVALID_BODY = 'invalid.body'
ERROR_INVALID_PARAMETER = 'invalid.parameter'
ERROR_SOCIO_NOT_FOUND = 'socio.not.found'
ERROR_EMAIL_ALREADY_EXISTS = 'socio.email.already.exists'
