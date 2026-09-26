from re import fullmatch


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
