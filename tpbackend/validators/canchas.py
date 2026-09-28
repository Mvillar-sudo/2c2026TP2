from datetime import datetime, timezone, timedelta
from errors import error_response

zonahoraria_arg = timezone(timedelta(hours=-3))

"""
Pre: Recibe el cuerpo JSON en POST /canchas como 'data', que puede o no ser del tipo None. 
Post: Devuelve (error_response, None) si falla alguna regla, 
o (None, datos_normalizados) si cumple el esquema.
"""


def validar_creacion(data):
    if not data or not isinstance(data, dict):
        return error_response(400, "CUERPO_INVALIDO", "Cuerpo invalido",
                              "El cuerpo debe ser un objeto JSON valido."), None

    permitidos = {'nombre', 'id_deporte', 'precio_hora', 'techada', 'activa'}
    if not set(data.keys()).issubset(permitidos):
        return error_response(400, "PARAMETRO_INVALIDO", "Campos no permitidos", "Campo invalido."), None

    if not all(k in data for k in ('nombre', 'id_deporte', 'precio_hora')):
        return error_response(400, "CAMPOS_FALTANTES", "Campos obligatorios ausentes",
                              "Faltan 'nombre', 'id_deporte' o 'precio_hora'."), None

    nombre = str(data['nombre']).strip()
    if not nombre:
        return error_response(400, "VALOR_INVALIDO", "Nombre invalido", "El nombre no puede quedar vacio."), None

    if not isinstance(data['precio_hora'], int) or data['precio_hora'] <= 0:
        return error_response(400, "VALOR_INVALIDO", "Precio invalido",
                              "precio_hora debe ser un entero positivo."), None

    if not isinstance(data['id_deporte'], int) or data['id_deporte'] <= 0:
        return error_response(400, "VALOR_INVALIDO", "id_deporte invalido",
                              "id_deporte debe ser un entero positivo."), None

    if 'techada' in data and not isinstance(data['techada'], bool):
        return error_response(400, "VALOR_INVALIDO", "Techada invalida",
                              "techada debe ser un booleano (true/false)."), None

    if 'activa' in data and not isinstance(data['activa'], bool):
        return error_response(400, "VALOR_INVALIDO", "Activa invalida",
                              "activa debe ser un booleano (true/false)."), None

    return None, {
        "nombre": nombre,
        "id_deporte": data['id_deporte'],
        "precio_hora": data['precio_hora'],
        "techada": bool(data.get('techada', False)),
        "activa": bool(data.get('activa', True))
    }


"""
Pre: Recibe el cuerpo JSON en PATCH /canchas<id> como 'data', que puede o no ser del tipo None.
Post: Devuelve (error_response, None) si hay campos invalidos, 
o (None, dict_updates) con las columnas a modificar si los campos son editables.
"""


def validar_modificacion(data):
    if not data or not isinstance(data, dict):
        return error_response(400, "CUERPO_VACIO", "Cuerpo invalido", "Cuerpo JSON vacio o invalido."), None

    campos_editables = ['nombre', 'precio_hora', 'techada', 'activa']
    for key in data.keys():
        if key not in campos_editables:
            return error_response(400, "CAMPO_INVALIDO", "Campo no editable",
                                  f"Campo no editable o invalido: {key}"), None

    updates = {}
    if 'nombre' in data:
        nom = str(data['nombre']).strip()
        if not nom:
            return error_response(400, "VALOR_INVALIDO", "Nombre invalido", "El nombre no puede quedar vacio."), None
        updates['nombre_cancha'] = nom

    if 'precio_hora' in data:
        if not isinstance(data['precio_hora'], int) or data['precio_hora'] <= 0:
            return error_response(400, "VALOR_INVALIDO", "Precio invalido",
                                  "precio_hora debe ser un entero positivo."), None
        updates['precio_hora'] = data['precio_hora']

    if 'techada' in data:
        if not isinstance(data['techada'], bool):
            return error_response(400, "VALOR_INVALIDO", "Techada invalida",
                                  "techada debe ser un booleano (true/false)."), None
        updates['techada'] = data['techada']

    if 'activa' in data:
        if not isinstance(data['activa'], bool):
            return error_response(400, "VALOR_INVALIDO", "Activa invalida",
                                  "activa debe ser un booleano (true/false)."), None
        updates['cancha_activa'] = data['activa']

    if not updates:
        return error_response(400, "SIN_CAMBIOS", "Peticion sin cambios", "No se han hecho modificaciones."), None

    return None, updates


