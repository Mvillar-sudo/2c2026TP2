from sqlalchemy.exc import IntegrityError

from ..repositories import socios as db
from ..constants import ERROR_EMAIL_ALREADY_EXISTS
from ..utils import construir_error_api


def _email_repetido():
    return ValueError(construir_error_api(
        ERROR_EMAIL_ALREADY_EXISTS,
        'Email ya registrado',
        'Ya existe un socio con ese email',
    ), 409)


def listar_socios(nombre, activo, limit, offset):
    return (
        db.obtener_socios(nombre, activo, limit, offset),
        db.contar_socios(nombre, activo),
    )


def crear_socio(datos):
    if db.obtener_socio_por_email(datos['email']):
        raise _email_repetido()
    try:
        socio_id = db.insertar_socio(datos['nombre_socio'], datos['email'])
    except IntegrityError:
        raise _email_repetido()
    return db.obtener_socio(socio_id)


def obtener_socio(socio_id):
    return db.obtener_socio(socio_id)


def actualizar_socio(socio_id, datos):
    if not db.obtener_socio(socio_id):
        return None
    if 'email' in datos and db.obtener_socio_por_email(datos['email'], socio_id):
        raise _email_repetido()
    try:
        db.modificar_socio(socio_id, datos)
    except IntegrityError:
        raise _email_repetido()
    return db.obtener_socio(socio_id)
