from ..constants import ERROR_INVALID_BODY
from ..utils import construir_error_api, validar_bool, validar_email


def _validar_nombre(value):
    if not isinstance(value, str) or not value.strip():
        raise ValueError(construir_error_api(
            'required.nombre', 'Nombre requerido', 'El nombre no puede estar vacio',
        ))
    return value.strip()


def validar_filtros(args):
    nombre = args.get('nombre_socio')
    activo = args.get('socio_activo')
    if nombre is not None:
        nombre = nombre.strip()
    if activo is not None:
        activo = validar_bool(activo, 'socio_activo')
    return nombre, activo


def validar_socio_create(body):
    if not isinstance(body, dict):
        raise ValueError(construir_error_api(
            ERROR_INVALID_BODY, 'Cuerpo invalido', 'El cuerpo debe ser un objeto JSON',
        ))
    return {
        'nombre_socio': _validar_nombre(body.get('nombre_socio')),
        'email': validar_email(body.get('email')),
    }


def validar_socio_update(body):
    if not isinstance(body, dict) or not body:
        raise ValueError(construir_error_api(
            ERROR_INVALID_BODY, 'Cuerpo invalido', 'Debe indicar al menos un campo para actualizar',
        ))
    allowed = {'nombre_socio', 'email', 'socio_activo'}
    unknown = set(body) - allowed
    if unknown:
        raise ValueError(construir_error_api(
            ERROR_INVALID_BODY, 'Cuerpo invalido', f"Campos no permitidos: {', '.join(sorted(unknown))}",
        ))
    data = {}
    if 'nombre_socio' in body:
        data['nombre_socio'] = _validar_nombre(body['nombre_socio'])
    if 'email' in body:
        data['email'] = validar_email(body['email'])
    if 'socio_activo' in body:
        data['socio_activo'] = validar_bool(body['socio_activo'], 'socio_activo')
    return data
