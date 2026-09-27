from re import fullmatch

from flask import jsonify, request


def construir_error_api(code: str, message: str, description: str, level: str = 'error') -> dict:
    return {
        'errors': [{
            'code': code,
            'message': message,
            'description': description,
            'level': level,
        }]
    }


def validar_id(raw_id) -> int:
    try:
        value = int(raw_id)
    except (TypeError, ValueError):
        raise ValueError(construir_error_api(
            'invalid.id', 
            'Identificador invalido', 
            'El id debe ser un entero positivo'
        ))
    if value < 1:
        raise ValueError(construir_error_api(
            'invalid.id', 
            'Identificador invalido', 
            'El id debe ser un entero positivo'
        ))
    return value


def validar_bool(raw_value, name: str) -> bool:
    if isinstance(raw_value, bool):
        return raw_value
    if isinstance(raw_value, str) and raw_value.lower() in ('true', 'false'):
        return raw_value.lower() == 'true'
    raise ValueError(construir_error_api(
        'invalid.parameter', 
        f"Parametro '{name}' invalido",
        f"El parametro '{name}' debe ser true o false",
    ))


def validar_paginacion(raw_limit, raw_offset) -> tuple[int, int]:
    try:
        if raw_limit is not None:
            limit = int(raw_limit)
        else:
            limit = 10
        if raw_offset is not None:
            offset = int(raw_offset)
        else:
            offset = 0
    except (TypeError, ValueError):
        raise ValueError(construir_error_api(
            'invalid.pagination', 
            'Paginacion invalida',
            '_limit y _offset deben ser enteros',
        ))
    if not 1 <= limit <= 100 or offset < 0:
        raise ValueError(construir_error_api(
            'invalid.pagination', 
            'Paginacion invalida',
            '_limit debe estar entre 1 y 100 y _offset no puede ser negativo',
        ))
    return limit, offset


def validar_email(email) -> str:
    if not isinstance(email, str) or not fullmatch(r'[^@\s]+@[^@\s]+\.[^@\s]+', email.strip()):
        raise ValueError(construir_error_api(
            'invalid.email', 
            'Email invalido', 
            'El email debe tener un formato valido',
        ))
    return email.strip().lower()


# --- Lo que sigue son PROPUESTAS DE AGREGADO a este archivo, para no  ---
# --- duplicar el manejo de errores ni el armado de links HATEOAS que  ---
# --- hoy cada blueprint (canchas, socios, reservas) reimplementa por  ---
# --- su cuenta con pequeñas diferencias. Charlarlo con el grupo antes ---
# --- de mergear, por si prefieren otro nombre o ubicación.            ---

def manejar_error(error: ValueError, default_status: int = 400):
    """
    Convierte un ValueError lanzado por un validador o un service
    (con un diccionario de construir_error_api como primer argumento,
    y opcionalmente un status HTTP como segundo argumento) en la
    respuesta Flask correspondiente.

    Uso típico en una ruta:
        try:
            datos = validar_algo(request.get_json(silent=True))
        except ValueError as error:
            return manejar_error(error)
    """
    mensaje = error.args[0]
    status = error.args[1] if len(error.args) > 1 else default_status
    return jsonify(mensaje), status


def construir_links(limit: int, offset: int, total: int, extra_query: str = "") -> dict:
    """
    Arma los links HATEOAS (_first, _prev, _next, _last) para un listado
    paginado, usando la URL actual del request (sin query string).

    'extra_query' es un string ya armado tipo "clave1=valor1&clave2=valor2",
    con los filtros que se quieren conservar al navegar entre páginas.
    """
    extra = f"&{extra_query}" if extra_query else ""
    links = {'_first': {'href': request.base_url + f'?_limit={limit}&_offset=0{extra}'}}
    if offset > 0:
        previous = max(0, offset - limit)
        links['_prev'] = {'href': request.base_url + f'?_limit={limit}&_offset={previous}{extra}'}
    if offset + limit < total:
        links['_next'] = {'href': request.base_url + f'?_limit={limit}&_offset={offset + limit}{extra}'}
    last = max(0, ((total - 1) // limit) * limit) if total else 0
    links['_last'] = {'href': request.base_url + f'?_limit={limit}&_offset={last}{extra}'}
    return links