"""
Pre: 'hora_inicio' y 'hora_fin' deben ser instancias válidas de datetime con zona horaria GMT-3.
Post: Devuelve (True, "") si cumplen las restricciones horarias. 
En el caso contrario devuelve (False, mensaje).
"""


def validar_reglas_horarias(hora_inicio, hora_fin):
    ahora = datetime.now(zonahoraria_arg)
    if hora_inicio <= ahora:
        return False, "El horario de inicio no puede ser anterior al horario actual."

    if hora_inicio.minute != 0 or hora_inicio.second != 0 or \
            hora_fin.minute != 0 or hora_fin.second != 0:
        return False, "Los horarios deben comenzar y terminar en punto."

    if hora_inicio.date() != hora_fin.date():
        return False, "El rango no puede superar las 0:00."

    duracion = (hora_fin - hora_inicio).total_seconds() / 3600
    if not (1 <= duracion <= 3) or not duracion.is_integer():
        return False, "La duracion debe ser entre 1 y 3 horas enteras."

    if hora_inicio.hour < 8 or hora_fin.hour > 23 or (
            hora_fin.hour == 23 and (hora_fin.minute > 0 or hora_fin.second > 0)):
        return False, "El club se encuentra abierto de 08:00 a 23:00."

    return True, ""


"""
Pre: 'args' es el MultiDict de query params de un GET /canchas (request.args).
Post: Devuelve (error_response, None) si algún parámetro es desconocido o
inválido, o (None, dict) con los filtros ya normalizados, la lista de
filtros aplicados (para armar los links HATEOAS) y la paginación validada.
"""


def validar_filtros_listado(args):
    permitidos = {'id_deporte', 'nombre', 'techada', 'activa', '_limit', '_offset'}
    for param in args.keys():
        if param not in permitidos:
            return error_response(400, "PARAMETRO_INVALIDO", "Parametro desconocido",
                                  f"El parametro '{param}' no esta permitido"), None

    filtros = {}
    filtros_url = []

    if args.get('id_deporte') is not None:
        try:
            id_dep = int(args.get('id_deporte'))
        except ValueError:
            return error_response(400, "VALOR_INVALIDO", "id_deporte invalido",
                                  "id_deporte debe ser un numero entero"), None
        if id_dep <= 0:
            return error_response(400, "VALOR_INVALIDO", "id_deporte invalido",
                                  "id_deporte debe ser un entero positivo"), None
        filtros['id_deporte'] = id_dep
        filtros_url.append(f"id_deporte={id_dep}")

    if args.get('nombre') is not None and args.get('nombre') != "":
        nombre = args.get('nombre')
        filtros['nombre'] = nombre
        filtros_url.append(f"nombre={nombre}")

    if args.get('techada') is not None:
        val = args.get('techada').lower()
        if val not in ('true', 'false'):
            return error_response(400, "VALOR_INVALIDO", "techada invalida",
                                  "El filtro techada debe ser true o false"), None
        filtros['techada'] = (val == 'true')
        filtros_url.append(f"techada={val}")

    if args.get('activa') is not None:
        val = args.get('activa').lower()
        if val not in ('true', 'false'):
            return error_response(400, "VALOR_INVALIDO", "activa invalida",
                                  "El filtro activa debe ser true o false"), None
        filtros['activa'] = (val == 'true')
        filtros_url.append(f"activa={val}")

    try:
        limit = int(args.get('_limit', 10))
        offset = int(args.get('_offset', 0))
    except ValueError:
        return error_response(400, "PAGINACION_INVALIDA", "Parametros de paginacion invalidos",
                              "_limit y _offset deben ser enteros"), None

    if limit < 1 or limit > 100 or offset < 0:
        return error_response(400, "PAGINACION_INVALIDA", "Rango de paginacion invalido",
                              "_limit debe estar entre 1 y 100, y _offset mayor o igual a 0"), None

    return None, {
        "filtros": filtros,
        "filtros_url": filtros_url,
        "limit": limit,
        "offset": offset,
    }
