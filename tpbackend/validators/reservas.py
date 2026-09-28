
import re
from datetime import datetime

from tpbackend.utils import construir_error_api, validar_id, validar_paginacion
from tpbackend.validators.canchas import validar_reglas_horarias

ESTADOS_VALIDOS = ("confirmada", "cancelada", "finalizada")
PATRON_FECHA = re.compile(r"^\d{4}-\d{2}-\d{2}$")
PATRON_FECHA_HORA = re.compile(
    r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{6}-03:00$"
)



def validar_filtros_listado(args):
    permitidos = {"id_cancha", "id_socio", "estado", "fecha_desde", "fecha_hasta",
                  "_limit", "_offset"}
    for param in args.keys():
        if param not in permitidos:
            raise ValueError(construir_error_api(
                'invalid.parameter', 'Parametro desconocido',
                f"El parametro '{param}' no esta permitido",
            ))

    filtros = {}

    id_cancha = args.get("id_cancha")
    if id_cancha is not None:
        filtros["id_cancha"] = validar_id(id_cancha)

    id_socio = args.get("id_socio")
    if id_socio is not None:
        filtros["id_socio"] = validar_id(id_socio)

    estado = args.get("estado")
    if estado is not None:
        if estado not in ESTADOS_VALIDOS:
            raise ValueError(construir_error_api(
                'invalid.parameter', 'Estado invalido',
                'estado debe ser confirmada, cancelada o finalizada',
            ))
        filtros["estado"] = estado

    fecha_desde = args.get("fecha_desde")
    if fecha_desde is not None:
        if not PATRON_FECHA.match(fecha_desde):
            raise ValueError(construir_error_api(
                'invalid.parameter', 'fecha_desde invalida',
                'fecha_desde debe tener formato YYYY-MM-DD',
            ))
        filtros["fecha_desde"] = fecha_desde

    fecha_hasta = args.get("fecha_hasta")
    if fecha_hasta is not None:
        if not PATRON_FECHA.match(fecha_hasta):
            raise ValueError(construir_error_api(
                'invalid.parameter', 'fecha_hasta invalida',
                'fecha_hasta debe tener formato YYYY-MM-DD',
            ))
        filtros["fecha_hasta"] = fecha_hasta

    if fecha_desde is not None and fecha_hasta is not None and fecha_desde > fecha_hasta:
        raise ValueError(construir_error_api(
            'invalid.parameter', 'Rango de fechas invalido',
            'fecha_desde debe ser menor o igual a fecha_hasta',
        ))

    limit, offset = validar_paginacion(args.get('_limit'), args.get('_offset'))
    filtros["_limit"] = limit
    filtros["_offset"] = offset

    return filtros



def validar_creacion(data):
    if not isinstance(data, dict):
        raise ValueError(construir_error_api(
            'invalid.body', 'Cuerpo invalido', 'El cuerpo debe ser un objeto JSON valido',
        ))

    esperados = {"id_socio", "id_cancha", "fecha_hora_inicio", "fecha_hora_fin"}
    if set(data.keys()) != esperados:
        raise ValueError(construir_error_api(
            'invalid.body', 'Campos invalidos',
            f"El cuerpo debe tener exactamente los campos: {sorted(esperados)}",
        ))

    id_socio = validar_id(data["id_socio"])
    id_cancha = validar_id(data["id_cancha"])

    fecha_inicio_str = data["fecha_hora_inicio"]
    fecha_fin_str = data["fecha_hora_fin"]

    if not isinstance(fecha_inicio_str, str) or not PATRON_FECHA_HORA.match(fecha_inicio_str):
        raise ValueError(construir_error_api(
            'invalid.body', 'fecha_hora_inicio invalida',
            'Formato esperado: YYYY-MM-DDTHH:MM:SS.ffffff-03:00',
        ))
    if not isinstance(fecha_fin_str, str) or not PATRON_FECHA_HORA.match(fecha_fin_str):
        raise ValueError(construir_error_api(
            'invalid.body', 'fecha_hora_fin invalida',
            'Formato esperado: YYYY-MM-DDTHH:MM:SS.ffffff-03:00',
        ))

    try:
        inicio = datetime.fromisoformat(fecha_inicio_str)
        fin = datetime.fromisoformat(fecha_fin_str)
    except ValueError:
        raise ValueError(construir_error_api(
            'invalid.body', 'Fecha invalida',
            'No se pudo interpretar alguna de las fechas recibidas',
        ))

    if inicio >= fin:
        raise ValueError(construir_error_api(
            'invalid.body', 'Intervalo invalido',
            'fecha_hora_inicio debe ser anterior a fecha_hora_fin',
        ))

    valido, mensaje = validar_reglas_horarias(inicio, fin)
    if not valido:
        raise ValueError(construir_error_api('invalid.body', 'Horario invalido', mensaje))

    return {
        "id_socio": id_socio,
        "id_cancha": id_cancha,
        "fecha_hora_inicio": inicio,
        "fecha_hora_fin": fin,
    }


def validar_cambio_estado(data):
    if not isinstance(data, dict):
        raise ValueError(construir_error_api(
            'invalid.body', 'Cuerpo invalido', 'El cuerpo debe ser un objeto JSON valido',
        ))
    if set(data.keys()) != {"estado"}:
        raise ValueError(construir_error_api(
            'invalid.body', 'Campos invalidos',
            "El cuerpo debe tener unicamente el campo 'estado'",
        ))
    estado = data["estado"]
    if not isinstance(estado, str) or estado not in ESTADOS_VALIDOS:
        raise ValueError(construir_error_api(
            'invalid.state', 'Estado invalido',
            "estado debe ser 'confirmada', 'cancelada' o 'finalizada'",
        ))
    return estado